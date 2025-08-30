FROM alpine:3.20

# Install tools
RUN apk add --no-cache curl unzip bash

# Install rclone
RUN curl https://rclone.org/install.sh | bash

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose RC / Web UI port
EXPOSE 10000

# Run entrypoint script
CMD ["/entrypoint.sh"]
