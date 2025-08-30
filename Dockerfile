# Use Alpine Linux for smaller image size
FROM alpine:latest

# Install dependencies
RUN apk add --no-cache curl unzip ca-certificates

# Install rclone with better error handling
RUN curl -L https://downloads.rclone.org/rclone-current-linux-amd64.zip -o rclone.zip \
    && unzip rclone.zip \
    && find . -name "rclone" -type f -executable | head -1 | xargs -I {} cp {} /usr/bin/rclone \
    && chmod +x /usr/bin/rclone \
    && rm -rf rclone* \
    && rclone version

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