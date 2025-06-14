#!/usr/bin/env python3
"""
Test script for Khmer News Classifier
"""

import sys
import os

def test_imports():
    """Test if all necessary modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import joblib
        print("✅ Joblib imported successfully")
    except ImportError as e:
        print(f"❌ Joblib import failed: {e}")
        return False
    
    try:
        from gensim.models.fasttext import load_facebook_model
        print("✅ Gensim FastText imported successfully")
    except ImportError as e:
        print(f"❌ Gensim import failed: {e}")
        return False
    
    return True

def test_files():
    """Test if required files exist"""
    print("\nTesting file existence...")
    
    required_files = [
        "cc.km.300.bin",
        "Demo_model/svm_model.joblib",
        "download_fasttext_model.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_model_loading():
    """Test if models can be loaded"""
    print("\nTesting model loading...")
    
    try:
        # Test SVM model loading
        import joblib
        svm_model = joblib.load("Demo_model/svm_model.joblib")
        print("✅ SVM model loaded successfully")
    except Exception as e:
        print(f"❌ SVM model loading failed: {e}")
        return False
    
    try:
        # Test FastText model loading
        from gensim.models.fasttext import load_facebook_model
        fasttext_model = load_facebook_model("cc.km.300.bin")
        print("✅ FastText model loaded successfully")
        
        # Test model functionality
        if hasattr(fasttext_model, 'get_word_vector'):
            vec = fasttext_model.get_word_vector("test")
            print(f"✅ FastText vector generation works (dimension: {len(vec)})")
        else:
            print("⚠️ FastText model API may be different")
        
    except Exception as e:
        print(f"❌ FastText model loading failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Khmer News Classifier - Dependency Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Files
    if test_files():
        tests_passed += 1
    
    # Test 3: Model Loading
    if test_model_loading():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The application should work correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please address the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
