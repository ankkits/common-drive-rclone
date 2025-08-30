#!/bin/sh
set -e

PORT=${PORT:-10000}

# Prepare a place for config
mkdir -p /app

RCONF_PATH="/app/rclone.conf"
USE_CONFIG_FLAG=""

# If RCLONE_CONFIG is provided, accept base64 or plain text
if [ -n "$RCLONE_CONFIG" ]; then
  if echo "$RCLONE_CONFIG" | base64 -d > "$RCONF_PATH" 2>/dev/null; then
    echo "[INFO] Decoded base64 RCLONE_CONFIG to $RCONF_PATH"
  else
    echo "$RCLONE_CONFIG" > "$RCONF_PATH"
    echo "[INFO] Wrote plain-text RCLONE_CONFIG to $RCONF_PATH"
  fi
  export RCLONE_CONFIG="$RCONF_PATH"
  USE_CONFIG_FLAG="--config=$RCONF_PATH"
else
  echo "[WARN] No RCLONE_CONFIG provided. Running without remotes."
fi

# Start rclone WebUI (the 403 from GitHub API is harmless; WebUI still serves)
exec rclone rcd \
  --rc-web-gui \
  --rc-addr=0.0.0.0:$PORT \
  --rc-user="$RCLONE_USER" \
  --rc-pass="$RCLONE_PASS" \
  $USE_CONFIG_FLAG
