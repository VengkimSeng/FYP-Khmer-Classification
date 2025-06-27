#!/usr/bin/env python3
"""
Khmer News Classifier - Dependency and Setup Validator
This script validates that all required dependencies and files are properly installed and configured.
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_dependencies():
    """Check if all required Python packages are installed"""
    print("\n📦 Checking Python dependencies...")
    
    required_packages = [
        'streamlit',
        'numpy',
        'pandas', 
        'scikit-learn',
        'scipy',
        'joblib',
        'gensim',
        'PyPDF2'
    ]
    
    optional_packages = [
        'psutil',
        'watchdog'
    ]
    
    all_good = True
    
    # Check required packages
    for package in required_packages:
        try:
            # Handle sklearn package name difference
            import_name = package
            if package == 'scikit-learn':
                import_name = 'sklearn'
            
            module = importlib.import_module(import_name.replace('-', '_'))
            version = getattr(module, '__version__', 'unknown')
            print(f"   ✅ {package} - {version}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            all_good = False
    
    # Check optional packages
    print("\n📦 Checking optional dependencies...")
    for package in optional_packages:
        try:
            module = importlib.import_module(package.replace('-', '_'))
            version = getattr(module, '__version__', 'unknown')
            print(f"   ✅ {package} - {version}")
        except ImportError:
            print(f"   ⚠️  {package} - Not installed (optional)")
    
    return all_good

def check_model_files():
    """Check if required model files exist"""
    print("\n🤖 Checking model files...")
    
    required_files = [
        'Demo_model/svm_model.joblib',
        'Demo_model/config.json'
    ]
    
    optional_files = [
        'cc.km.300.bin',
        'Demo_model/X_train_fasttext.joblib',
        'Demo_model/X_test_fasttext.joblib',
        'Demo_model/y_train_fasttext.joblib',
        'Demo_model/y_test_fasttext.joblib'
    ]
    
    all_good = True
    
    # Check required files
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            print(f"   ✅ {file_path} - {size_mb:.1f} MB")
        else:
            print(f"   ❌ {file_path} - NOT FOUND")
            all_good = False
    
    # Check optional files
    for file_path in optional_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            print(f"   ✅ {file_path} - {size_mb:.1f} MB")
        else:
            print(f"   ⚠️  {file_path} - Not found (optional)")
    
    return all_good

def check_scripts():
    """Check if development scripts are executable"""
    print("\n🔧 Checking development scripts...")
    
    scripts = [
        'run_dev.sh',
        'run_prod.sh',
        'deploy_from_github.sh',
        'upload_ssl_certs.sh'
    ]
    
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"   ✅ {script} - Executable")
            else:
                print(f"   ⚠️  {script} - Not executable (run: chmod +x {script})")
        else:
            print(f"   ❌ {script} - Not found")

def check_config_files():
    """Check configuration files"""
    print("\n⚙️  Checking configuration files...")
    
    config_files = [
        'requirements.txt',
        'DEVELOPMENT_GUIDE.md',
        'SSL_CERTIFICATE_MANAGEMENT.md',
        '.gitignore'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   ✅ {config_file}")
        else:
            print(f"   ❌ {config_file} - Not found")

def test_model_loading():
    """Test if models can be loaded successfully"""
    print("\n🧪 Testing model loading...")
    
    try:
        # Test SVM model
        import joblib
        svm_model = joblib.load('Demo_model/svm_model.joblib')
        print(f"   ✅ SVM model loaded - {type(svm_model).__name__}")
        
        # Test config
        import json
        with open('Demo_model/config.json', 'r') as f:
            config = json.load(f)
        print(f"   ✅ Config loaded - {len(config)} parameters")
        
        # Test FastText (optional)
        if os.path.exists('cc.km.300.bin'):
            try:
                from gensim.models.fasttext import load_facebook_model
                fasttext_model = load_facebook_model('cc.km.300.bin')
                print(f"   ✅ FastText model loaded - {len(fasttext_model.wv)} words")
            except Exception as e:
                print(f"   ⚠️  FastText model issue: {e}")
        else:
            print("   ⚠️  FastText model not found - SVM only mode")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        return False

def check_memory():
    """Check available system memory"""
    print("\n💾 Checking system memory...")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        print(f"   📊 Total RAM: {total_gb:.1f} GB")
        print(f"   📊 Available RAM: {available_gb:.1f} GB")
        print(f"   📊 Memory usage: {memory.percent}%")
        
        if total_gb >= 8:
            print("   ✅ Sufficient memory for optimal performance")
        elif total_gb >= 4:
            print("   ⚠️  Limited memory - may affect performance with FastText")
        else:
            print("   ❌ Insufficient memory - consider upgrading or using SVM only")
            
    except ImportError:
        print("   ⚠️  psutil not installed - cannot check memory")

def main():
    """Run all validation checks"""
    print("🔍 Khmer News Classifier - System Validation")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_model_files(),
        test_model_loading()
    ]
    
    # Non-critical checks
    check_scripts()
    check_config_files()
    check_memory()
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 All critical checks passed! Your system is ready for development.")
        print("\n🚀 To start development mode, run:")
        print("   ./run_dev.sh")
        print("\n🌐 To start production mode, run:")
        print("   ./run_prod.sh")
    else:
        print("❌ Some critical checks failed. Please fix the issues above.")
        print("\n💡 Tips:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Ensure model files are in Demo_model/ directory")
        print("   - Check file permissions and paths")
    
    print("\n📚 For detailed setup instructions, see DEVELOPMENT_GUIDE.md")

if __name__ == "__main__":
    main()
