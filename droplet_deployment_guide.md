# DigitalOcean Droplet Deployment Guide

## 🚀 **Deploying Khmer News Classifier on DigitalOcean Droplet**

### **Recommended Droplet Specifications**

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **RAM** | 4GB | 8GB | FastText model needs ~3GB |
| **CPU** | 2 vCPUs | 4 vCPUs | Better for concurrent users |
| **Storage** | 50GB SSD | 100GB SSD | For models and logs |
| **OS** | Ubuntu 22.04 | Ubuntu 22.04 LTS | Stable and supported |

**Estimated Cost**: $24-48/month (vs $0 Streamlit free but with limitations)

### **Step 1: Create and Configure Droplet**

1. **Create Droplet**
   ```bash
   # On DigitalOcean dashboard:
   # - Choose Ubuntu 22.04 LTS
   # - Select 4GB+ RAM droplet
   # - Add SSH key
   # - Enable monitoring
   ```

2. **Initial Server Setup**
   ```bash
   # SSH into your droplet
   ssh root@your-droplet-ip
   
   # Update system
   apt update && apt upgrade -y
   
   # Install essential packages
   apt install -y python3 python3-pip python3-venv nginx supervisor git htop
   
   # Create application user
   adduser --disabled-password --gecos "" khmerapp
   usermod -aG sudo khmerapp
   ```

### **Step 2: Application Setup**

1. **Clone Repository**
   ```bash
   # Switch to app user
   su - khmerapp
   
   # Clone your repository
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Download FastText Model**
   ```bash
   # Download the FastText model
   python download_fasttext_model.py
   
   # Verify model exists
   ls -lh cc.km.300.bin
   ```

### **Step 3: Production Configuration**

1. **Create Production Config**
   ```bash
   # Create config file
   nano production_config.py
   ```

2. **Nginx Configuration**
   ```bash
   # Create nginx config
   sudo nano /etc/nginx/sites-available/khmer-classifier
   ```

3. **Supervisor Configuration**
   ```bash
   # Create supervisor config
   sudo nano /etc/supervisor/conf.d/khmer-classifier.conf
   ```

### **Step 4: SSL and Domain Setup**

1. **Domain Configuration**
   ```bash
   # Point your domain to droplet IP
   # Example: classifier.yourdomain.com -> your-droplet-ip
   ```

2. **SSL Certificate**
   ```bash
   # Install certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Get SSL certificate
   sudo certbot --nginx -d classifier.yourdomain.com
   ```

### **Step 5: Monitoring and Maintenance**

1. **Log Management**
   ```bash
   # Setup log rotation
   sudo nano /etc/logrotate.d/khmer-classifier
   ```

2. **Monitoring Setup**
   ```bash
   # Install monitoring tools
   sudo apt install htop iotop nethogs
   ```

---

## 📁 **Configuration Files**

### **1. Production Config (`production_config.py`)**
```python
import os
import streamlit as st

# Production settings
PRODUCTION = True
DEBUG = False

# Server settings
HOST = "0.0.0.0"
PORT = 8501

# Security settings
ENABLE_CORS = False
ENABLE_XSRF_PROTECTION = True

# Performance settings
MAX_UPLOAD_SIZE = 200  # MB
SERVER_MAX_HEAP_SIZE = "4g"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "/var/log/khmer-classifier/app.log"

# Model settings
MODEL_CACHE_SIZE = 1  # Keep models in memory
FASTTEXT_MODEL_PATH = "/home/khmerapp/your-repo/cc.km.300.bin"
SVM_MODEL_PATH = "/home/khmerapp/your-repo/Demo_model/svm_model.joblib"

# Analytics
ENABLE_ANALYTICS = True
ANALYTICS_DB_PATH = "/var/lib/khmer-classifier/analytics.db"
```

### **2. Nginx Configuration (`/etc/nginx/sites-available/khmer-classifier`)**
```nginx
server {
    listen 80;
    server_name classifier.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name classifier.yourdomain.com;
    
    # SSL Configuration (certbot will add this)
    ssl_certificate /etc/letsencrypt/live/classifier.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/classifier.yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Proxy settings
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # File upload size
        client_max_body_size 200M;
    }
    
    # Static files (if any)
    location /static/ {
        alias /home/khmerapp/your-repo/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### **3. Supervisor Configuration (`/etc/supervisor/conf.d/khmer-classifier.conf`)**
```ini
[program:khmer-classifier]
command=/home/khmerapp/your-repo/venv/bin/streamlit run khmer_news_classifier_pro.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=true
directory=/home/khmerapp/your-repo
user=khmerapp
group=khmerapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/khmer-classifier/app.log
stderr_logfile=/var/log/khmer-classifier/error.log
environment=PYTHONPATH="/home/khmerapp/your-repo",STREAMLIT_SERVER_HEADLESS=true

[program:khmer-classifier-worker]
command=/home/khmerapp/your-repo/venv/bin/python -m celery worker -A tasks --loglevel=info
directory=/home/khmerapp/your-repo
user=khmerapp
group=khmerapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/khmer-classifier/worker.log
```

### **4. Systemd Service (Alternative to Supervisor)**
```ini
# /etc/systemd/system/khmer-classifier.service
[Unit]
Description=Khmer News Classifier
After=network.target

[Service]
Type=simple
User=khmerapp
Group=khmerapp
WorkingDirectory=/home/khmerapp/your-repo
Environment=PATH=/home/khmerapp/your-repo/venv/bin
Environment=PYTHONPATH=/home/khmerapp/your-repo
ExecStart=/home/khmerapp/your-repo/venv/bin/streamlit run khmer_news_classifier_pro.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **5. Log Rotation (`/etc/logrotate.d/khmer-classifier`)**
```
/var/log/khmer-classifier/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 khmerapp khmerapp
    postrotate
        supervisorctl restart khmer-classifier
    endscript
}
```

---

## 🔧 **Deployment Script**

### **Automated Deployment Script (`deploy.sh`)**
```bash
#!/bin/bash

