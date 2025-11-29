#!/usr/bin/env python3
"""
WhatsApp Automation Bot - Windows Launcher
This script handles setup, installation, and running the bot.
Can be compiled to .exe using PyInstaller.
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

# Get the directory where this script/exe is located
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent

os.chdir(BASE_DIR)

def print_header():
    print("\n" + "=" * 50)
    print("   WhatsApp Automation Bot")
    print("=" * 50 + "\n")

def print_error(msg):
    print(f"\n[ERROR] {msg}\n")

def print_success(msg):
    print(f"[OK] {msg}")

def print_info(msg):
    print(f"[INFO] {msg}")

def create_folders():
    """Create required folder structure"""
    folders = [
        'data',
        'uploads',
        'uploads/images',
        'attachments',
        'invitations',
        'whatsapp_profile',
        'static/images',
        'logs'
    ]
    for folder in folders:
        folder_path = BASE_DIR / folder
        folder_path.mkdir(parents=True, exist_ok=True)
    print_success("Folders created")

def check_python():
    """Check if Python is available"""
    try:
        result = subprocess.run(
            [sys.executable, '--version'],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip() or result.stderr.strip()
        print_success(f"Python found: {version}")
        return True
    except Exception as e:
        print_error(f"Python not found: {e}")
        return False

def create_venv():
    """Create virtual environment if it doesn't exist"""
    venv_path = BASE_DIR / 'venv'
    
    if venv_path.exists():
        print_success("Virtual environment exists")
        return True
    
    print_info("Creating virtual environment...")
    try:
        subprocess.run(
            [sys.executable, '-m', 'venv', str(venv_path)],
            check=True
        )
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create venv: {e}")
        return False

def get_venv_python():
    """Get path to Python in virtual environment"""
    if sys.platform == 'win32':
        return BASE_DIR / 'venv' / 'Scripts' / 'python.exe'
    else:
        return BASE_DIR / 'venv' / 'bin' / 'python'

def install_requirements():
    """Install requirements in virtual environment"""
    venv_python = get_venv_python()
    requirements_file = BASE_DIR / 'requirements.txt'
    
    if not requirements_file.exists():
        print_error("requirements.txt not found!")
        return False
    
    # Check if flask is installed (quick check)
    try:
        result = subprocess.run(
            [str(venv_python), '-c', 'import flask'],
            capture_output=True
        )
        if result.returncode == 0:
            print_success("Dependencies already installed")
            return True
    except:
        pass
    
    print_info("Installing dependencies (this may take a few minutes)...")
    try:
        # Upgrade pip first
        subprocess.run(
            [str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'],
            capture_output=True
        )
        
        # Install requirements
        result = subprocess.run(
            [str(venv_python), '-m', 'pip', 'install', '-r', str(requirements_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print_error(f"pip install failed:\n{result.stderr}")
            return False
        
        print_success("Dependencies installed")
        return True
    except Exception as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def run_server():
    """Run the Flask server"""
    venv_python = get_venv_python()
    app_file = BASE_DIR / 'app.py'
    
    if not app_file.exists():
        print_error("app.py not found!")
        return False
    
    print_info("Starting server on http://localhost:5001")
    print_info("Press Ctrl+C to stop\n")
    print("-" * 50)
    
    try:
        # Run the Flask app
        process = subprocess.Popen(
            [str(venv_python), str(app_file)],
            cwd=str(BASE_DIR)
        )
        
        # Wait a bit then open browser
        time.sleep(3)
        webbrowser.open('http://localhost:5001')
        
        # Wait for process to finish
        process.wait()
        
        return process.returncode
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
        return 0
    except Exception as e:
        print_error(f"Server error: {e}")
        return 1

def setup():
    """Run full setup"""
    print_header()
    print("Running setup...\n")
    
    # Step 1: Create folders
    print("[1/4] Creating folders...")
    create_folders()
    
    # Step 2: Check Python
    print("\n[2/4] Checking Python...")
    if not check_python():
        return False
    
    # Step 3: Create venv
    print("\n[3/4] Setting up virtual environment...")
    if not create_venv():
        return False
    
    # Step 4: Install requirements
    print("\n[4/4] Installing dependencies...")
    if not install_requirements():
        return False
    
    print("\n" + "=" * 50)
    print("   SETUP COMPLETE!")
    print("=" * 50 + "\n")
    
    return True

def main():
    """Main entry point"""
    print_header()
    
    # Check if this is first run (no venv)
    venv_path = BASE_DIR / 'venv'
    if not venv_path.exists():
        print("First time setup detected...\n")
        if not setup():
            print("\nSetup failed! Press Enter to exit...")
            input()
            return 1
    
    # Run server in a loop (auto-restart on crash)
    while True:
        print("\n" + "=" * 50)
        print("   Starting WhatsApp Bot Server")
        print("=" * 50 + "\n")
        
        exit_code = run_server()
        
        print("\n" + "-" * 50)
        print(f"Server stopped with exit code: {exit_code}")
        print("-" * 50)
        
        if exit_code == 0:
            # Clean exit
            print("\nPress Enter to restart, or close window to exit...")
            try:
                input()
            except:
                break
        else:
            # Error - auto restart after delay
            print("\nServer crashed! Restarting in 5 seconds...")
            print("Press Ctrl+C to exit instead.")
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
