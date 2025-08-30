# Use lightweight rclone base image
FROM rclone/rclone:latest

# Install bash (needed for entrypoint script)
RUN apk add --no-cache bash

# Create app directory
WORKDIR /app

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose Render PORT
EXPOSE 10000

CMD ["/app/entrypoint.sh"]
