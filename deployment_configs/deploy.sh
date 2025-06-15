#!/bin/bash
# Automated Deployment Script for Khmer News Classifier
# Usage: ./deploy.sh [server_ip] [ssh_user]

set -e

# Configuration
SERVER_IP=${1:-"your_server_ip"}
SSH_USER=${2:-"root"}
APP_NAME="khmer-news-classifier"
APP_DIR="/opt/$APP_NAME"
REPO_URL="https://github.com/VengkimSeng/FYP-Khmer-Classification.git"

echo "🚀 Starting deployment to $SERVER_IP"

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

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ]; then
    log_warning "SSH key not found. Make sure you can SSH to the server."
fi

# Function to run commands on remote server
run_remote() {
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$1"
}

# Function to copy files to remote server
copy_to_remote() {
    scp -o StrictHostKeyChecking=no -r "$1" $SSH_USER@$SERVER_IP:"$2"
}

log_info "Step 1: Updating system packages"
run_remote "apt update && apt upgrade -y"

log_info "Step 2: Installing system dependencies"
run_remote "apt install -y python3 python3-pip python3-venv nginx supervisor git htop curl wget unzip"

log_info "Step 3: Setting up application directory"
run_remote "mkdir -p $APP_DIR && cd $APP_DIR"

log_info "Step 4: Cloning repository"
run_remote "cd $APP_DIR && rm -rf * && git clone $REPO_URL . || (rm -rf .git && git clone $REPO_URL .)"

log_info "Step 5: Setting up Python virtual environment"
run_remote "cd $APP_DIR && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip"

log_info "Step 6: Installing Python dependencies"
run_remote "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt"

log_info "Step 7: Installing additional production dependencies"
run_remote "cd $APP_DIR && source venv/bin/activate && pip install gunicorn watchdog"

log_info "Step 8: Creating application user"
run_remote "useradd -r -s /bin/false $APP_NAME || true"
run_remote "chown -R $APP_NAME:$APP_NAME $APP_DIR"

log_info "Step 9: Copying configuration files"
copy_to_remote "deployment_configs/nginx.conf" "/etc/nginx/sites-available/$APP_NAME"
copy_to_remote "deployment_configs/supervisor.conf" "/etc/supervisor/conf.d/$APP_NAME.conf"

log_info "Step 10: Enabling Nginx site"
run_remote "ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/ && rm -f /etc/nginx/sites-enabled/default"

log_info "Step 11: Testing Nginx configuration"
run_remote "nginx -t"

log_info "Step 12: Setting up firewall"
run_remote "ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw --force enable"

log_info "Step 13: Creating log directories"
run_remote "mkdir -p /var/log/$APP_NAME && chown $APP_NAME:$APP_NAME /var/log/$APP_NAME"

log_info "Step 14: Starting services"
run_remote "supervisorctl reread && supervisorctl update && supervisorctl start $APP_NAME"
run_remote "systemctl reload nginx && systemctl enable nginx"

log_info "Step 15: Downloading FastText model (this may take a while...)"
run_remote "cd $APP_DIR && source venv/bin/activate && python download_fasttext_model.py" || log_warning "FastText model download failed - app will run in SVM-only mode"

log_info "Step 16: Final service restart"
run_remote "supervisorctl restart $APP_NAME"

log_success "🎉 Deployment completed successfully!"
log_info "Your app should be available at: http://$SERVER_IP"
log_info "To check status: ssh $SSH_USER@$SERVER_IP 'supervisorctl status'"
log_info "To view logs: ssh $SSH_USER@$SERVER_IP 'tail -f /var/log/$APP_NAME/app.log'"

echo
echo "📋 Quick Commands:"
echo "  Check app status: ssh $SSH_USER@$SERVER_IP 'supervisorctl status $APP_NAME'"
echo "  Restart app: ssh $SSH_USER@$SERVER_IP 'supervisorctl restart $APP_NAME'"
echo "  View logs: ssh $SSH_USER@$SERVER_IP 'tail -f /var/log/$APP_NAME/app.log'"
echo "  Update code: ssh $SSH_USER@$SERVER_IP 'cd $APP_DIR && git pull && supervisorctl restart $APP_NAME'"
