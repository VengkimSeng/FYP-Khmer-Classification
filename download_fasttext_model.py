#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastText Model Downloader for Khmer Language
============================================

This module provides functionality to download and extract the FastText model
for Khmer language (cc.km.300.bin) from Facebook's official pre-trained models.

The model is approximately 2.8GB and will be downloaded from:
https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.bin.gz

Author: FYP Research Team
Version: 1.0.0
Date: June 14, 2025
License: Academic Research Use
"""

import os
import gzip
import shutil
import urllib.request
import urllib.error
from typing import Optional, Callable
import hashlib
import time

class FastTextModelDownloader:
    """Handles downloading and extracting FastText Khmer model"""
    
    # Official FastText model URL
    FASTTEXT_URL = "https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.km.300.bin.gz"
    MODEL_GZ_FILENAME = "cc.km.300.bin.gz"
    MODEL_FILENAME = "cc.km.300.bin"
    
    # Expected file sizes (approximate)
    EXPECTED_GZ_SIZE = 2800000000  # ~2.8GB compressed
    EXPECTED_BIN_SIZE = 7000000000  # ~7GB uncompressed
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the downloader
        
        Args:
            base_dir: Directory where the model should be downloaded. 
                     Defaults to current working directory.
        """
        self.base_dir = base_dir or os.getcwd()
        self.gz_path = os.path.join(self.base_dir, self.MODEL_GZ_FILENAME)
        self.bin_path = os.path.join(self.base_dir, self.MODEL_FILENAME)
    
    def model_exists(self) -> bool:
        """Check if the FastText model already exists"""
        return os.path.exists(self.bin_path) and os.path.getsize(self.bin_path) > 0
    
    def download_model(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        Download the FastText model
        
        Args:
            progress_callback: Optional callback function for progress updates.
                             Should accept (downloaded_bytes, total_bytes) as arguments.
        
        Returns:
            True if download successful, False otherwise
        """
        if self.model_exists():
            print(f"✅ FastText model already exists at: {self.bin_path}")
            return True
        
        print(f"📥 Downloading FastText Khmer model...")
        print(f"   URL: {self.FASTTEXT_URL}")
        print(f"   Destination: {self.gz_path}")
        print(f"   Expected size: ~{self.EXPECTED_GZ_SIZE / (1024**3):.1f}GB")
        print("   This may take several minutes depending on your internet connection...")
        
        try:
            # Create custom opener with progress tracking
            def progress_hook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(100.0, (downloaded / total_size) * 100)
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    
                    print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}MB / {mb_total:.1f}MB)", end="", flush=True)
                    
                    if progress_callback:
                        progress_callback(downloaded, total_size)
            
            # Download the file
            urllib.request.urlretrieve(self.FASTTEXT_URL, self.gz_path, progress_hook)
            print(f"\n✅ Download completed: {self.gz_path}")
            
            # Verify download
            if not os.path.exists(self.gz_path):
                print("❌ Download failed: File not found after download")
                return False
            
            file_size = os.path.getsize(self.gz_path)
            print(f"   Downloaded file size: {file_size / (1024**3):.2f}GB")
            
            # Basic size validation
            if file_size < (self.EXPECTED_GZ_SIZE * 0.8):  # Allow 20% variance
                print("⚠️ Warning: Downloaded file size seems too small")
            
            return True
            
        except urllib.error.URLError as e:
            print(f"❌ Network error during download: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during download: {e}")
            return False
    
    def extract_model(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        Extract the downloaded gzipped model
        
        Args:
            progress_callback: Optional callback function for progress updates.
                             Should accept (processed_bytes, total_bytes) as arguments.
        
        Returns:
            True if extraction successful, False otherwise
        """
        if not os.path.exists(self.gz_path):
            print(f"❌ Compressed file not found: {self.gz_path}")
            return False
        
        if self.model_exists():
            print(f"✅ Model already extracted at: {self.bin_path}")
            return True
        
        print(f"📦 Extracting FastText model...")
        print(f"   Source: {self.gz_path}")
        print(f"   Destination: {self.bin_path}")
        
        try:
            # Get total size for progress tracking
            total_size = os.path.getsize(self.gz_path)
            processed_size = 0
            
            with gzip.open(self.gz_path, 'rb') as gz_file:
                with open(self.bin_path, 'wb') as bin_file:
                    chunk_size = 1024 * 1024  # 1MB chunks
                    
                    while True:
                        chunk = gz_file.read(chunk_size)
                        if not chunk:
                            break
                        
                        bin_file.write(chunk)
                        processed_size += len(chunk)
                        
                        # Progress update
                        if total_size > 0:
                            percent = min(100.0, (processed_size / total_size) * 100)
                            mb_processed = processed_size / (1024 * 1024)
                            print(f"\r   Extraction progress: {percent:.1f}% ({mb_processed:.1f}MB processed)", end="", flush=True)
                            
                            if progress_callback:
                                progress_callback(processed_size, total_size)
            
            print(f"\n✅ Extraction completed: {self.bin_path}")
            
            # Verify extraction
            if not os.path.exists(self.bin_path):
                print("❌ Extraction failed: File not found after extraction")
                return False
            
            extracted_size = os.path.getsize(self.bin_path)
            print(f"   Extracted file size: {extracted_size / (1024**3):.2f}GB")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during extraction: {e}")
            return False
    
    def cleanup_gz_file(self) -> bool:
        """
        Remove the compressed .gz file after successful extraction
        
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            if os.path.exists(self.gz_path):
                os.remove(self.gz_path)
                print(f"🗑️ Cleaned up compressed file: {self.gz_path}")
                return True
            return True
        except Exception as e:
            print(f"⚠️ Warning: Could not remove compressed file: {e}")
            return False
    
    def download_and_extract(self, cleanup: bool = True, 
                           progress_callback: Optional[Callable[[int, int], None]] = None) -> bool:
        """
        Complete download and extraction process
        
        Args:
            cleanup: Whether to remove the .gz file after extraction
            progress_callback: Optional callback function for progress updates
        
        Returns:
            True if entire process successful, False otherwise
        """
        print("🚀 Starting FastText Khmer model download and extraction process...")
        print("="*70)
        
        # Check if model already exists
        if self.model_exists():
            print(f"✅ FastText model already available at: {self.bin_path}")
            return True
        
        # Step 1: Download
        print("\n📥 Step 1: Downloading compressed model...")
        if not self.download_model(progress_callback):
            print("❌ Download failed. Cannot proceed with extraction.")
            return False
        
        # Step 2: Extract
        print("\n📦 Step 2: Extracting model...")
        if not self.extract_model(progress_callback):
            print("❌ Extraction failed.")
            return False
        
        # Step 3: Cleanup (optional)
        if cleanup:
            print("\n🗑️ Step 3: Cleaning up...")
            self.cleanup_gz_file()
        
        print("\n🎉 FastText model setup completed successfully!")
        print(f"   Model location: {self.bin_path}")
        print("="*70)
        
        return True

def download_fasttext_model(base_dir: str = None, cleanup: bool = True) -> bool:
    """
    Convenience function to download and extract FastText Khmer model
    
    Args:
        base_dir: Directory where the model should be downloaded. 
                 Defaults to current working directory.
        cleanup: Whether to remove the .gz file after extraction
    
    Returns:
        True if successful, False otherwise
    """
    downloader = FastTextModelDownloader(base_dir)
    return downloader.download_and_extract(cleanup=cleanup)

def check_fasttext_model(base_dir: str = None) -> bool:
    """
    Check if FastText model exists
    
    Args:
        base_dir: Directory to check for the model.
                 Defaults to current working directory.
    
    Returns:
        True if model exists, False otherwise
    """
    downloader = FastTextModelDownloader(base_dir)
    return downloader.model_exists()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download FastText Khmer model")
    parser.add_argument("--dir", "-d", default=".", 
                       help="Directory to download the model (default: current directory)")
    parser.add_argument("--no-cleanup", action="store_true",
                       help="Keep the compressed .gz file after extraction")
    
    args = parser.parse_args()
    
    # Run the download
    success = download_fasttext_model(
        base_dir=args.dir,
        cleanup=not args.no_cleanup
    )
    
    if success:
        print("\n✅ FastText model is ready for use!")
        exit(0)
    else:
        print("\n❌ Failed to setup FastText model.")
        exit(1)
