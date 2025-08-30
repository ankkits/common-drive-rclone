#!/bin/bash

# Rclone Render Deployment Script
echo "🚀 Setting up rclone for Render deployment..."

# Create project directory
mkdir -p rclone-render
cd rclone-render

# Copy your existing rclone config
echo "📁 Please copy your rclone.conf file to this directory"
echo "Your rclone config should be at one of these locations:"
echo "  Linux/Mac: ~/.config/rclone/rclone.conf"
echo "  Windows: %APPDATA%/rclone/rclone.conf"
echo ""

# Create Dockerfile
cat > Dockerfile << 'EOF'
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

# Copy your rclone config
COPY rclone.conf /root/.config/rclone/rclone.conf

# Expose the port that Render will use
EXPOSE 10000

# Start rclone with web GUI
CMD ["rclone", "rcd", "--rc-web-gui", "--rc-addr", "0.0.0.0:10000", "--rc-user", "admin", "--rc-pass", "password123", "--rc-web-gui-update", "--rc-web-gui-no-open-browser"]
EOF

# Create render.yaml
cat > render.yaml << 'EOF'
services:
  - type: web
    name: rclone-webui
    env: docker
    dockerfilePath: ./Dockerfile
    region: oregon
    plan: free
    autoDeploy: true
    envVars:
      - key: RCLONE_CONFIG
        value: /root/.config/rclone/rclone.conf
    healthCheckPath: /
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Don't include sensitive config in git
rclone.conf
*.log
.DS_Store
.env
EOF

# Create README
cat > README.md << 'EOF'
# Rclone Web GUI on Render

This deploys rclone with Web GUI to Render's free plan using environment variables for security.

## Setup Steps:

1. Run the deployment script
2. Push to GitHub repository (rclone.conf won't be included - it's in .gitignore)
3. Connect to Render and deploy
4. Set environment variables in Render dashboard

## Environment Variables to Set in Render:

### RCLONE_CONFIG
Copy your entire rclone.conf content. Example:
```
[gdrive]
type = drive
client_id = your_client_id
client_secret = your_client_secret
token = {"access_token":"..."}

[dropbox]
type = dropbox
token = {"access_token":"..."}
```

### RC_USER
Your desired username (e.g., "admin")

### RC_PASS  
Your desired password (choose a strong password)

## Accessing Your Deployment:
Your rclone Web GUI will be available at: `https://your-service-name.onrender.com`

## Security Benefits:
- No sensitive data in git repository
- Config stored securely as environment variables
- Easy to update credentials without redeploying
EOF

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy the content of your rclone.conf file (don't copy the file itself)"
echo "2. Initialize git repository: git init"
echo "3. Add files: git add ."
echo "4. Commit: git commit -m 'Initial rclone setup'"
echo "5. Push to GitHub"
echo "6. Connect GitHub repo to Render"
echo "7. Set these environment variables in Render dashboard:"
echo "   - RCLONE_CONFIG: (paste your entire rclone.conf content)"
echo "   - RC_USER: (your desired username)"
echo "   - RC_PASS: (your desired password)"
echo ""
echo "🔐 Security: Your rclone.conf won't be stored in git!"
echo "🆓 Render free plan limitations:"
echo "   - Service sleeps after 15 minutes of inactivity"
echo "   - 750 hours/month usage limit"