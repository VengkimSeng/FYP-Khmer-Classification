#!/bin/bash
# SSL Setup Script using Let's Encrypt

DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"admin@your-domain.com"}
APP_NAME="khmer-news-classifier"

# Colors
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

if [ "$DOMAIN" = "your-domain.com" ]; then
    log_error "Please provide a valid domain name"
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 myapp.com admin@myapp.com"
    exit 1
fi

log_info "Setting up SSL for $DOMAIN"

# Install Certbot
log_info "Installing Certbot..."
apt update
apt install -y certbot python3-certbot-nginx

# Stop nginx temporarily
log_info "Stopping nginx temporarily..."
systemctl stop nginx

# Get SSL certificate
log_info "Obtaining SSL certificate..."
certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email $EMAIL

if [ $? -eq 0 ]; then
    log_success "SSL certificate obtained successfully"
else
    log_error "Failed to obtain SSL certificate"
    systemctl start nginx
    exit 1
fi

# Update nginx configuration for SSL
log_info "Updating nginx configuration..."
cat > /etc/nginx/sites-available/$APP_NAME << EOF
# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Client settings
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_set_header Sec-WebSocket-Extensions \$http_sec_websocket_extensions;
        proxy_set_header Sec-WebSocket-Key \$http_sec_websocket_key;
        proxy_set_header Sec-WebSocket-Version \$http_sec_websocket_version;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Disable proxy buffering
        proxy_buffering off;
        proxy_cache off;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8501/script-health-check;
        access_log off;
    }
}
EOF

# Test nginx configuration
log_info "Testing nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    log_success "Nginx configuration is valid"
else
    log_error "Nginx configuration is invalid"
    exit 1
fi

# Start nginx
log_info "Starting nginx..."
systemctl start nginx
systemctl reload nginx

# Set up automatic renewal
log_info "Setting up automatic SSL renewal..."
cat > /etc/cron.d/certbot-renew << EOF
# Renew SSL certificates twice daily
0 12 * * * root /usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"
0 0 * * * root /usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# Update firewall for HTTPS
log_info "Updating firewall rules..."
ufw allow 443

log_success "🎉 SSL setup completed successfully!"
log_info "Your site is now available at: https://$DOMAIN"
log_info "SSL certificate will auto-renew before expiration"

# Test the setup
log_info "Testing SSL setup..."
sleep 5
response=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health)
if [ "$response" = "200" ]; then
    log_success "✅ SSL setup verified - site is accessible"
else
    log_warning "⚠️ SSL setup completed but site may not be fully accessible yet"
fi
