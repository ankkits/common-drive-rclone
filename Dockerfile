# Use Alpine Linux for smaller image size
FROM alpine:latest

# Install rclone and dependencies
RUN apk add --no-cache \
    curl \
    unzip \
    ca-certificates \
    && curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip \
    && unzip rclone-current-linux-amd64.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin/ \
    && chmod +x /usr/bin/rclone \
    && cd .. \
    && rm -rf rclone-* \
    && rm rclone-current-linux-amd64.zip

# Create rclone config directory
RUN mkdir -p /root/.config/rclone

# Create startup script
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'echo "$RCLONE_CONFIG" > /root/.config/rclone/rclone.conf' >> /start.sh && \
    echo 'exec rclone rcd --rc-web-gui --rc-addr 0.0.0.0:10000 --rc-user "$RC_USER" --rc-pass "$RC_PASS" --rc-web-gui-update --rc-web-gui-no-open-browser' >> /start.sh && \
    chmod +x /start.sh

# Expose the port that Render will use
EXPOSE 10000

# Start rclone with environment variables
CMD ["/start.sh"]