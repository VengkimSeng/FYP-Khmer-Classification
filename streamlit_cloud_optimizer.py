#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit Cloud Optimizer
========================
Optimizations for running Khmer News Classifier on Streamlit Community Cloud

This module provides:
1. Memory-efficient model loading
2. Model compression and caching
3. Fallback mechanisms for resource constraints
4. Progressive loading strategies
"""

import os
import json
import pickle
import gzip
import streamlit as st
from typing import Optional, Dict, Any
import numpy as np
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamlitCloudOptimizer:
    """Optimizes models and resources for Streamlit Community Cloud"""
    
    def __init__(self, cache_dir: str = ".streamlit_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_memory_mb = 800  # Conservative limit for free tier
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def is_cloud_environment(self) -> bool:
        """Detect if running on Streamlit Cloud"""
        return (
            os.getenv('STREAMLIT_SHARING_MODE') is not None or
            os.getenv('STREAMLIT_CLOUD') is not None or
            'streamlit.app' in os.getenv('HOSTNAME', '') or
            os.path.exists('/app')  # Common cloud indicator
        )
    
    def create_lightweight_embeddings(self, original_model_path: str, 
                                    vocab_limit: int = 50000,
                                    output_path: str = "lightweight_embeddings.pkl.gz") -> bool:
        """Create a lightweight version of FastText embeddings"""
        try:
            st.info("🔄 Creating lightweight embeddings for cloud deployment...")
            
            # Try loading with gensim first
            try:
                from gensim.models.fasttext import load_facebook_model
                model = load_facebook_model(original_model_path)
                
                # Get most common Khmer words
                vocab_items = list(model.wv.key_to_index.items())
                # Sort by frequency (assuming lower index = higher frequency)
                vocab_items = sorted(vocab_items, key=lambda x: x[1])[:vocab_limit]
                
                # Create lightweight embedding dict
                lightweight_embeddings = {
                    'vectors': {},
                    'dimension': model.wv.vector_size,
                    'vocab_size': len(vocab_items)
                }
                
                progress_bar = st.progress(0)
                for i, (word, _) in enumerate(vocab_items):
                    lightweight_embeddings['vectors'][word] = model.wv[word].astype(np.float16)  # Use float16 to save memory
                    if i % 1000 == 0:
                        progress_bar.progress(i / len(vocab_items))
                
                # Save compressed
                output_file = self.cache_dir / output_path
                with gzip.open(output_file, 'wb') as f:
                    pickle.dump(lightweight_embeddings, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                file_size_mb = output_file.stat().st_size / 1024 / 1024
                st.success(f"✅ Lightweight embeddings created: {file_size_mb:.1f}MB")
                return True
                
            except Exception as e:
                logger.error(f"Failed to create lightweight embeddings: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error in create_lightweight_embeddings: {e}")
            return False
    
    def load_lightweight_embeddings(self, embeddings_path: str = "lightweight_embeddings.pkl.gz") -> Optional[Dict]:
        """Load lightweight embeddings from cache"""
        cache_file = self.cache_dir / embeddings_path
        
        if not cache_file.exists():
            return None
            
        try:
            with gzip.open(cache_file, 'rb') as f:
                embeddings = pickle.load(f)
            
            st.success(f"✅ Loaded lightweight embeddings: {embeddings['vocab_size']} words, {embeddings['dimension']}D")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to load lightweight embeddings: {e}")
            return None
    
    def get_word_embedding(self, word: str, embeddings: Dict) -> Optional[np.ndarray]:
        """Get word embedding from lightweight embeddings"""
        if embeddings and word in embeddings['vectors']:
            return embeddings['vectors'][word].astype(np.float32)
        return None
    
    def text_to_vector(self, text: str, embeddings: Dict) -> np.ndarray:
        """Convert text to vector using lightweight embeddings"""
        if not embeddings:
            return np.zeros(300)  # Default dimension
        
        words = text.split()
        vectors = []
        
        for word in words:
            vec = self.get_word_embedding(word, embeddings)
            if vec is not None:
                vectors.append(vec)
        
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return np.zeros(embeddings['dimension'])

@st.cache_resource
def get_cloud_optimizer():
    """Get cached cloud optimizer instance"""
    return StreamlitCloudOptimizer()

@st.cache_resource
def load_cloud_optimized_fasttext():
    """Load FastText model optimized for Streamlit Cloud"""
    optimizer = get_cloud_optimizer()
    
    # Check if we're on cloud
    if optimizer.is_cloud_environment():
        st.info("🌤️ Detected Streamlit Cloud environment - using optimized loading")
        
        # Try to load lightweight embeddings first
        embeddings = optimizer.load_lightweight_embeddings()
        if embeddings:
            return {'type': 'lightweight', 'model': embeddings}
        
        # If lightweight doesn't exist, check if full model is available
        if os.path.exists('cc.km.300.bin'):
            st.warning("⚠️ Full FastText model found but may exceed memory limits")
            
            # Create lightweight version
            if optimizer.create_lightweight_embeddings('cc.km.300.bin'):
                embeddings = optimizer.load_lightweight_embeddings()
                if embeddings:
                    return {'type': 'lightweight', 'model': embeddings}
        
        # Fallback: No embeddings available
        st.warning("⚠️ No FastText embeddings available - using SVM-only mode")
        return {'type': 'none', 'model': None}
    
    else:
        # Local development - use full model
        st.info("💻 Local environment detected - loading full FastText model")
        try:
            from gensim.models.fasttext import load_facebook_model
            model = load_facebook_model('cc.km.300.bin')
            return {'type': 'full', 'model': model}
        except Exception as e:
            st.error(f"Failed to load full model: {e}")
            return {'type': 'none', 'model': None}

def get_text_features_cloud_optimized(text: str, fasttext_result: Dict) -> np.ndarray:
    """Extract text features optimized for cloud deployment"""
    if fasttext_result['type'] == 'full':
        # Use full model
        model = fasttext_result['model']
        words = text.split()
        vectors = [model.wv[word] for word in words if word in model.wv]
        return np.mean(vectors, axis=0) if vectors else np.zeros(300)
    
    elif fasttext_result['type'] == 'lightweight':
        # Use lightweight embeddings
        optimizer = get_cloud_optimizer()
        return optimizer.text_to_vector(text, fasttext_result['model'])
    
    else:
        # No embeddings - return zero vector (SVM will use other features)
        return np.zeros(300)

def show_cloud_optimization_info():
    """Show information about cloud optimizations"""
    optimizer = get_cloud_optimizer()
    
    with st.expander("☁️ Cloud Optimization Info", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Environment", 
                     "☁️ Cloud" if optimizer.is_cloud_environment() else "💻 Local")
            
            memory_usage = optimizer.get_memory_usage()
            if memory_usage > 0:
                st.metric("Memory Usage", f"{memory_usage:.1f} MB")
                
                if memory_usage > optimizer.max_memory_mb:
                    st.warning(f"⚠️ Memory usage exceeds recommended limit ({optimizer.max_memory_mb}MB)")
        
        with col2:
            cache_files = list(optimizer.cache_dir.glob("*"))
            st.metric("Cache Files", len(cache_files))
            
            if cache_files:
                total_size = sum(f.stat().st_size for f in cache_files) / 1024 / 1024
                st.metric("Cache Size", f"{total_size:.1f} MB")
        
        if st.button("🗑️ Clear Cache"):
            import shutil
            shutil.rmtree(optimizer.cache_dir, ignore_errors=True)
            optimizer.cache_dir.mkdir(exist_ok=True)
            st.success("Cache cleared! Please restart the app.")

# Export key functions
__all__ = [
    'StreamlitCloudOptimizer',
    'get_cloud_optimizer', 
    'load_cloud_optimized_fasttext',
    'get_text_features_cloud_optimized',
    'show_cloud_optimization_info'
]
