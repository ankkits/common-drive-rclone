import os
import subprocess
import tempfile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# --- Environment variables ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.environ.get("TELEGRAM_GROUP_ID")

RCLONE_USER = os.environ.get("RCLONE_USER", "admin")
RCLONE_PASS = os.environ.get("RCLONE_PASS", "changeme")
APP_PORT = int(os.environ.get("PORT", "8080"))
RCLONE_CONFIG_PATH = "/tmp/rclone.conf"

UPLOAD_REMOTE = "gdrive:telegram_uploads"   # change if needed


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
def start(update, context):
    update.message.reply_text("Hello! Bot is running 🚀\nSend me a file and I’ll upload it to Drive.")

def echo(update, context):
    update.message.reply_text(update.message.text)

def handle_file(update, context):
    file = None
    if update.message.document:
        file = update.message.document
    elif update.message.photo:
        file = update.message.photo[-1]
    elif update.message.video:
        file = update.message.video

    if not file:
        return

    file_id = file.file_id
    file_name = getattr(file, "file_name", f"{file_id}.bin")

    tg_file = context.bot.get_file(file_id)
    tmp_path = os.path.join(tempfile.gettempdir(), file_name)
    tg_file.download(tmp_path)

    try:
        cmd = [
            "./bin/rclone",
            "copy",
            tmp_path,
            UPLOAD_REMOTE,
            "--config", RCLONE_CONFIG_PATH,
            "-v"
        ]
        subprocess.check_call(cmd)
        update.message.reply_text(f"✅ Uploaded {file_name} to {UPLOAD_REMOTE}")
    except subprocess.CalledProcessError as e:
        update.message.reply_text(f"❌ Upload failed: {e}")


# --- Entry point ---
def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN is missing!")
        return

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    dp.add_handler(MessageHandler(Filters.document | Filters.photo | Filters.video, handle_file))

    print("🤖 Bot is starting with polling ...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    start_rclone()
    run_bot()