# Khmer News Classifier Deployment Script
set -e

echo "🚀 Starting Khmer News Classifier deployment..."

# Variables
APP_USER="khmerapp"
APP_DIR="/home/$APP_USER/khmer-classifier"
REPO_URL="https://github.com/your-username/your-repo.git"
DOMAIN="classifier.yourdomain.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root"
   exit 1
fi

# Update system
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
log_info "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git htop curl

# Create directories
log_info "Creating application directories..."
sudo mkdir -p /var/log/khmer-classifier
sudo mkdir -p /var/lib/khmer-classifier
sudo chown -R $APP_USER:$APP_USER /var/log/khmer-classifier
sudo chown -R $APP_USER:$APP_USER /var/lib/khmer-classifier

# Clone or update repository
if [ -d "$APP_DIR" ]; then
    log_info "Updating existing repository..."
    cd $APP_DIR
    git pull origin main
else
    log_info "Cloning repository..."
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

# Setup Python environment
log_info "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Download FastText model if not exists
if [ ! -f "cc.km.300.bin" ]; then
    log_info "Downloading FastText model..."
    python download_fasttext_model.py
else
    log_info "FastText model already exists"
fi

# Setup Nginx
log_info "Configuring Nginx..."
sudo cp configs/nginx.conf /etc/nginx/sites-available/khmer-classifier
sudo ln -sf /etc/nginx/sites-available/khmer-classifier /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Setup Supervisor
log_info "Configuring Supervisor..."
sudo cp configs/supervisor.conf /etc/supervisor/conf.d/khmer-classifier.conf
sudo supervisorctl reread
sudo supervisorctl update

# Setup SSL (if domain provided)
if [ ! -z "$DOMAIN" ]; then
    log_info "Setting up SSL certificate..."
    sudo apt install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
fi

# Start services
log_info "Starting services..."
sudo systemctl enable nginx
sudo systemctl restart nginx
sudo supervisorctl start khmer-classifier

# Setup log rotation
log_info "Setting up log rotation..."
sudo cp configs/logrotate.conf /etc/logrotate.d/khmer-classifier

# Final checks
log_info "Running final checks..."
sleep 5

if curl -f http://localhost:8501 > /dev/null 2>&1; then
    log_info "✅ Application is running successfully!"
    log_info "🌐 Access your app at: http://$DOMAIN"
else
    log_error "❌ Application failed to start. Check logs:"
    log_error "   sudo tail -f /var/log/khmer-classifier/app.log"
fi

echo ""
log_info "🎉 Deployment completed!"
log_info "📊 Monitor your app:"
log_info "   - Logs: sudo tail -f /var/log/khmer-classifier/app.log"
log_info "   - Status: sudo supervisorctl status khmer-classifier"
log_info "   - Restart: sudo supervisorctl restart khmer-classifier"
```

---

## 🔍 **Monitoring and Maintenance**

### **Health Check Script (`health_check.sh`)**
```bash
#!/bin/bash

# Health check script
URL="http://localhost:8501"
TIMEOUT=10

if curl -f --max-time $TIMEOUT $URL > /dev/null 2>&1; then
    echo "✅ Service is healthy"
    exit 0
else
    echo "❌ Service is down"
    # Restart service
    sudo supervisorctl restart khmer-classifier
    exit 1
fi
```

### **Backup Script (`backup.sh`)**
```bash
#!/bin/bash

# Backup script
BACKUP_DIR="/backup/khmer-classifier"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup models
tar -czf $BACKUP_DIR/models_$DATE.tar.gz Demo_model/ cc.km.300.bin

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/khmer-classifier/

# Backup analytics data
if [ -f "/var/lib/khmer-classifier/analytics.db" ]; then
    cp /var/lib/khmer-classifier/analytics.db $BACKUP_DIR/analytics_$DATE.db
fi

echo "Backup completed: $BACKUP_DIR"
```

### **Performance Monitoring**
```bash
# Monitor system resources
htop

# Monitor network connections
sudo netstat -tulpn | grep :8501

# Monitor application logs
sudo tail -f /var/log/khmer-classifier/app.log

# Monitor Nginx access logs
sudo tail -f /var/log/nginx/access.log
```

---

## 💰 **Cost Comparison**

| Platform | Monthly Cost | RAM | Storage | Bandwidth | Custom Domain | SSL |
|----------|-------------|-----|---------|-----------|---------------|-----|
| **Streamlit Free** | $0 | ~1GB | Limited | Limited | ❌ | ❌ |
| **DigitalOcean 4GB** | $24 | 4GB | 80GB SSD | 4TB | ✅ | ✅ |
| **DigitalOcean 8GB** | $48 | 8GB | 160GB SSD | 5TB | ✅ | ✅ |

**Benefits of Droplet Deployment:**
- ✅ Full control over resources
- ✅ Can handle large FastText model
- ✅ Better performance for multiple users
- ✅ Custom domain and SSL
- ✅ No platform limitations
- ✅ Professional appearance

Your Khmer News Classifier will run much better on a droplet with full access to the FastText model and better performance!
