#!/bin/bash
# Production server startup script for Khmer News Classifier
# This script runs the application in production mode

set -e

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

echo "🚀 Starting Khmer News Classifier in Production Mode"
echo "===================================================="

# Set production environment variables
export STREAMLIT_DEBUG=false
export STREAMLIT_SERVER_RUN_ON_SAVE=false
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_GLOBAL_LOG_LEVEL=warning

# Get configuration from environment or use defaults
PORT=${STREAMLIT_PORT:-8501}
HOST=${STREAMLIT_HOST:-0.0.0.0}

log_info "Starting Streamlit production server..."
log_info "Host: $HOST"
log_info "Port: $PORT"
echo ""

# Start Streamlit with production settings
streamlit run khmer_news_classifier_pro.py \
    --server.port=$PORT \
    --server.address=$HOST \
    --server.headless=true \
    --server.runOnSave=false \
    --server.allowRunOnSave=false \
    --server.fileWatcherType=none \
    --client.showErrorDetails=false \
    --client.toolbarMode=minimal \
    --global.logLevel=warning \
    --server.enableCORS=true \
    --server.enableXsrfProtection=true
