#!/bin/bash
# Upload SSL certificates directly to server
# Usage: ./upload_ssl_certs.sh [server_ip] [ssh_user]

set -e

# Configuration
SERVER_IP=${1:-"your_droplet_ip"}
SSH_USER=${2:-"root"}
APP_NAME="khmer-news-classifier"
APP_DIR="/opt/$APP_NAME"
SSL_DIR="/etc/ssl/certs"
NGINX_SSL_DIR="/etc/nginx/ssl"

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
    echo "Usage: ./upload_ssl_certs.sh [server_ip] [ssh_user]"
    echo "Example: ./upload_ssl_certs.sh 192.168.1.100 root"
    exit 1
fi

# Local certificate file paths
LOCAL_CERT_FILES=(
    "khnewsclassifier_tech/khnewsclassifier_tech.crt"
    "khnewsclassifier_tech/khnewsclassifier_tech.ca-bundle"
    "server.key"
    "server_csr.txt"
)

# Function to run commands on remote server
run_remote() {
    ssh -o StrictHostKeyChecking=no $SSH_USER@$SERVER_IP "$1"
}

# Test SSH connection
log_info "Testing SSH connection to $SERVER_IP..."
if ! run_remote "echo 'SSH connection successful'"; then
    log_error "Failed to connect to server. Please check your SSH configuration."
    exit 1
fi
log_success "SSH connection established"

# Check if certificate files exist locally
log_info "Checking for SSL certificate files..."
missing_files=()
for file in "${LOCAL_CERT_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    log_warning "The following certificate files were not found:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    log_info "Continuing with available files..."
fi

# Create SSL directories on server
log_info "Creating SSL directories on server..."
run_remote "mkdir -p $NGINX_SSL_DIR"
run_remote "mkdir -p $SSL_DIR"
run_remote "mkdir -p $APP_DIR/ssl"

# Upload certificate files
log_info "Uploading SSL certificate files..."

if [ -f "khnewsclassifier_tech/khnewsclassifier_tech.crt" ]; then
    log_info "Uploading SSL certificate..."
    scp -o StrictHostKeyChecking=no khnewsclassifier_tech/khnewsclassifier_tech.crt $SSH_USER@$SERVER_IP:$NGINX_SSL_DIR/
    log_success "SSL certificate uploaded"
fi

if [ -f "khnewsclassifier_tech/khnewsclassifier_tech.ca-bundle" ]; then
    log_info "Uploading CA bundle..."
    scp -o StrictHostKeyChecking=no khnewsclassifier_tech/khnewsclassifier_tech.ca-bundle $SSH_USER@$SERVER_IP:$NGINX_SSL_DIR/
    log_success "CA bundle uploaded"
fi

if [ -f "server.key" ]; then
    log_info "Uploading private key..."
    scp -o StrictHostKeyChecking=no server.key $SSH_USER@$SERVER_IP:$NGINX_SSL_DIR/
    # Set secure permissions for private key
    run_remote "chmod 600 $NGINX_SSL_DIR/server.key"
    log_success "Private key uploaded with secure permissions"
fi

if [ -f "server_csr.txt" ]; then
    log_info "Uploading CSR file (for reference)..."
    scp -o StrictHostKeyChecking=no server_csr.txt $SSH_USER@$SERVER_IP:$NGINX_SSL_DIR/
    log_success "CSR file uploaded"
fi

# Create combined certificate file if both cert and ca-bundle exist
if [ -f "khnewsclassifier_tech/khnewsclassifier_tech.crt" ] && [ -f "khnewsclassifier_tech/khnewsclassifier_tech.ca-bundle" ]; then
    log_info "Creating combined certificate file..."
    run_remote "cat $NGINX_SSL_DIR/khnewsclassifier_tech.crt $NGINX_SSL_DIR/khnewsclassifier_tech.ca-bundle > $NGINX_SSL_DIR/fullchain.crt"
    log_success "Combined certificate created at $NGINX_SSL_DIR/fullchain.crt"
fi

# Set proper ownership and permissions
log_info "Setting SSL file permissions..."
run_remote "chown -R root:root $NGINX_SSL_DIR"
run_remote "chmod 644 $NGINX_SSL_DIR/*.crt $NGINX_SSL_DIR/*.ca-bundle 2>/dev/null || true"
run_remote "chmod 600 $NGINX_SSL_DIR/*.key 2>/dev/null || true"

# Create SSL-enabled nginx configuration
log_info "Creating SSL-enabled nginx configuration..."
run_remote "cat > /etc/nginx/sites-available/khmer-classifier-ssl << 'EOF'
server {
    listen 80;
    server_name _;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;

    ssl_certificate $NGINX_SSL_DIR/fullchain.crt;
    ssl_certificate_key $NGINX_SSL_DIR/server.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_session_timeout 10m;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;

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

# Test nginx configuration
log_info "Testing nginx configuration..."
if run_remote "nginx -t"; then
    log_success "Nginx configuration is valid"
    
    # Ask user if they want to switch to SSL configuration
    read -p "Do you want to enable SSL configuration now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Enabling SSL configuration..."
        run_remote "ln -sf /etc/nginx/sites-available/khmer-classifier-ssl /etc/nginx/sites-enabled/khmer-classifier"
        run_remote "systemctl reload nginx"
        log_success "SSL configuration enabled!"
        log_success "Your application is now available at: https://$SERVER_IP"
    else
        log_info "SSL configuration created but not enabled. To enable later, run:"
        echo "ssh $SSH_USER@$SERVER_IP 'ln -sf /etc/nginx/sites-available/khmer-classifier-ssl /etc/nginx/sites-enabled/khmer-classifier && systemctl reload nginx'"
    fi
else
    log_error "Nginx configuration test failed. Please check the SSL certificate files."
    exit 1
fi

log_success "SSL certificate upload completed!"
echo ""
echo "SSL Upload Summary:"
echo "- Certificates uploaded to: $NGINX_SSL_DIR/"
echo "- SSL configuration created: /etc/nginx/sites-available/khmer-classifier-ssl"
echo "- Server: $SERVER_IP"
echo ""
echo "SSL Files uploaded:"
for file in "${LOCAL_CERT_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (not found)"
    fi
done
echo ""
echo "Next steps:"
echo "1. Verify SSL: https://$SERVER_IP"
echo "2. Check certificate: ssh $SSH_USER@$SERVER_IP 'openssl x509 -in $NGINX_SSL_DIR/khnewsclassifier_tech.crt -text -noout'"
echo "3. Monitor nginx: ssh $SSH_USER@$SERVER_IP 'tail -f /var/log/nginx/error.log'"
