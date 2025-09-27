#!/usr/bin/env python3
"""
Installation script for word cloud dependencies
Run this script to install the required packages for word cloud functionality
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install all required packages"""
    print("🚀 Installing word cloud dependencies...")
    print("=" * 50)
    
    packages = [
        "wordcloud==1.9.2",
        "Pillow==10.0.1"
    ]
    
    success_count = 0
    for package in packages:
        print(f"\n📦 Installing {package}...")
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Installation Summary: {success_count}/{len(packages)} packages installed successfully")
    
    if success_count == len(packages):
        print("🎉 All dependencies installed successfully!")
        print("You can now run your application with word cloud functionality.")
    else:
        print("⚠️ Some packages failed to install. Please check the errors above.")
    
    return success_count == len(packages)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
