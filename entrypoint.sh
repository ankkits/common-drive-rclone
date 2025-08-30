#!/bin/sh
set -e

# Ensure PORT is set by Render, fallback to 10000
PORT=${PORT:-10000}

# Decode RCLONE_CONFIG if provided
if [ -n "$RCLONE_CONFIG" ]; then
  echo "$RCLONE_CONFIG" | base64 -d > /app/rclone.conf
  export RCLONE_CONFIG=/app/rclone.conf
  echo "[INFO] Rclone config written to /app/rclone.conf"
else
  echo "[WARN] No RCLONE_CONFIG provided. Running without remotes."
fi

# Start rclone remote control with Web GUI
exec rclone rcd \
  --rc-web-gui \
  --rc-addr=0.0.0.0:$PORT \
  --rc-user=$RCLONE_USER \
  --rc-pass=$RCLONE_PASS
