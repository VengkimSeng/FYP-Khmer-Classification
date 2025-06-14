#!/usr/bin/env python3
"""
FastText Dependency Fix Script
=============================
This script helps resolve the scipy/gensim compatibility issues
that prevent FastText model loading.

Author: FYP Research Team
Date: June 2025
"""

import subprocess
import sys
import os
import importlib.util

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr.strip()}")
        return False

def check_package_version(package_name):
    """Check if a package is installed and return its version"""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            return None
        
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'unknown')
        return version
    except Exception:
        return None

def main():
    print("🔧 FastText Dependency Fix Script")
    print("=" * 50)
    
    # Check current versions
    print("\n📋 Checking current package versions:")
    packages_to_check = ['gensim', 'scipy', 'fasttext', 'numpy']
    
    for package in packages_to_check:
        version = check_package_version(package)
        if version:
            print(f"✅ {package}: {version}")
        else:
            print(f"❌ {package}: Not installed")
    
    # Ask user which fix method they want to use
    print("\n🛠️ Choose a fix method:")
    print("1. Update existing packages (Recommended)")
    print("2. Reinstall packages with specific versions") 
    print("3. Install fasttext alternative")
    print("4. Full clean reinstall")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            # Method 1: Update packages
            print("\n🔄 Method 1: Updating packages to compatible versions")
            
            commands = [
                ("pip install --upgrade gensim>=4.2.0,<4.4.0", "Updating gensim"),
                ("pip install --upgrade scipy>=1.7.0,<1.11.0", "Updating scipy"),
                ("pip install --upgrade numpy>=1.21.0", "Updating numpy"),
            ]
            
            for command, description in commands:
                if not run_command(command, description):
                    print("⚠️ Some packages failed to update. Try method 2.")
                    break
            break
            
        elif choice == '2':
            # Method 2: Reinstall with specific versions
            print("\n🔄 Method 2: Reinstalling packages with specific versions")
            
            # Uninstall first
            uninstall_commands = [
                ("pip uninstall -y gensim", "Uninstalling gensim"),
                ("pip uninstall -y scipy", "Uninstalling scipy"),
            ]
            
            for command, description in uninstall_commands:
                run_command(command, description)
            
            # Reinstall with specific versions
            install_commands = [
                ("pip install gensim==4.3.2", "Installing gensim 4.3.2"),
                ("pip install scipy==1.10.1", "Installing scipy 1.10.1"),
            ]
            
            for command, description in install_commands:
                if not run_command(command, description):
                    print("❌ Failed to install packages")
                    break
            break
            
        elif choice == '3':
            # Method 3: Install fasttext alternative
            print("\n🔄 Method 3: Installing fasttext alternative")
            
            if not run_command("pip install fasttext", "Installing fasttext library"):
                print("❌ Failed to install fasttext")
            break
            
        elif choice == '4':
            # Method 4: Full clean reinstall
            print("\n🔄 Method 4: Full clean reinstall")
            print("⚠️ This will uninstall and reinstall all ML packages")
            
            confirm = input("Are you sure? (y/N): ").lower()
            if confirm == 'y':
                # Uninstall all
                uninstall_packages = ['gensim', 'scipy', 'scikit-learn', 'numpy', 'fasttext']
                for package in uninstall_packages:
                    run_command(f"pip uninstall -y {package}", f"Uninstalling {package}")
                
                # Reinstall requirements
                if os.path.exists('requirements.txt'):
                    run_command("pip install -r requirements.txt", "Installing from requirements.txt")
                else:
                    # Install manually
                    packages = [
                        "numpy==1.24.3",
                        "scipy==1.10.1", 
                        "scikit-learn==1.3.0",
                        "gensim==4.3.2",
                        "fasttext==0.9.2"
                    ]
                    for package in packages:
                        run_command(f"pip install {package}", f"Installing {package}")
            break
            
        elif choice == '5':
            print("👋 Exiting without changes")
            sys.exit(0)
            
        else:
            print("❌ Invalid choice. Please enter 1-5.")
    
    print("\n🎉 Dependency fix process completed!")
    print("\nNext steps:")
    print("1. Restart your application")
    print("2. If the error persists, try deleting cc.km.300.bin and re-downloading")
    print("3. Check that the model loads successfully")
    
    # Test import
    print("\n🧪 Testing imports...")
    try:
        import gensim
        print(f"✅ gensim {gensim.__version__} imported successfully")
    except Exception as e:
        print(f"❌ gensim import failed: {e}")
    
    try:
        import scipy
        print(f"✅ scipy {scipy.__version__} imported successfully")
    except Exception as e:
        print(f"❌ scipy import failed: {e}")
    
    try:
        import fasttext
        print(f"✅ fasttext imported successfully")
    except Exception as e:
        print(f"⚠️ fasttext not available: {e}")

if __name__ == "__main__":
    main()
