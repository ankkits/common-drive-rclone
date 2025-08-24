import os
import subprocess
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- Environment Variables ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ALLOWED_CHAT_ID = os.environ.get("TELEGRAM_ALLOWED_CHAT_ID")
RCLONE_RC_USER = os.environ.get("RCLONE_RC_USER", "admin")
RCLONE_RC_PASS = os.environ.get("RCLONE_RC_PASS", "changeme")
RCLONE_DEST = os.environ.get("RCLONE_DEST", "protondrive1:/telegram")
PORT = os.environ.get("PORT", "8080")

# --- Start Rclone WebUI ---
def start_rclone():
    cmd = [
        "./bin/rclone", "rcd",
        "--rc-web-gui",
        f"--rc-user={RCLONE_RC_USER}",
        f"--rc-pass={RCLONE_RC_PASS}",
        "--rc-serve",
        f"--rc-addr=0.0.0.0:{PORT}"
    ]
    return subprocess.Popen(cmd)

# --- Telegram Bot Handlers ---
async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(ALLOWED_CHAT_ID):
        return

    file = None
    if update.message.document:
        file = update.message.document
    elif update.message.photo:
        file = update.message.photo[-1]
    elif update.message.video:
        file = update.message.video

    if not file:
        return

    file_path = f"/tmp/{file.file_unique_id}"
    await file.get_file().download_to_drive(file_path)

    # Upload to rclone remote
    cmd = ["./bin/rclone", "move", file_path, RCLONE_DEST]
    subprocess.run(cmd)

    await update.message.reply_text("✅ File uploaded to cloud storage")

async def run_bot():
    if not TELEGRAM_TOKEN:
        print("No TELEGRAM_TOKEN provided, bot disabled")
        return
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, save_file))
    await app.run_polling()

# --- Main ---
if __name__ == "__main__":
    # Start Rclone WebUI
    rclone_proc = start_rclone()
    print(f"✅ Rclone WebUI running on port {PORT}")

    # Start Telegram Bot
    try:
        asyncio.run(run_bot())
    finally:
        rclone_proc.terminate()
