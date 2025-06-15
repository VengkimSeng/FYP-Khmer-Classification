#!/bin/bash
# Pre-deployment verification script
# Checks if all required files are present before uploading to droplet

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

LOCAL_DIR="/Users/socheata/Documents/DEV"
ERRORS=0

echo "========================================"
echo "Pre-Deployment Verification"
echo "========================================"

# Check main application file
if [ -f "$LOCAL_DIR/khmer_news_classifier_pro.py" ]; then
    log_success "Main application file found"
else
    log_error "khmer_news_classifier_pro.py not found"
    ERRORS=$((ERRORS + 1))
fi

# Check requirements.txt
if [ -f "$LOCAL_DIR/requirements.txt" ]; then
    log_success "requirements.txt found"
else
    log_error "requirements.txt not found"
    ERRORS=$((ERRORS + 1))
fi

# Check Demo_model directory
if [ -d "$LOCAL_DIR/Demo_model" ]; then
    log_success "Demo_model directory found"
    # Check for SVM model
    if [ -f "$LOCAL_DIR/Demo_model/svm_model.joblib" ]; then
        log_success "SVM model found"
    else
        log_warning "SVM model (svm_model.joblib) not found in Demo_model"
    fi
else
    log_error "Demo_model directory not found"
    ERRORS=$((ERRORS + 1))
fi

# Check FastText model
if [ -f "$LOCAL_DIR/cc.km.300.bin" ]; then
    SIZE=$(du -h "$LOCAL_DIR/cc.km.300.bin" | cut -f1)
    log_success "FastText model found ($SIZE)"
else
    log_warning "FastText model (cc.km.300.bin) not found - app will work without it"
fi

# Check stopwords file
if [ -f "$LOCAL_DIR/Khmer-Stop-Word-1000.txt" ]; then
    log_success "Stopwords file found"
else
    log_warning "Stopwords file not found"
fi

# Check deployment configs
if [ -d "$LOCAL_DIR/deployment_configs" ]; then
    log_success "Deployment configs directory found"
else
    log_warning "deployment_configs directory not found"
fi

# Check upload script
if [ -f "$LOCAL_DIR/upload_to_droplet.sh" ]; then
    if [ -x "$LOCAL_DIR/upload_to_droplet.sh" ]; then
        log_success "Upload script is executable"
    else
        log_warning "Upload script found but not executable (run: chmod +x upload_to_droplet.sh)"
    fi
else
    log_error "upload_to_droplet.sh not found"
    ERRORS=$((ERRORS + 1))
fi

# Check SSH key
if [ -f ~/.ssh/id_rsa ] || [ -f ~/.ssh/id_ed25519 ]; then
    log_success "SSH key found"
else
    log_warning "No SSH key found in ~/.ssh/ - make sure you can SSH to your droplet"
fi

echo "========================================"

if [ $ERRORS -eq 0 ]; then
    log_success "All critical files found! Ready for deployment."
    echo ""
    echo "To deploy, run:"
    echo "  ./upload_to_droplet.sh YOUR_DROPLET_IP root"
    echo ""
    echo "Replace YOUR_DROPLET_IP with your actual droplet IP address."
    exit 0
else
    log_error "Found $ERRORS critical issues. Please fix them before deployment."
    exit 1
fi
