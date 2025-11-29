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
import shutil
import webbrowser
from pathlib import Path

# Get the directory where this script/exe is located
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = Path(sys.executable).parent
    IS_EXE = True
else:
    # Running as script
    BASE_DIR = Path(__file__).parent
    IS_EXE = False

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

def check_for_updates():
    """Check and pull latest updates from GitHub"""
    git_dir = BASE_DIR / '.git'
    
    # Check if git is available
    git_path = shutil.which('git')
    if not git_path:
        print_info("Git not installed, skipping update check")
        print_info("Install Git from https://git-scm.com/ for auto-updates")
        return True
    
    # If not a git repo, initialize it and add remote
    if not git_dir.exists():
        print_info("Not a git repository, initializing for updates...")
        try:
            # Initialize git repo
            subprocess.run(
                [git_path, 'init'],
                cwd=str(BASE_DIR),
                capture_output=True,
                timeout=30
            )
            
            # Add remote origin
            subprocess.run(
                [git_path, 'remote', 'add', 'origin', 'https://github.com/dwarkeshkaswala/whatsapp-automation.git'],
                cwd=str(BASE_DIR),
                capture_output=True,
                timeout=30
            )
            
            # Fetch from remote
            print_info("Fetching from GitHub...")
            fetch_result = subprocess.run(
                [git_path, 'fetch', 'origin', 'main'],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if fetch_result.returncode == 0:
                # Reset to match remote
                print_info("Syncing with latest version...")
                subprocess.run(
                    [git_path, 'reset', '--hard', 'origin/main'],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    timeout=60
                )
                print_success("Repository initialized and updated!")
                return 'reinstall'
            else:
                print_error(f"Fetch failed: {fetch_result.stderr}")
                return True
                
        except Exception as e:
            print_info(f"Git initialization failed: {e}")
            return True
    
    print_info("Checking for updates from GitHub...")
    
    try:
        # Fetch latest from remote
        result = subprocess.run(
            [git_path, 'fetch', 'origin'],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Check if there are updates
        result = subprocess.run(
            [git_path, 'status', '-uno'],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if 'behind' in result.stdout.lower():
            print_info("Updates available! Pulling latest changes...")
            
            # Stash any local changes
            subprocess.run(
                [git_path, 'stash'],
                cwd=str(BASE_DIR),
                capture_output=True,
                timeout=30
            )
            
            # Pull latest
            pull_result = subprocess.run(
                [git_path, 'pull', 'origin', 'main'],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if pull_result.returncode == 0:
                print_success("Updated to latest version!")
                # Check if requirements changed
                if 'requirements.txt' in pull_result.stdout:
                    print_info("Requirements updated, will reinstall dependencies")
                    # Force reinstall by returning special value
                    return 'reinstall'
            else:
                print_error(f"Update failed: {pull_result.stderr}")
                # Try to restore stashed changes
                subprocess.run(
                    [git_path, 'stash', 'pop'],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    timeout=30
                )
        else:
            print_success("Already up to date")
        
        return True
        
    except subprocess.TimeoutExpired:
        print_error("Update check timed out")
        return True
    except Exception as e:
        print_info(f"Update check failed: {e}")
        return True

def find_python():
    """Find Python executable on the system"""
    # If running as script, use current Python
    if not IS_EXE:
        return sys.executable
    
    # If running as EXE, search for Python
    python_names = ['python', 'python3', 'py']
    
    for name in python_names:
        python_path = shutil.which(name)
        if python_path:
            # Verify it's actually Python
            try:
                result = subprocess.run(
                    [python_path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if 'Python' in (result.stdout + result.stderr):
                    return python_path
            except:
                continue
    
    # Check common Windows locations
    common_paths = [
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'Python',
        Path('C:/Python311'),
        Path('C:/Python310'),
        Path('C:/Python39'),
        Path('C:/Program Files/Python311'),
        Path('C:/Program Files/Python310'),
    ]
    
    for base_path in common_paths:
        if base_path.exists():
            for python_exe in base_path.rglob('python.exe'):
                return str(python_exe)
    
    return None

def check_python():
    """Check if Python is available"""
    python_path = find_python()
    
    if not python_path:
        print_error("Python not found!")
        print("Please install Python from https://www.python.org/downloads/")
        print("Make sure to check 'Add Python to PATH' during installation.")
        return None
    
    try:
        result = subprocess.run(
            [python_path, '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        version = result.stdout.strip() or result.stderr.strip()
        print_success(f"Python found: {version}")
        print_info(f"Location: {python_path}")
        return python_path
    except Exception as e:
        print_error(f"Python check failed: {e}")
        return None

def create_venv(python_path):
    """Create virtual environment if it doesn't exist"""
    venv_path = BASE_DIR / 'venv'
    
    if venv_path.exists():
        # Check if it's valid
        venv_python = get_venv_python()
        if venv_python.exists():
            print_success("Virtual environment exists")
            return True
        else:
            print_info("Invalid venv found, recreating...")
            shutil.rmtree(venv_path, ignore_errors=True)
    
    print_info("Creating virtual environment...")
    try:
        result = subprocess.run(
            [python_path, '-m', 'venv', str(venv_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            print_error(f"venv creation failed: {result.stderr}")
            return False
        print_success("Virtual environment created")
        return True
    except subprocess.TimeoutExpired:
        print_error("venv creation timed out")
        return False
    except Exception as e:
        print_error(f"Failed to create venv: {e}")
        return False

def get_venv_python():
    """Get path to Python in virtual environment"""
    if sys.platform == 'win32':
        return BASE_DIR / 'venv' / 'Scripts' / 'python.exe'
    else:
        return BASE_DIR / 'venv' / 'bin' / 'python'

def install_requirements(force=False):
    """Install requirements in virtual environment"""
    venv_python = get_venv_python()
    requirements_file = BASE_DIR / 'requirements.txt'
    
    if not venv_python.exists():
        print_error("Virtual environment Python not found!")
        return False
    
    if not requirements_file.exists():
        print_error("requirements.txt not found!")
        return False
    
    # Check if flask is installed (quick check) - skip if force reinstall
    if not force:
        try:
            result = subprocess.run(
                [str(venv_python), '-c', 'import flask; print("ok")'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and 'ok' in result.stdout:
                print_success("Dependencies already installed")
                return True
        except:
            pass
    
    print_info("Installing dependencies (this may take a few minutes)...")
    
    try:
        # Upgrade pip first
        print_info("Upgrading pip...")
        subprocess.run(
            [str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'],
            capture_output=True,
            timeout=120
        )
        
        # Install requirements
        print_info("Installing packages from requirements.txt...")
        result = subprocess.run(
            [str(venv_python), '-m', 'pip', 'install', '-r', str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        if result.returncode != 0:
            print_error(f"pip install failed:\n{result.stderr}")
            return False
        
        print_success("Dependencies installed")
        return True
    except subprocess.TimeoutExpired:
        print_error("Installation timed out. Try running again.")
        return False
    except Exception as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def run_server():
    """Run the Flask server"""
    venv_python = get_venv_python()
    app_file = BASE_DIR / 'app.py'
    
    if not venv_python.exists():
        print_error("Virtual environment Python not found!")
        return 1
    
    if not app_file.exists():
        print_error("app.py not found!")
        return 1
    
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
        try:
            webbrowser.open('http://localhost:5001')
        except:
            pass
        
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
    python_path = check_python()
    if not python_path:
        return False
    
    # Step 3: Create venv
    print("\n[3/4] Setting up virtual environment...")
    if not create_venv(python_path):
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
    
    # Check for updates from GitHub
    update_result = check_for_updates()
    force_reinstall = (update_result == 'reinstall')
    
    # Check if this is first run (no venv)
    venv_python = get_venv_python()
    if not venv_python.exists():
        print("First time setup detected...\n")
        if not setup():
            print("\nSetup failed!")
            print("\nPress Enter to exit...")
            input()
            return 1
    elif force_reinstall:
        # Requirements changed after update, reinstall
        print_info("Reinstalling dependencies after update...")
        if not install_requirements(force=True):
            print_error("Failed to reinstall dependencies")
    
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
                # Check for updates on restart
                update_result = check_for_updates()
                if update_result == 'reinstall':
                    print_info("Reinstalling dependencies after update...")
                    install_requirements(force=True)
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
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
