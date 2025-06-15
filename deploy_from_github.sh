#!/bin/bash
# Deploy Khmer News Classifier from GitHub to DigitalOcean Droplet
# Usage: ./deploy_from_github.sh [server_ip] [github_repo_url] [ssh_user]

set -e

# Configuration - Update these with your details
SERVER_IP=${1:-"your_droplet_ip"}
GITHUB_REPO=${2:-"your_github_repo_url"}
SSH_USER=${3:-"root"}
APP_NAME="khmer-news-classifier"
APP_DIR="/opt/$APP_NAME"

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
    log_error "Please provide your droplet IP address and GitHub repository URL"
    echo "Usage: ./deploy_from_github.sh [server_ip] [github_repo_url] [ssh_user]"
    echo "Example: ./deploy_from_github.sh 192.168.1.100 https://github.com/username/khmer-news-classifier.git root"
    exit 1
fi

if [ "$GITHUB_REPO" = "your_github_repo_url" ]; then
    log_error "Please provide your GitHub repository URL"
    echo "Usage: ./deploy_from_github.sh [server_ip] [github_repo_url] [ssh_user]"
    echo "Example: ./deploy_from_github.sh 192.168.1.100 https://github.com/username/khmer-news-classifier.git root"
    exit 1
fi

log_info "Starting deployment from GitHub to $SERVER_IP as user $SSH_USER"
log_info "Repository: $GITHUB_REPO"

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

# Install system dependencies
log_info "Installing system dependencies..."
run_remote "apt update && apt install -y git python3 python3-pip python3-venv nginx curl wget"

# Remove existing app directory if it exists
if run_remote "[ -d $APP_DIR ]"; then
    log_warning "Existing application directory found. Removing..."
    run_remote "systemctl stop khmer-classifier 2>/dev/null || true"
    run_remote "rm -rf $APP_DIR"
fi

# Clone repository from GitHub
log_info "Cloning repository from GitHub..."
run_remote "git clone $GITHUB_REPO $APP_DIR"

# Change to app directory
run_remote "cd $APP_DIR"

# Create Python virtual environment
log_info "Creating Python virtual environment..."
run_remote "cd $APP_DIR && python3 -m venv venv"

# Install Python packages
log_info "Installing Python packages..."
run_remote "cd $APP_DIR && source venv/bin/activate && pip install --upgrade pip"
run_remote "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt"

# Download FastText model for Khmer (this is the large file we don't want in Git)
log_info "Downloading FastText model for Khmer (this may take 10-15 minutes)..."

# Method 1: Try to download the FastText model
if run_remote "cd $APP_DIR && timeout 600 wget --progress=dot:giga -O cc.km.300.vec.gz 'https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.vec.gz'"; then
    log_info "Extracting FastText model..."
    run_remote "cd $APP_DIR && gunzip cc.km.300.vec.gz"
    run_remote "cd $APP_DIR && mv cc.km.300.vec cc.km.300.bin"
    log_success "FastText model downloaded successfully"
else
    log_warning "FastText model download failed - application will work with SVM only"
fi

# Verify model download
if run_remote "cd $APP_DIR && [ -f cc.km.300.bin ]"; then
    MODEL_SIZE=$(run_remote "cd $APP_DIR && du -h cc.km.300.bin | cut -f1")
    log_success "FastText model verified: $MODEL_SIZE"
else
    log_warning "FastText model not available - app will use SVM model only"
fi

# Set up systemd service
log_info "Setting up systemd service..."
run_remote "cat > /etc/systemd/system/khmer-classifier.service << 'EOF'
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
EOF"

run_remote "systemctl daemon-reload"
run_remote "systemctl enable khmer-classifier"

# Set up nginx configuration
log_info "Setting up nginx reverse proxy..."
run_remote "cat > /etc/nginx/sites-available/khmer-classifier << 'EOF'
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
EOF"

run_remote "ln -sf /etc/nginx/sites-available/khmer-classifier /etc/nginx/sites-enabled/"
run_remote "rm -f /etc/nginx/sites-enabled/default"
run_remote "nginx -t && systemctl reload nginx"

# Set proper permissions
log_info "Setting file permissions..."
run_remote "chown -R www-data:www-data $APP_DIR"
run_remote "chmod +x $APP_DIR/deployment_configs/*.sh 2>/dev/null || true"

# Start the application
log_info "Starting the application..."
run_remote "systemctl start khmer-classifier"

# Check if application is running
sleep 10
run_remote "systemctl status khmer-classifier --no-pager"

if run_remote "curl -f http://localhost:8501 > /dev/null 2>&1"; then
    log_success "Application is running successfully!"
    log_success "You can access it at: http://$SERVER_IP"
else
    log_warning "Application may not be fully started yet. Check logs with:"
    echo "ssh $SSH_USER@$SERVER_IP 'journalctl -u khmer-classifier -f'"
fi

log_success "GitHub deployment completed!"
echo ""
echo "Deployment Summary:"
echo "- Repository: $GITHUB_REPO"
echo "- Server: $SERVER_IP"
echo "- Application URL: http://$SERVER_IP"
echo ""
echo "Next steps:"
echo "1. Access your application at: http://$SERVER_IP"
echo "2. Monitor logs: ssh $SSH_USER@$SERVER_IP 'journalctl -u khmer-classifier -f'"
echo "3. To update: ssh $SSH_USER@$SERVER_IP 'cd $APP_DIR && git pull && systemctl restart khmer-classifier'"
echo ""
echo "Troubleshooting:"
echo "- Check app status: ssh $SSH_USER@$SERVER_IP 'systemctl status khmer-classifier'"
echo "- Restart app: ssh $SSH_USER@$SERVER_IP 'systemctl restart khmer-classifier'"
