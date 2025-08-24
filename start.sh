#!/usr/bin/env bash
set -e

# Ensure bin exists
mkdir -p bin

# Download rclone binary for Linux
curl -L https://downloads.rclone.org/rclone-current-linux-amd64.zip -o /tmp/rclone.zip

# Extract just the rclone binary
unzip -j /tmp/rclone.zip "rclone-*-linux-amd64/rclone" -d bin

# Make it executable
chmod +x bin/rclone

# Write the rclone.conf from env var to file (if provided)
if [ -n "$RCLONE_DEST" ]; then
  mkdir -p ~/.config/rclone
  echo "$RCLONE_DEST" > ~/.config/rclone/rclone.conf
fi

# Start the python app
python app.py --mode webui
