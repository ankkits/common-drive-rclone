#!/usr/bin/env bash
set -e

# Ensure bin exists
mkdir -p bin

# Download rclone binary for Linux
if [ ! -f bin/rclone ]; then
  echo "[init] downloading rclone..."
  curl -L https://downloads.rclone.org/rclone-current-linux-amd64.zip -o /tmp/rclone.zip
  unzip -j /tmp/rclone.zip "rclone-*-linux-amd64/rclone" -d bin
  chmod +x bin/rclone
else
  echo "[init] using cached rclone binary"
fi

# Start Python app (both WebUI + Bot)
exec python app.py
