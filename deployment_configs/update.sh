#!/bin/bash
# Update and maintenance script

APP_NAME="khmer-news-classifier"
APP_DIR="/opt/$APP_NAME"
BACKUP_DIR="/opt/backups/$APP_NAME"

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

# Create backup
create_backup() {
    log_info "Creating backup..."
    mkdir -p $BACKUP_DIR
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="$BACKUP_DIR/backup_$timestamp.tar.gz"
    
    cd $APP_DIR
    tar -czf $backup_file \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='cc.km.300.bin' \
        .
    
    if [ $? -eq 0 ]; then
        log_success "Backup created: $backup_file"
        
        # Keep only last 5 backups
        cd $BACKUP_DIR
        ls -t backup_*.tar.gz | tail -n +6 | xargs -r rm
        log_info "Old backups cleaned up"
    else
        log_error "Backup failed"
        exit 1
    fi
}

# Update application
update_app() {
    log_info "Stopping application..."
    supervisorctl stop $APP_NAME
    
    log_info "Pulling latest code..."
    cd $APP_DIR
    git stash
    git pull origin main
    
    log_info "Updating dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_info "Starting application..."
    supervisorctl start $APP_NAME
    
    # Wait and check if app started successfully
    sleep 15
    if supervisorctl status $APP_NAME | grep -q "RUNNING"; then
        log_success "Application updated and running"
        
        # Test health endpoint
        sleep 5
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/script-health-check)
        if [ "$response" = "200" ]; then
            log_success "✅ Health check passed"
        else
            log_warning "⚠️ Health check failed (HTTP $response)"
        fi
    else
        log_error "Application failed to start after update"
        exit 1
    fi
}

# System maintenance
system_maintenance() {
    log_info "Performing system maintenance..."
    
    # Update system packages
    apt update && apt upgrade -y
    
    # Clean package cache
    apt autoremove -y
    apt autoclean
    
    # Clean logs older than 30 days
    find /var/log -name "*.log" -mtime +30 -delete 2>/dev/null || true
    find /var/log -name "*.gz" -mtime +30 -delete 2>/dev/null || true
    
    # Clean temporary files
    find /tmp -type f -mtime +7 -delete 2>/dev/null || true
    
    # Restart services for good measure
    systemctl restart nginx
    systemctl restart supervisor
    
    log_success "System maintenance completed"
}

# Check disk space
check_disk_space() {
    usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $usage -gt 90 ]; then
        log_error "Critical: Disk usage is ${usage}%"
        # Try to clean up
        docker system prune -f 2>/dev/null || true
        apt autoremove -y
        apt autoclean
        log_info "Cleanup attempted"
    elif [ $usage -gt 80 ]; then
        log_warning "Warning: Disk usage is ${usage}%"
    else
        log_info "Disk usage: ${usage}%"
    fi
}

# Main script
case "$1" in
    "backup")
        create_backup
        ;;
    "update")
        create_backup
        update_app
        ;;
    "maintenance")
        system_maintenance
        ;;
    "full")
        check_disk_space
        create_backup
        update_app
        system_maintenance
        ;;
    *)
        echo "Usage: $0 {backup|update|maintenance|full}"
        echo ""
        echo "Commands:"
        echo "  backup      - Create application backup"
        echo "  update      - Update application from git"
        echo "  maintenance - Perform system maintenance"
        echo "  full        - Run all operations"
        exit 1
        ;;
esac

log_success "🎉 Operation completed successfully"
