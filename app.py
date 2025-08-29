import os
import subprocess
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- Environment variables ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.environ.get("TELEGRAM_GROUP_ID")  # e.g. "-1001234567890"

RCLONE_USER = os.environ.get("RCLONE_USER", "admin")
RCLONE_PASS = os.environ.get("RCLONE_PASS", "changeme")
RCLONE_PORT = int(os.environ.get("RCLONE_PORT", "10000"))  # WebUI port
APP_PORT = int(os.environ.get("PORT", RCLONE_PORT))        # Render expects this exposed


# --- Start rclone WebUI ---
def start_rclone():
    print(f"✅ Starting rclone WebUI on port {APP_PORT} ...")
    cmd = [
        "./bin/rclone",
        "rcd",
        "--rc-web-gui",
        "--rc-addr", f":{APP_PORT}",
        "--rc-user", RCLONE_USER,
        "--rc-pass", RCLONE_PASS,
    ]
    subprocess.Popen(cmd)  # run in background


# --- Flask app for webhook ---
flask_app = Flask(__name__)

telegram_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Handlers
async def start(update, context):
    await update.message.reply_text("Hello! Bot is up and running 🚀")

async def echo(update, context):
    await update.message.reply_text(update.message.text)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# --- Flask routes ---
@flask_app.route("/")
def index():
    return "✅ Rclone WebUI + Telegram Bot running"

@flask_app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok", 200


async def setup_webhook():
    app_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not app_url:
        print("⚠️ No RENDER_EXTERNAL_URL set, webhook cannot be configured")
        return
    webhook_url = f"{app_url}/webhook"
    print(f"🔗 Setting Telegram webhook: {webhook_url}")
    await telegram_app.bot.set_webhook(webhook_url)


# --- Entry point ---
if __name__ == "__main__":
    # 1. Start rclone WebUI
    start_rclone()

    # 2. Setup Telegram webhook
    asyncio.run(setup_webhook())

    # 3. Run Flask (keeps everything alive)
    flask_app.run(host="0.0.0.0", port=APP_PORT)
