import os
import subprocess
import tempfile
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- Environment variables ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.environ.get("TELEGRAM_GROUP_ID")

RCLONE_USER = os.environ.get("RCLONE_USER", "admin")
RCLONE_PASS = os.environ.get("RCLONE_PASS", "changeme")
APP_PORT = int(os.environ.get("PORT", "8080"))
RCLONE_CONFIG_PATH = "/tmp/rclone.conf"

# rclone destination (change remote if needed)
UPLOAD_REMOTE = "gdrive:telegram_uploads"


# --- Start rclone WebUI ---
def start_rclone():
    print(f"✅ Starting rclone WebUI on port {APP_PORT} ...")

    rclone_conf = os.environ.get("RCLONE_CONFIG")
    if rclone_conf:
        with open(RCLONE_CONFIG_PATH, "w") as f:
            f.write(rclone_conf)
        print("📄 rclone config written to /tmp/rclone.conf")
    else:
        print("⚠️ No RCLONE_CONFIG provided, uploads may fail")

    cmd = [
        "./bin/rclone",
        "rcd",
        "--rc-web-gui",
        "--rc-addr", f":{APP_PORT}",
        "--rc-user", RCLONE_USER,
        "--rc-pass", RCLONE_PASS,
        "--disable-http2",
        "--config", RCLONE_CONFIG_PATH,
    ]
    subprocess.Popen(cmd)


# --- Telegram bot handlers ---
async def start(update, context):
    await update.message.reply_text(
        "Hello! Bot is running 🚀\nSend me a file and I’ll upload it to Google Drive."
    )

async def echo(update, context):
    await update.message.reply_text(update.message.text)

async def handle_file(update, context):
    file = None
    if update.message.document:
        file = update.message.document
    elif update.message.photo:
        file = update.message.photo[-1]  # highest resolution
    elif update.message.video:
        file = update.message.video

    if not file:
        return

    file_id = file.file_id
    file_name = getattr(file, "file_name", f"{file_id}.bin")

    tg_file = await context.bot.get_file(file_id)
    tmp_path = os.path.join(tempfile.gettempdir(), file_name)
    await tg_file.download_to_drive(tmp_path)

    try:
        cmd = [
            "./bin/rclone",
            "copy",
            tmp_path,
            UPLOAD_REMOTE,
            "--config", RCLONE_CONFIG_PATH,
            "-v",
        ]
        subprocess.check_call(cmd)
        await update.message.reply_text(f"✅ Uploaded {file_name} to {UPLOAD_REMOTE}")
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ Upload failed: {e}")


# --- Entry point ---
def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN is missing!")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO,
        handle_file
    ))

    # Render provides RENDER_EXTERNAL_URL
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        raise RuntimeError("❌ RENDER_EXTERNAL_URL is missing!")

    webhook_url = render_url.rstrip("/") + f"/{TELEGRAM_BOT_TOKEN}"

    print(f"🤖 Setting webhook to {webhook_url} ...")
    app.run_webhook(
        listen="0.0.0.0",
        port=APP_PORT,
        webhook_url=webhook_url
    )


if __name__ == "__main__":
    start_rclone()
    run_bot()
