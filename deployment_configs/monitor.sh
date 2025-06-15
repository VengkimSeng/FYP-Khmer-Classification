#!/bin/bash
# System monitoring script for Khmer News Classifier

APP_NAME="khmer-news-classifier"
LOG_FILE="/var/log/$APP_NAME/monitor.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_message() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        log_message "${GREEN}✅ $service is running${NC}"
        return 0
    else
        log_message "${RED}❌ $service is not running${NC}"
        return 1
    fi
}

check_port() {
    local port=$1
    local service=$2
    if netstat -tuln | grep -q ":$port "; then
        log_message "${GREEN}✅ Port $port ($service) is open${NC}"
        return 0
    else
        log_message "${RED}❌ Port $port ($service) is not accessible${NC}"
        return 1
    fi
}

check_disk_space() {
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $usage -gt 80 ]; then
        log_message "${RED}⚠️  Disk usage is ${usage}% - cleanup recommended${NC}"
        return 1
    else
        log_message "${GREEN}✅ Disk usage: ${usage}%${NC}"
        return 0
    fi
}

check_memory() {
    local mem_usage=$(free | awk '/Mem:/ {printf "%.1f", $3/$2 * 100}')
    local mem_int=${mem_usage%.*}
    if [ $mem_int -gt 80 ]; then
        log_message "${YELLOW}⚠️  Memory usage: ${mem_usage}%${NC}"
        return 1
    else
        log_message "${GREEN}✅ Memory usage: ${mem_usage}%${NC}"
        return 0
    fi
}

check_app_health() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501/script-health-check 2>/dev/null)
    if [ "$response" = "200" ]; then
        log_message "${GREEN}✅ Application health check passed${NC}"
        return 0
    else
        log_message "${RED}❌ Application health check failed (HTTP $response)${NC}"
        return 1
    fi
}

restart_app() {
    log_message "${YELLOW}🔄 Restarting application...${NC}"
    supervisorctl restart $APP_NAME
    sleep 10
    if check_app_health; then
        log_message "${GREEN}✅ Application restarted successfully${NC}"
    else
        log_message "${RED}❌ Application restart failed${NC}"
    fi
}

# Main monitoring
log_message "${BLUE}🔍 Starting system health check${NC}"

# Check system services
services_ok=true
check_service nginx || services_ok=false
check_service supervisor || services_ok=false

# Check ports
ports_ok=true
check_port 80 "HTTP" || ports_ok=false
check_port 8501 "Streamlit" || ports_ok=false

# Check resources
resources_ok=true
check_disk_space || resources_ok=false
check_memory || resources_ok=false

# Check application health
app_ok=true
check_app_health || app_ok=false

# Summary
if [ "$services_ok" = true ] && [ "$ports_ok" = true ] && [ "$app_ok" = true ]; then
    log_message "${GREEN}🎉 All systems operational${NC}"
    exit 0
else
    log_message "${RED}⚠️  Issues detected${NC}"
    
    # Auto-restart if only app is failing
    if [ "$services_ok" = true ] && [ "$ports_ok" = true ] && [ "$app_ok" = false ]; then
        restart_app
    fi
    
    exit 1
fi
