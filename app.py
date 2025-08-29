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
RCLONE_CONF_PATH = "/tmp/rclone.conf"

UPLOAD_REMOTE = "gdrive:telegram_uploads"   # change if needed


# --- Start rclone WebUI ---
def start_rclone():
    print(f"✅ Starting rclone WebUI on port {APP_PORT} ...")

    # Write rclone config from env var
    rclone_conf = os.environ.get("rclone_dest")
    if rclone_conf:
        with open(RCLONE_CONF_PATH, "w") as f:
            f.write(rclone_conf)
        print("📄 rclone config written to /tmp/rclone.conf")
    else:
        print("⚠️ No rclone_dest provided, uploads may fail")

    cmd = [
        "./bin/rclone",
        "rcd",
        "--rc-web-gui",
        "--rc-web-gui-no-open",
        "--rc-addr", f":{APP_PORT}",
        "--rc-user", RCLONE_USER,
        "--rc-pass", RCLONE_PASS,
        "--disable-http2",
        "--config", RCLONE_CONF_PATH,
    ]
    subprocess.Popen(cmd)


# --- Telegram bot handlers ---
async def start(update, context):
    await update.message.reply_text("Hello! Bot is running 🚀\nSend me a file and I’ll upload it to Drive.")

async def echo(update, context):
    await update.message.reply_text(update.message.text)

async def handle_file(update, context):
    file = None
    if update.message.document:
        file = update.message.document
    elif update.message.photo:
        file = update.message.photo[-1]  # highest resolution photo
    elif update.message.video:
        file = update.message.video

    if not file:
        return

    file_id = file.file_id
    file_name = getattr(file, "file_name", f"{file_id}.bin")

    # Download to tmp
    tg_file = await context.bot.get_file(file_id)
    tmp_path = os.path.join(tempfile.gettempdir(), file_name)
    await tg_file.download_to_drive(tmp_path)

    # Upload with rclone
    try:
        cmd = [
            "./bin/rclone",
            "copy",
            tmp_path,
            UPLOAD_REMOTE,
            "--config", RCLONE_CONF_PATH,
            "-v"
        ]
        subprocess.check_call(cmd)
        await update.message.reply_text(f"✅ Uploaded {file_name} to {UPLOAD_REMOTE}")
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ Upload failed: {e}")


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

    print("🤖 Telegram bot started...")
    app.run_polling()


# --- Entry point ---
if __name__ == "__main__":
    start_rclone()
    run_bot()
