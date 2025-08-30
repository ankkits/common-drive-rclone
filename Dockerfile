# Start from Alpine
FROM alpine:3.19

# Install bash, curl, unzip, ca-certificates
RUN apk add --no-cache bash curl unzip ca-certificates

# Install rclone manually
RUN curl -fsSL https://downloads.rclone.org/rclone-current-linux-amd64.zip -o rclone.zip \
    && unzip rclone.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin/ \
    && cd .. \
    && rm -rf rclone.zip rclone-*-linux-amd64

# Create app directory
WORKDIR /app

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose default port
EXPOSE 10000

# Run our script directly
ENTRYPOINT ["/app/entrypoint.sh"]
