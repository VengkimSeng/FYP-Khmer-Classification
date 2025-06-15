#!/bin/bash
# Upload Khmer News Classifier to DigitalOcean Droplet
# Usage: ./upload_to_droplet.sh [server_ip] [ssh_user]

set -e

# Configuration - Update these with your droplet details
SERVER_IP=${1:-"your_droplet_ip"}
SSH_USER=${2:-"root"}
APP_NAME="khmer-news-classifier"
APP_DIR="/opt/$APP_NAME"
LOCAL_DIR="/Users/socheata/Documents/DEV"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required parameters are provided
if [ "$SERVER_IP" = "your_droplet_ip" ]; then
    log_error "Please provide your droplet IP address"
    echo "Usage: ./upload_to_droplet.sh [server_ip] [ssh_user]"
    echo "Example: ./upload_to_droplet.sh 192.168.1.100 root"
    exit 1
fi

log_info "Starting upload to $SERVER_IP as user $SSH_USER"

# Function to run commands on remote server
run_remote() {
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$1"
}

# Test SSH connection
log_info "Testing SSH connection..."
if ! run_remote "echo 'SSH connection successful'"; then
    log_error "Failed to connect to server. Please check your SSH configuration."
    exit 1
fi
log_success "SSH connection established"

# Create application directory on server
log_info "Creating application directory on server..."
run_remote "mkdir -p $APP_DIR"
run_remote "mkdir -p $APP_DIR/Demo_model"
run_remote "mkdir -p $APP_DIR/FastText"
run_remote "mkdir -p $APP_DIR/deployment_configs"

# Upload main application files
log_info "Uploading main application file..."
scp -o StrictHostKeyChecking=no "$LOCAL_DIR/khmer_news_classifier_pro.py" $SSH_USER@$SERVER_IP:$APP_DIR/

log_info "Uploading requirements.txt..."
scp -o StrictHostKeyChecking=no "$LOCAL_DIR/requirements.txt" $SSH_USER@$SERVER_IP:$APP_DIR/

log_info "Uploading packages.txt..."
scp -o StrictHostKeyChecking=no "$LOCAL_DIR/packages.txt" $SSH_USER@$SERVER_IP:$APP_DIR/

# Upload model files
log_info "Uploading Demo_model directory..."
scp -r -o StrictHostKeyChecking=no "$LOCAL_DIR/Demo_model/" $SSH_USER@$SERVER_IP:$APP_DIR/

# Upload FastText model if it exists
if [ -f "$LOCAL_DIR/cc.km.300.bin" ]; then
    log_warning "FastText model found locally but will be downloaded on server instead for faster deployment"
else
    log_info "FastText model not found locally - will download on server"
fi

# Upload stopwords file
if [ -f "$LOCAL_DIR/Khmer-Stop-Word-1000.txt" ]; then
    log_info "Uploading stopwords file..."
    scp -o StrictHostKeyChecking=no "$LOCAL_DIR/Khmer-Stop-Word-1000.txt" $SSH_USER@$SERVER_IP:$APP_DIR/
fi

# Upload deployment configs
log_info "Uploading deployment configurations..."
scp -r -o StrictHostKeyChecking=no "$LOCAL_DIR/deployment_configs/" $SSH_USER@$SERVER_IP:$APP_DIR/

# Upload metadata if it exists
if [ -f "$LOCAL_DIR/metadata.csv" ]; then
    log_info "Uploading metadata.csv..."
    scp -o StrictHostKeyChecking=no "$LOCAL_DIR/metadata.csv" $SSH_USER@$SERVER_IP:$APP_DIR/
fi

# Install system dependencies and Python packages
log_info "Installing system dependencies..."
run_remote "apt update && apt install -y python3 python3-pip python3-venv nginx"

# Create Python virtual environment
log_info "Creating Python virtual environment..."
run_remote "cd $APP_DIR && python3 -m venv venv"

