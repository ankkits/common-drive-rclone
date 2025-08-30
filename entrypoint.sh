#!/bin/bash
set -e

# Ensure PORT from Render (default 10000)
PORT=${PORT:-10000}

# If RCLONE_CONFIG exists in env, write it to /app/rclone.conf
if [ -n "$RCLONE_CONFIG" ]; then
  echo "$RCLONE_CONFIG" | base64 -d > /app/rclone.conf
  export RCLONE_CONFIG=/app/rclone.conf
fi

# Start rclone WebUI
exec rclone rcd \
  --rc-web-gui \
  --rc-web-gui-no-open-browser \
  --rc-addr=0.0.0.0:$PORT \
  --rc-user=$RCLONE_USER \
  --rc-pass=$RCLONE_PASS
