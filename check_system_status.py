#!/usr/bin/env python3
"""
System Status Check Script
==========================
This script checks the status of all dependencies and models
for the Khmer News Classifier system.

Author: FYP Research Team
Date: June 2025
"""

import os
import sys
import importlib.util
import subprocess

def check_python_version():
    """Check Python version"""
    print("🐍 Python Version Check")
    print("-" * 30)
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️ Python 3.8+ recommended")
    else:
        print("✅ Python version is compatible")
    print()

def check_package_status():
    """Check status of required packages"""
    print("📦 Package Status Check")
    print("-" * 30)
    
    required_packages = {
        'streamlit': '1.28.0',
        'numpy': '1.21.0',
        'pandas': '1.3.0',
        'scikit-learn': '1.0.0',
        'joblib': '1.1.0',
        'gensim': '4.2.0',
        'scipy': '1.7.0',
        'PyPDF2': '3.0.0',
        'unicodedata2': '15.0.0',
    }
    
    optional_packages = {
        'fasttext': '0.9.2',
        'numba': '0.56.0',
        'khmer-nltk': 'any'
    }
    
    all_good = True
    
    # Check required packages
    print("Required packages:")
    for package, min_version in required_packages.items():
        try:
            if package == 'scikit-learn':
                import sklearn
                version = sklearn.__version__
                package_name = 'sklearn'
            else:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown')
                package_name = package
            
            print(f"✅ {package_name}: {version}")
        except ImportError:
            print(f"❌ {package}: Not installed")
            all_good = False
        except Exception as e:
            print(f"⚠️ {package}: Error checking version - {e}")
            all_good = False
    
    print("\nOptional packages:")
    for package, min_version in optional_packages.items():
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {package}: {version}")
        except ImportError:
            print(f"⚠️ {package}: Not installed (optional)")
        except Exception as e:
            print(f"⚠️ {package}: Error checking version - {e}")
    
    print()
    return all_good

def check_model_files():
    """Check if model files exist"""
    print("🤖 Model Files Check")
    print("-" * 30)
    
    model_files = {
        'SVM Model': 'Demo_model/svm_model.joblib',
        'FastText Model': 'cc.km.300.bin',
        'Stop Words': 'Khmer-Stop-Word-1000.txt',
        'Metadata': 'metadata.csv'
    }
    
    all_models_present = True
    
    for name, path in model_files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 1024 * 1024:  # > 1MB
                size_str = f"{size / (1024*1024):.1f} MB"
            else:
                size_str = f"{size / 1024:.1f} KB"
            print(f"✅ {name}: Found ({size_str})")
        else:
            print(f"❌ {name}: Not found at {path}")
            all_models_present = False
    
    print()
    return all_models_present

def check_data_directories():
    """Check if data directories exist"""
    print("📁 Data Directories Check")
    print("-" * 30)
    
    directories = [
        'Demo_model',
        'FastText',
        'preprocessed_articles',
        'raw_articles'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            if os.path.isdir(directory):
                file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
                print(f"✅ {directory}: Found ({file_count} files)")
            else:
                print(f"⚠️ {directory}: Exists but is not a directory")
        else:
            print(f"❌ {directory}: Not found")
    
    print()

def check_scipy_gensim_compatibility():
    """Check specific scipy/gensim compatibility"""
    print("🔬 Scipy/Gensim Compatibility Check")
    print("-" * 30)
    
    try:
        import scipy
        import gensim
        
        print(f"✅ Scipy version: {scipy.__version__}")
        print(f"✅ Gensim version: {gensim.__version__}")
        
        # Test the specific import that was failing
        try:
            from scipy.linalg import triu
            print("✅ scipy.linalg.triu import successful")
        except ImportError as e:
            print(f"❌ scipy.linalg.triu import failed: {e}")
            print("💡 This is the source of your FastText loading error")
            
        # Test FastText model loading
        try:
            from gensim.models.fasttext import load_facebook_model
            print("✅ gensim FastText import successful")
            
            if os.path.exists('cc.km.300.bin'):
                print("🔄 Testing FastText model loading...")
                try:
                    model = load_facebook_model('cc.km.300.bin')
                    print("✅ FastText model loads successfully!")
                except Exception as e:
                    print(f"❌ FastText model loading failed: {e}")
            else:
                print("⚠️ FastText model file not found - cannot test loading")
                
        except ImportError as e:
            print(f"❌ gensim FastText import failed: {e}")
            
    except ImportError as e:
        print(f"❌ Cannot import scipy/gensim: {e}")
    
    print()

def suggest_fixes():
    """Suggest fixes based on the status"""
    print("💡 Suggested Fixes")
    print("-" * 30)
    
    print("If you see compatibility issues:")
    print("1. Run: python fix_dependencies.py")
    print("2. Or manually fix with:")
    print("   pip install gensim==4.3.2 scipy==1.10.1")
    print()
    
    print("If FastText model is missing:")
    print("1. The app will try to download it automatically")
    print("2. Or manually download from: https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.bin.gz")
    print()
    
    print("If other model files are missing:")
    print("1. Ensure you have trained your SVM model")
    print("2. Check the Demo_model directory")
    print()

def main():
    print("🔍 Khmer News Classifier - System Status Check")
    print("=" * 60)
    print()
    
    # Run all checks
    check_python_version()
    packages_ok = check_package_status()
    models_ok = check_model_files()
    check_data_directories()
    check_scipy_gensim_compatibility()
    
    # Overall status
    print("📊 Overall Status")
    print("-" * 30)
    
    if packages_ok and models_ok:
        print("✅ System appears to be ready!")
    else:
        print("⚠️ Some issues detected - see suggestions below")
    
    print()
    suggest_fixes()

if __name__ == "__main__":
    main()