# Install Python packages
log_info "Installing Python packages..."
run_remote "cd $APP_DIR && source venv/bin/activate && pip install --upgrade pip"
run_remote "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt"

# Install additional packages if packages.txt exists
run_remote "cd $APP_DIR && source venv/bin/activate && pip install streamlit"

# Download FastText model for Khmer
log_info "Downloading FastText model for Khmer (this may take 10-15 minutes)..."
run_remote "cd $APP_DIR && wget -O cc.km.300.bin.gz https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.vec.gz"
run_remote "cd $APP_DIR && gunzip cc.km.300.bin.gz"

# Alternative download if the above fails
if ! run_remote "cd $APP_DIR && [ -f cc.km.300.bin ]"; then
    log_warning "Primary FastText download failed, trying alternative method..."
    run_remote "cd $APP_DIR && wget -O cc.km.300.vec.gz https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.vec.gz"
    run_remote "cd $APP_DIR && gunzip cc.km.300.vec.gz"
    run_remote "cd $APP_DIR && mv cc.km.300.vec cc.km.300.bin"
fi

# Check if FastText model was downloaded successfully
if run_remote "cd $APP_DIR && [ -f cc.km.300.bin ]"; then
    log_success "FastText model downloaded successfully"
    MODEL_SIZE=$(run_remote "cd $APP_DIR && du -h cc.km.300.bin | cut -f1")
    log_info "FastText model size: $MODEL_SIZE"
else
    log_warning "FastText model download failed - application will work with SVM only"
fi

# Set up systemd service
log_info "Setting up systemd service..."
cat > /tmp/khmer-classifier.service << EOF
[Unit]
Description=Khmer News Classifier Streamlit App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/streamlit run khmer_news_classifier_pro.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

scp -o StrictHostKeyChecking=no /tmp/khmer-classifier.service $SSH_USER@$SERVER_IP:/etc/systemd/system/
run_remote "systemctl daemon-reload"
run_remote "systemctl enable khmer-classifier"

# Set up nginx configuration
log_info "Setting up nginx reverse proxy..."
cat > /tmp/khmer-classifier-nginx << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }
}
EOF

scp -o StrictHostKeyChecking=no /tmp/khmer-classifier-nginx $SSH_USER@$SERVER_IP:/etc/nginx/sites-available/khmer-classifier
run_remote "ln -sf /etc/nginx/sites-available/khmer-classifier /etc/nginx/sites-enabled/"
run_remote "rm -f /etc/nginx/sites-enabled/default"
run_remote "nginx -t && systemctl reload nginx"

# Set proper permissions
log_info "Setting file permissions..."
run_remote "chown -R www-data:www-data $APP_DIR"
run_remote "chmod +x $APP_DIR/deployment_configs/*.sh"

# Start the application
log_info "Starting the application..."
run_remote "systemctl start khmer-classifier"
run_remote "systemctl status khmer-classifier --no-pager"

# Check if application is running
sleep 5
if run_remote "curl -f http://localhost:8501 > /dev/null 2>&1"; then
    log_success "Application is running successfully!"
    log_success "You can access it at: http://$SERVER_IP"
else
    log_warning "Application may not be fully started yet. Check logs with:"
    echo "ssh $SSH_USER@$SERVER_IP 'journalctl -u khmer-classifier -f'"
fi

# Cleanup temporary files
rm -f /tmp/khmer-classifier.service /tmp/khmer-classifier-nginx

log_success "Deployment completed!"
echo ""
echo "Next steps:"
echo "1. Access your application at: http://$SERVER_IP"
echo "2. Set up SSL certificate if needed: ssh $SSH_USER@$SERVER_IP 'cd $APP_DIR/deployment_configs && ./setup_ssl.sh'"
echo "3. Monitor logs: ssh $SSH_USER@$SERVER_IP 'journalctl -u khmer-classifier -f'"
echo "4. Update application: ssh $SSH_USER@$SERVER_IP 'cd $APP_DIR/deployment_configs && ./update.sh'"
