#!/bin/bash
# Quick update script for server - run this on your DigitalOcean droplet
# Usage: curl -sSL https://raw.githubusercontent.com/VengkimSeng/FYP-Khmer-Classification/main/quick_update.sh | bash

set -e

echo "🔄 Updating Khmer News Classifier on server..."

# Navigate to application directory
cd /opt/khmer-news-classifier

# Stop the service
echo "Stopping application service..."
systemctl stop khmer-classifier || true

# Pull latest changes
echo "Pulling latest code from GitHub..."
git pull origin main

# Update systemd service with corrected configuration
echo "Updating systemd service configuration..."
cat > /etc/systemd/system/khmer-classifier.service << 'EOF'
[Unit]
Description=Khmer News Classifier Streamlit App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/khmer-news-classifier
Environment=PATH=/opt/khmer-news-classifier/venv/bin
Environment=STREAMLIT_DEBUG=true
Environment=STREAMLIT_SERVER_HEADLESS=true
Environment=STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ExecStart=/opt/khmer-news-classifier/venv/bin/streamlit run khmer_news_classifier_pro.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --server.enableCORS=true --server.enableXsrfProtection=false --client.showErrorDetails=true
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and restart service
echo "Reloading systemd configuration..."
systemctl daemon-reload

echo "Starting application service..."
systemctl start khmer-classifier

echo "Enabling service for auto-start..."
systemctl enable khmer-classifier

# Check status
echo "Checking service status..."
systemctl status khmer-classifier --no-pager

echo "✅ Update completed!"
echo "🌐 Application should be available at: http://$(curl -s ipinfo.io/ip):8501"
echo "📋 To check logs: journalctl -u khmer-classifier -f"
