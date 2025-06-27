# Khmer News Classifier - Development & Hosting Guide

This guide explains how to run the Khmer News Classifier in both development and production modes.

## 📋 Requirements

### System Requirements
- Python 3.8+ (recommended: 3.9 or 3.10)
- 8GB+ RAM (for optimal performance with FastText embeddings)
- 2GB+ available disk space

### Required Files
Ensure you have these files in your project directory:
```
khmer_news_classifier_pro.py    # Main application
requirements.txt                # Dependencies
Demo_model/
  ├── svm_model.joblib          # Trained SVM model
  ├── config.json               # Model configuration
  ├── X_train_fasttext.joblib   # Training features (optional)
  ├── X_test_fasttext.joblib    # Test features (optional)
  ├── y_train_fasttext.joblib   # Training labels (optional)
  └── y_test_fasttext.joblib    # Test labels (optional)
cc.km.300.bin                   # FastText model (optional, ~1.2GB)
```

## 🚀 Development Mode

### Quick Start (Recommended)
```bash
# Make the script executable (first time only)
chmod +x run_dev.sh

# Start development server
./run_dev.sh

# Optional: specify custom port and host
./run_dev.sh 8502 localhost
```

### Manual Development Setup
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Set development environment variables
export STREAMLIT_DEBUG=true
export STREAMLIT_SERVER_RUN_ON_SAVE=true
export STREAMLIT_SERVER_HEADLESS=false

# 4. Start development server
streamlit run khmer_news_classifier_pro.py \
    --server.port=8501 \
    --server.address=localhost \
    --server.headless=false \
    --server.runOnSave=true \
    --server.allowRunOnSave=true \
    --client.showErrorDetails=true \
    --client.toolbarMode=developer
```

### Development Features
- **Auto-reload**: Changes to code automatically reload the app
- **Debug mode**: Detailed error messages and stack traces
- **Development indicators**: Visual indicators showing dev mode is active
- **Cache management**: Tools to clear cache and force reload
- **System monitoring**: RAM usage and performance metrics
- **Model information**: Detailed model loading and configuration info

## 🌐 Production/Hosting Mode

### Quick Start
```bash
# Make the script executable (first time only)
chmod +x run_prod.sh

# Start production server
./run_prod.sh
```

### Manual Production Setup
```bash
# 1. Set production environment variables
export STREAMLIT_DEBUG=false
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 2. Start production server
streamlit run khmer_news_classifier_pro.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.runOnSave=false \
    --client.showErrorDetails=false \
    --client.toolbarMode=minimal
```

### Deployment with GitHub
```bash
# Deploy to server
./deploy_from_github.sh username/repository server_ip root

# Upload SSL certificates (optional)
./upload_ssl_certs.sh server_ip root
```

## 🔧 Configuration Options

### Environment Variables
```bash
# Development/Production Mode
STREAMLIT_DEBUG=true/false              # Enable/disable dev mode
STREAMLIT_SERVER_HEADLESS=false/true    # Show/hide browser UI
STREAMLIT_SERVER_RUN_ON_SAVE=true/false # Auto-reload on changes

# Server Configuration
STREAMLIT_PORT=8501                     # Server port
STREAMLIT_HOST=localhost               # Server host
STREAMLIT_GLOBAL_LOG_LEVEL=info        # Logging level

# Performance
PYTHONHASHSEED=0                       # Reproducible results
```

### Application Configuration
The app automatically detects the mode based on environment variables:
- **Development Mode**: `STREAMLIT_DEBUG=true` (default)
- **Production Mode**: `STREAMLIT_DEBUG=false`

## 📱 Accessing the Application

### Development
- **Local**: http://localhost:8501
- **Custom port**: http://localhost:YOUR_PORT
- **Network**: http://YOUR_IP:8501 (if accessible)

### Production/Hosting
- **HTTP**: http://your-server-ip:8501
- **HTTPS**: https://your-domain.com (with SSL)
- **Behind proxy**: Configure nginx/apache accordingly

## 🛠️ Development Tools

### Available in Development Mode
1. **Development Banner**: Visual indicator at the top
2. **Debug Information**: Detailed error messages
3. **Cache Controls**: Clear cache buttons in sidebar
4. **System Monitoring**: RAM usage and performance metrics
5. **Model Information**: Detailed model loading info
6. **Quick Actions**: Force reload and cache management

### Debugging
```bash
# View Streamlit logs
streamlit run khmer_news_classifier_pro.py --global.logLevel=debug

# Check system resources
top -p $(pgrep -f streamlit)

# Monitor memory usage
watch -n 1 'ps aux | grep streamlit'
```

## 🔍 Troubleshooting

### Common Issues

#### Models Not Loading
```bash
# Check file permissions
ls -la Demo_model/
ls -la cc.km.300.bin

# Verify file integrity
python -c "import joblib; print(joblib.load('Demo_model/svm_model.joblib'))"
```

#### Memory Issues
```bash
# Monitor memory usage
free -h
ps aux --sort=-%mem | head

# Reduce memory usage
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200  # MB
```

#### Port Already in Use
```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 $(lsof -t -i:8501)

# Use different port
./run_dev.sh 8502
```

#### Permission Errors
```bash
# Fix script permissions
chmod +x run_dev.sh run_prod.sh

# Fix file permissions
chmod 644 requirements.txt
chmod 755 Demo_model/
```

## 📊 Performance Optimization

### For 8GB RAM Systems
The application is optimized for 8GB RAM with:
- Model caching at startup
- Word embedding caching
- Memory management optimizations
- Garbage collection tuning

### Memory Management
```python
# Clear cache if memory is low
st.cache_resource.clear()
classification_engine.clear_cache()
gc.collect()
```

## 🔐 Security Considerations

### Development Mode
- **Never use in production** with debug mode enabled
- Only bind to localhost (127.0.0.1) for security
- Disable in production environments

### Production Mode
- Use HTTPS with SSL certificates
- Configure proper firewall rules
- Use reverse proxy (nginx/apache)
- Regular security updates

## 📈 Monitoring

### Application Health
- Check application status via HTTP endpoint
- Monitor memory and CPU usage
- Log analysis for errors and performance

### System Commands
```bash
# Check service status (systemd)
systemctl status khmer-classifier

# View logs
journalctl -u khmer-classifier -f

# Restart service
systemctl restart khmer-classifier
```

## 🤝 Support

For issues or questions:
1. Check this documentation
2. Review error logs
3. Verify system requirements
4. Check file permissions and paths
5. Ensure all dependencies are installed

### Development vs Production Summary
| Feature | Development | Production |
|---------|-------------|------------|
| Auto-reload | ✅ Enabled | ❌ Disabled |
| Debug info | ✅ Detailed | ❌ Minimal |
| Error details | ✅ Full stack | ❌ User-friendly |
| Performance | 🔶 Debug overhead | ✅ Optimized |
| Security | 🔶 Local only | ✅ Production-ready |
| Monitoring | ✅ Built-in tools | 🔶 External tools |
