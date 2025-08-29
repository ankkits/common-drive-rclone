#!/usr/bin/env bash
set -e

mkdir -p bin

# Download rclone
if [ ! -f "bin/rclone" ]; then
  echo "⬇️ Downloading rclone..."
  curl -L https://downloads.rclone.org/rclone-current-linux-amd64.zip -o /tmp/rclone.zip
  unzip -j /tmp/rclone.zip "rclone-*-linux-amd64/rclone" -d bin
  chmod +x bin/rclone
fi

# Pre-download WebUI assets
mkdir -p ~/.cache/rclone/webgui
curl -L https://github.com/rclone/rclone-webui-react/releases/latest/download/current.zip -o /tmp/webui.zip
unzip -o /tmp/webui.zip -d ~/.cache/rclone/webgui

# Start Python app
echo "🚀 Starting app..."
python app.py
