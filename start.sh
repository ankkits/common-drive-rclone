#!/usr/bin/env bash
set -e

# Ensure bin exists
mkdir -p bin

# Download rclone binary (only if not already downloaded)
if [ ! -f "bin/rclone" ]; then
  echo "⬇️ Downloading rclone..."
  curl -L https://downloads.rclone.org/rclone-current-linux-amd64.zip -o /tmp/rclone.zip
  unzip -j /tmp/rclone.zip "rclone-*-linux-amd64/rclone" -d bin
  chmod +x bin/rclone
  rm -f /tmp/rclone.zip
else
  echo "✅ rclone already present."
fi

# Start Python app
echo "🚀 Starting app..."
python app.py
