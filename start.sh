#!/usr/bin/env bash
set -e

# Ensure bin exists
mkdir -p bin

mkdir -p ~/.config/rclone
echo "$RCLONE_CONFIG" > ~/.config/rclone/rclone.conf

# Download rclone binary for Linux
curl -L https://downloads.rclone.org/rclone-current-linux-amd64.zip -o /tmp/rclone.zip

# Extract just the rclone binary
unzip -j /tmp/rclone.zip "rclone-*-linux-amd64/rclone" -d bin

# Make it executable
chmod +x bin/rclone

# Start the Python app
python app.py


