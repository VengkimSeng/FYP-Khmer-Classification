#!/bin/bash
# Development server startup script for Khmer News Classifier
# This script runs the application in development mode with hot-reload and debugging

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

echo "🚀 Starting Khmer News Classifier in Development Mode"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    log_warning "No virtual environment found. Creating one..."
    python3 -m venv venv
    log_success "Virtual environment created"
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    log_info "Activated virtual environment: venv"
elif [ -d ".venv" ]; then
    source .venv/bin/activate
    log_info "Activated virtual environment: .venv"
fi

# Install/upgrade requirements
log_info "Installing/updating requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if required model files exist
log_info "Checking for required model files..."

if [ ! -d "Demo_model" ]; then
    log_error "Demo_model directory not found!"
    echo "Please ensure the following files exist:"
    echo "  - Demo_model/svm_model.joblib"
    echo "  - Demo_model/config.json"
    exit 1
fi

if [ ! -f "Demo_model/svm_model.joblib" ]; then
    log_error "SVM model file not found: Demo_model/svm_model.joblib"
    exit 1
fi

if [ ! -f "Demo_model/config.json" ]; then
    log_error "Config file not found: Demo_model/config.json"
    exit 1
fi

if [ ! -f "cc.km.300.bin" ]; then
    log_warning "FastText model not found: cc.km.300.bin"
    log_info "The app will work with SVM only, or download the model manually"
fi

log_success "All required files found"

# Set development environment variables
export STREAMLIT_DEBUG=true
export STREAMLIT_SERVER_RUN_ON_SAVE=true
export STREAMLIT_SERVER_HEADLESS=false
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_GLOBAL_LOG_LEVEL=info

# Get the port from command line argument or use default
PORT=${1:-8501}
HOST=${2:-localhost}

log_info "Starting Streamlit development server..."
log_info "Host: $HOST"
log_info "Port: $PORT"
log_info "Application: khmer_news_classifier_pro.py"
echo ""
log_success "🌐 Development server will be available at: http://$HOST:$PORT"
log_info "📝 Auto-reload is enabled - changes will be reflected automatically"
log_info "🔧 Debug mode is ON - detailed error messages will be shown"
echo ""
log_warning "Press Ctrl+C to stop the development server"
echo ""

# Start Streamlit with development settings
streamlit run khmer_news_classifier_pro.py \
    --server.port=$PORT \
    --server.address=$HOST \
    --server.headless=false \
    --server.runOnSave=true \
    --server.allowRunOnSave=true \
    --server.fileWatcherType=auto \
    --client.showErrorDetails=true \
    --client.toolbarMode=developer \
    --global.logLevel=info
