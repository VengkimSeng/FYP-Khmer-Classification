#!/bin/bash
# Download FastText model for Khmer on the droplet
# Usage: ./download_fasttext_model.sh [server_ip] [ssh_user]

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
    echo "Usage: ./download_fasttext_model.sh [server_ip] [ssh_user]"
    echo "Example: ./download_fasttext_model.sh 192.168.1.100 root"
    exit 1
fi

# Function to run commands on remote server
run_remote() {
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$1"
}

log_info "Downloading FastText model to $SERVER_IP..."

# Check if app directory exists
if ! run_remote "[ -d $APP_DIR ]"; then
    log_error "Application directory $APP_DIR not found. Please deploy the application first."
    exit 1
fi

# Check if model already exists
if run_remote "[ -f $APP_DIR/cc.km.300.bin ]"; then
    log_warning "FastText model already exists. Do you want to re-download? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Keeping existing model"
        exit 0
    fi
    log_info "Removing existing model..."
    run_remote "rm -f $APP_DIR/cc.km.300.bin*"
fi

# Create download directory and set up environment
run_remote "cd $APP_DIR"

# Method 1: Try to download the binary model directly
log_info "Attempting to download FastText binary model..."
if run_remote "cd $APP_DIR && timeout 300 wget --progress=dot:giga -O cc.km.300.bin 'https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.vec.gz' && gunzip cc.km.300.bin 2>/dev/null"; then
    log_success "FastText model downloaded via Method 1"
else
    log_warning "Method 1 failed, trying Method 2..."
    
    # Method 2: Download as .vec.gz and convert
    if run_remote "cd $APP_DIR && timeout 600 wget --progress=dot:giga -O cc.km.300.vec.gz 'https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.vec.gz'"; then
        log_info "Extracting model file..."
        run_remote "cd $APP_DIR && gunzip cc.km.300.vec.gz"
        run_remote "cd $APP_DIR && mv cc.km.300.vec cc.km.300.bin"
        log_success "FastText model downloaded via Method 2"
    else
        log_warning "Method 2 failed, trying Method 3 (mirror)..."
        
        # Method 3: Try alternative mirror
        if run_remote "cd $APP_DIR && timeout 600 wget --progress=dot:giga -O cc.km.300.vec.gz 'https://fasttext.cc/docs/en/crawl-vectors.html'"; then
            log_info "Extracting model file..."
            run_remote "cd $APP_DIR && gunzip cc.km.300.vec.gz"
            run_remote "cd $APP_DIR && mv cc.km.300.vec cc.km.300.bin"
            log_success "FastText model downloaded via Method 3"
        else
            log_error "All download methods failed. You may need to:"
            echo "1. Check internet connection on the droplet"
            echo "2. Manually download the model"
            echo "3. Use a different FastText model"
            exit 1
        fi
    fi
fi

# Verify the downloaded model
if run_remote "[ -f $APP_DIR/cc.km.300.bin ]"; then
    MODEL_SIZE=$(run_remote "cd $APP_DIR && du -h cc.km.300.bin | cut -f1")
    log_success "FastText model verified successfully"
    log_info "Model size: $MODEL_SIZE"
    
    # Set proper permissions
    run_remote "chown www-data:www-data $APP_DIR/cc.km.300.bin"
    log_info "File permissions set"
    
    # Restart the application if it's running
    if run_remote "systemctl is-active --quiet khmer-classifier"; then
        log_info "Restarting application to load new model..."
        run_remote "systemctl restart khmer-classifier"
        sleep 5
        
        if run_remote "systemctl is-active --quiet khmer-classifier"; then
            log_success "Application restarted successfully"
        else
            log_warning "Application restart may have failed. Check logs with:"
            echo "ssh $SSH_USER@$SERVER_IP 'journalctl -u khmer-classifier -f'"
        fi
    fi
    
else
    log_error "Model file not found after download"
    exit 1
fi

log_success "FastText model download completed!"
echo ""
echo "The application should now have FastText support enabled."
echo "Access your application at: http://$SERVER_IP"
