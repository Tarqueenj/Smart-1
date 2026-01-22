#!/usr/bin/env python3
"""
Installation script for Hugging Face AI dependencies
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Main installation function"""
    print("🤖 Installing Hugging Face AI dependencies for SmartTriage AI...")
    print("=" * 60)
    
    # Required packages for Hugging Face integration
    packages = [
        "torch==2.1.2",
        "transformers==4.46.0", 
        "huggingface==0.26.1",
        "sentence-transformers==2.11.0",
        "accelerate==0.25.0"
    ]
    
    failed_packages = []
    
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    print("=" * 60)
    
    if failed_packages:
        print(f"❌ Installation failed for {len(failed_packages)} packages:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n⚠️ Please install these packages manually:")
        print(f"pip install {' '.join(failed_packages)}")
        sys.exit(1)
    else:
        print("✅ All Hugging Face AI dependencies installed successfully!")
        print("\n🚀 You can now run the SmartTriage AI with advanced AI analysis.")
        print("📝 The system will automatically use Hugging Face models when available.")
        print("🔄 If Hugging Face models are not available, it will fallback to keyword analysis.")

if __name__ == "__main__":
    main()
