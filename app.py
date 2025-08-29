import os
import subprocess
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- Environment variables ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.environ.get("TELEGRAM_GROUP_ID")  # e.g. "-1001234567890"

RCLONE_USER = os.environ.get("RCLONE_USER", "admin")
RCLONE_PASS = os.environ.get("RCLONE_PASS", "changeme")
RCLONE_PORT = int(os.environ.get("RCLONE_PORT", "10000"))  # WebUI port
APP_PORT = int(os.environ.get("PORT", "8080"))  # Render expects something on PORT


# --- Start rclone WebUI ---
def start_rclone():
    print(f"✅ Starting rclone WebUI on port {RCLONE_PORT} ...")
    cmd = [
        "./bin/rclone",
        "rcd",
        "--rc-web-gui",
        "--rc-addr", f":{RCLONE_PORT}",
        "--rc-user", RCLONE_USER,
        "--rc-pass", RCLONE_PASS,
    ]
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
    app.run_polling()  # ✅ handles asyncio internally (no manual loop)


# --- Entry point ---
if __name__ == "__main__":
    start_rclone()
    run_bot()
