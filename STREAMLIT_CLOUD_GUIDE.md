# Streamlit Cloud Deployment Guide

## 🚀 **Deploying Khmer News Classifier on Streamlit Free Tier**

### **Pre-deployment Checklist**

1. **Repository Setup**
   - ✅ All code files committed to GitHub
   - ✅ `streamlit_cloud_optimizer.py` included
   - ✅ Updated `requirements.txt` with `psutil>=5.8.0`
   - ❌ **Do NOT include** `cc.km.300.bin` (too large for GitHub/Streamlit)

2. **Memory Optimization**
   - ✅ Cloud optimizer automatically detects Streamlit Cloud
   - ✅ Creates lightweight embeddings (50K most common words)
   - ✅ Uses float16 precision to reduce memory usage
   - ✅ Compressed storage with gzip + pickle

### **Deployment Steps**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit Cloud optimizations"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `khmer_news_classifier_pro.py` as the main file

3. **First Run Behavior**
   - App will detect it's running on Streamlit Cloud
   - Will skip FastText download (too large)
   - Will show "SVM-only mode" initially
   - FastText features will be disabled gracefully

### **Cloud-Specific Features**

#### **Automatic Optimization**
```python
# The optimizer automatically:
if optimizer.is_cloud_environment():
    - Uses lightweight embeddings (50K vocab instead of 248K)
    - Compresses vectors to float16 (50% memory reduction)
    - Enables aggressive caching
    - Shows memory usage warnings
```

#### **Memory Management**
- **Memory Limit**: ~800MB (conservative for 1GB limit)
- **Model Size**: 
  - Full FastText: ~2.8GB ❌ (too large)
  - Lightweight: ~150MB ✅ (cloud-friendly)
  - SVM Model: ~13MB ✅ (always works)

#### **Fallback Strategy**
1. **Try lightweight embeddings** (created from local model)
2. **Fall back to SVM-only** if embeddings unavailable
3. **Graceful degradation** with user notifications

### **Creating Lightweight Embeddings (Local)**

If you want to pre-create lightweight embeddings:

```python
from streamlit_cloud_optimizer import StreamlitCloudOptimizer

optimizer = StreamlitCloudOptimizer()
success = optimizer.create_lightweight_embeddings(
    original_model_path="cc.km.300.bin",
    vocab_limit=50000,  # Adjust based on needs
    output_path="lightweight_embeddings.pkl.gz"
)
```

Then commit the lightweight file:
```bash
git add .streamlit_cache/lightweight_embeddings.pkl.gz
git commit -m "Add pre-built lightweight embeddings"
git push origin main
```

### **Performance Comparison**

| Feature | Local (Full) | Cloud (Lightweight) | Cloud (SVM-only) |
|---------|-------------|-------------------|------------------|
| Memory Usage | ~3GB | ~200MB | ~50MB |
| Load Time | 30-60s | 5-10s | 1-2s |
| Accuracy | 100% | ~95% | ~85% |
| Vocabulary | 248K words | 50K words | Basic features |

### **Monitoring Cloud Performance**

The app includes built-in monitoring:

- **Memory Usage**: Real-time tracking
- **Environment Detection**: Automatic cloud detection  
- **Cache Management**: Clear cache functionality
- **Performance Metrics**: Load times and accuracy

### **Troubleshooting**

#### **Memory Errors**
```
MemoryError: Unable to allocate X GB
```
**Solution**: App automatically switches to SVM-only mode

#### **Import Errors**
```
ModuleNotFoundError: No module named 'fasttext'
```
**Solution**: App gracefully handles missing dependencies

#### **Slow Loading**
```
App takes too long to load
```
**Solution**: Lightweight embeddings load much faster

### **Advanced Configuration**

#### **Custom Vocabulary Size**
```python
# In streamlit_cloud_optimizer.py
vocab_limit = 30000  # Smaller = faster, less memory
vocab_limit = 100000  # Larger = better accuracy, more memory
```

#### **Memory Threshold**
```python
# In streamlit_cloud_optimizer.py
max_memory_mb = 600  # Very conservative
max_memory_mb = 900  # More aggressive
```

### **Expected Cloud Behavior**

1. **First Launch**: 
   - Detects cloud environment
   - Shows "No FastText embeddings" warning
   - Runs in SVM-only mode
   - Still provides good classification

2. **With Pre-built Embeddings**:
   - Loads lightweight embeddings quickly
   - Shows "✅ Loaded lightweight embeddings"
   - Full functionality with reduced memory

3. **Continuous Updates**:
   - Cache persists between sessions
   - Automatic memory monitoring
   - Graceful error handling

### **Success Metrics**

✅ **App starts successfully on Streamlit Cloud**
✅ **Memory usage stays under 800MB**
✅ **Classification still works (SVM-only)**
✅ **No crashes or timeout errors**
✅ **Responsive user interface**

The cloud optimizer ensures your app works reliably on Streamlit's free tier while maintaining core functionality!
