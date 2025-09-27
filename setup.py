#!/usr/bin/env python3
"""
Setup script for Movie Sentiment Analysis Project
This script helps set up the project environment
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f" {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f" {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("Setting up Movie Sentiment Analysis Project")
    print("=" * 50)
    
    # Check if Python is available
    if not run_command("python --version", "Checking Python installation"):
        print(" Python is not installed or not in PATH")
        return False
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print(" Failed to install Python dependencies")
        return False
    
    # Check if Node.js is available
    if not run_command("node --version", "Checking Node.js installation"):
        print(" Node.js is not installed or not in PATH")
        return False
    
    # Install Node.js dependencies
    if not run_command("cd frontend && npm install", "Installing Node.js dependencies"):
        print(" Failed to install Node.js dependencies")
        return False
    
    print("\n" + "=" * 50)
    print(" Setup completed successfully!")
    print("\nTo run the project:")
    print("1. Start backend: cd backend && python app.py")
    print("2. Start frontend: cd frontend && npm start")
    print("3. Open http://localhost:3000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
