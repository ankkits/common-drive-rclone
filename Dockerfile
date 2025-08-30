FROM rclone/rclone:latest

# Small utilities
RUN apk add --no-cache bash coreutils && mkdir -p /app

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Render will inject $PORT; EXPOSE is informational
EXPOSE 10000

ENTRYPOINT ["/entrypoint.sh"]
