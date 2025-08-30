# Use Alpine for small image
FROM rclone/rclone:latest

# Install bash and coreutils for decoding
RUN apk add --no-cache bash coreutils

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose Render port (Render sets $PORT automatically)
EXPOSE 10000

ENTRYPOINT ["/entrypoint.sh"]
