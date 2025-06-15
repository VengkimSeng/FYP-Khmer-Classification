#!/bin/bash
# Update Khmer News Classifier from GitHub
# Usage: ./update_from_github.sh [server_ip] [ssh_user]

set -e

# Configuration
SERVER_IP=${1:-"your_droplet_ip"}
SSH_USER=${2:-"root"}
APP_DIR="/opt/khmer-news-classifier"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
    echo "Usage: ./update_from_github.sh [server_ip] [ssh_user]"
    echo "Example: ./update_from_github.sh 192.168.1.100 root"
    exit 1
fi

# Function to run commands on remote server
run_remote() {
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$1"
}

log_info "Updating application from GitHub on $SERVER_IP..."

# Check if app directory exists
if ! run_remote "[ -d $APP_DIR ]"; then
    log_error "Application directory not found. Please deploy first using deploy_from_github.sh"
    exit 1
fi

# Stop the application
log_info "Stopping application..."
run_remote "systemctl stop khmer-classifier"

# Pull latest changes from GitHub
log_info "Pulling latest changes from GitHub..."
run_remote "cd $APP_DIR && git pull origin main"

# Update Python dependencies if requirements.txt changed
log_info "Updating Python dependencies..."
run_remote "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt"

# Set proper permissions
run_remote "chown -R www-data:www-data $APP_DIR"

# Start the application
log_info "Starting application..."
run_remote "systemctl start khmer-classifier"

# Check if application is running
sleep 5
if run_remote "systemctl is-active --quiet khmer-classifier"; then
    log_success "Application updated and restarted successfully!"
    log_success "Access at: http://$SERVER_IP"
else
    log_error "Application failed to start after update"
    echo "Check logs: ssh $SSH_USER@$SERVER_IP 'journalctl -u khmer-classifier -f'"
    exit 1
fi

log_success "Update completed!"
