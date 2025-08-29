import os
import subprocess
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- Environment variables ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.environ.get("TELEGRAM_GROUP_ID")  # e.g. "-1001234567890"

RCLONE_USER = os.environ.get("RCLONE_USER", "admin")
RCLONE_PASS = os.environ.get("RCLONE_PASS", "changeme")
APP_PORT = int(os.environ.get("PORT", "8080"))  # Render gives this automatically


# --- Start rclone WebUI ---
def start_rclone():
    print(f"✅ Starting rclone WebUI on port {APP_PORT} ...")

    # Write rclone config from env var to temp file
    rclone_conf = os.environ.get("RCLONE_CONFIG") or os.environ.get("rclone_dest")
    config_path = "/tmp/rclone.conf"
    if rclone_conf:
        with open(config_path, "w") as f:
            f.write(rclone_conf)
        print("📄 rclone config written to /tmp/rclone.conf")
    else:
        print("⚠️ No RCLONE_CONFIG/rclone_dest env var found, starting without remotes")
        config_path = None

    cmd = [
        "./bin/rclone",
        "rcd",                     # run as daemon
        "--rc-web-gui",            # enable Web UI
        "--rc-addr", f":{APP_PORT}",
        "--rc-user", RCLONE_USER,
        "--rc-pass", RCLONE_PASS,
    ]
    if config_path:
        cmd += ["--config", config_path]

    subprocess.Popen(cmd)  # run in background


# --- Telegram bot handlers ---
async def start(update, context):
    await update.message.reply_text("Hello! Bot is up and running 🚀")

async def echo(update, context):
    await update.message.reply_text(update.message.text)


def run_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN is missing in environment variables!")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Telegram bot started...")
    app.run_polling()


# --- Entry point ---
if __name__ == "__main__":
    start_rclone()
    run_bot()
