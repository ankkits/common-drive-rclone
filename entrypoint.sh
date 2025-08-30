#!/bin/bash
set -e

# Make config dir
mkdir -p /root/.config/rclone

# Write the RCLONE_CONFIG content from env var into config file
if [ -n "$RCLONE_CONFIG" ]; then
  echo "$RCLONE_CONFIG" > /root/.config/rclone/rclone.conf
fi

# Run rclone in RC + WebUI mode with creds from env vars
exec rclone rcd \
  --rc-web-gui \
  --rc-addr :10000 \
  --rc-user "${RCLONE_USER:-admin}" \
  --rc-pass "${RCLONE_PASS:-password}"
