#!/usr/bin/env python3
"""
WhatsApp Automation - Universal Setup Script
Supports: macOS, Windows, Linux
Browsers: Chrome, Brave, Firefox, Edge

Run this script to set up everything automatically:
    python setup.py

Or with options:
    python setup.py --browser chrome
    python setup.py --headless
"""

import os
import sys
import subprocess
import platform
import shutil
import argparse
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Print application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗    ██╗██╗  ██╗ █████╗ ████████╗███████╗ █████╗ ██████╗  ║
║   ██║    ██║██║  ██║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗██╔══██╗ ║
║   ██║ █╗ ██║███████║███████║   ██║   ███████╗███████║██████╔╝ ║
║   ██║███╗██║██╔══██║██╔══██║   ██║   ╚════██║██╔══██║██╔═══╝  ║
║   ╚███╔███╔╝██║  ██║██║  ██║   ██║   ███████║██║  ██║██║      ║
║    ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝      ║
║                                                               ║
║              AUTOMATION BOT - SETUP WIZARD                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(f"{Colors.CYAN}{banner}{Colors.END}")


def log(message, level="info"):
    """Print colored log messages"""
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.WARNING,
        "error": Colors.FAIL,
    }
    symbols = {
        "info": "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error": "✗",
    }
    color = colors.get(level, Colors.BLUE)
    symbol = symbols.get(level, "•")
    print(f"{color}{symbol} {message}{Colors.END}")


def get_system_info():
    """Get system information"""
    system = platform.system()
    machine = platform.machine()
    
    log(f"Detected OS: {system} ({machine})")
    
    return {
        'system': system,
        'machine': machine,
        'is_mac': system == 'Darwin',
        'is_windows': system == 'Windows',
        'is_linux': system == 'Linux',
        'is_arm': 'arm' in machine.lower() or 'aarch' in machine.lower(),
    }


def find_python():
    """Find Python executable"""
    if sys.executable:
        return sys.executable
    
    for cmd in ['python3', 'python']:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return cmd
        except:
            continue
    
    return None


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        log(f"Python 3.8+ required. Found: {version.major}.{version.minor}", "error")
        return False
    
    log(f"Python version: {version.major}.{version.minor}.{version.micro}", "success")
    return True


def find_browsers(sys_info):
    """Find installed browsers"""
    browsers = {}
    
    if sys_info['is_mac']:
        browser_paths = {
            'chrome': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            'brave': '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
            'firefox': '/Applications/Firefox.app/Contents/MacOS/firefox',
            'edge': '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        }
    elif sys_info['is_windows']:
        browser_paths = {
            'chrome': [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe'),
            ],
            'brave': [
                r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
                r'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe',
                os.path.expandvars(r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe'),
            ],
            'firefox': [
                r'C:\Program Files\Mozilla Firefox\firefox.exe',
                r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe',
            ],
            'edge': [
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
            ],
        }
    else:  # Linux
        browser_paths = {
            'chrome': ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable'],
            'brave': ['/usr/bin/brave-browser', '/usr/bin/brave'],
            'firefox': ['/usr/bin/firefox'],
            'edge': ['/usr/bin/microsoft-edge', '/usr/bin/microsoft-edge-stable'],
        }
    
    for browser, paths in browser_paths.items():
        if isinstance(paths, str):
            paths = [paths]
        
        for path in paths:
            if os.path.exists(path):
                browsers[browser] = path
                break
    
    return browsers


def create_virtual_environment(base_dir):
    """Create Python virtual environment"""
    venv_path = os.path.join(base_dir, 'venv')
    
    if os.path.exists(venv_path):
        log("Virtual environment already exists", "info")
        return venv_path
    
    log("Creating virtual environment...")
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
        log("Virtual environment created", "success")
        return venv_path
    except subprocess.CalledProcessError as e:
        log(f"Failed to create virtual environment: {e}", "error")
        return None


def get_pip_path(venv_path, sys_info):
    """Get pip executable path"""
    if sys_info['is_windows']:
        return os.path.join(venv_path, 'Scripts', 'pip.exe')
    return os.path.join(venv_path, 'bin', 'pip')


def get_python_path(venv_path, sys_info):
    """Get Python executable path in venv"""
    if sys_info['is_windows']:
        return os.path.join(venv_path, 'Scripts', 'python.exe')
    return os.path.join(venv_path, 'bin', 'python')


def install_dependencies(venv_path, sys_info):
    """Install Python dependencies"""
    pip_path = get_pip_path(venv_path, sys_info)
    
    log("Upgrading pip...")
    subprocess.run([pip_path, 'install', '--upgrade', 'pip'], 
                   capture_output=True)
    
    log("Installing dependencies...")
    
    requirements = [
        'flask>=3.0.0',
        'selenium>=4.15.0',
        'APScheduler>=3.10.0',
        'Pillow>=10.0.0',
        'gunicorn>=21.0.0',  # Production WSGI server
        'python-dotenv>=1.0.0',  # Environment config
        'setuptools',
    ]
    
    for req in requirements:
        try:
            subprocess.run([pip_path, 'install', req], 
                          capture_output=True, check=True)
            log(f"Installed {req.split('>=')[0]}", "success")
        except subprocess.CalledProcessError:
            log(f"Failed to install {req}", "warning")
    
    return True


def create_config_file(base_dir, browsers, sys_info, args):
    """Create configuration file"""
    config_path = os.path.join(base_dir, 'config.py')
    
    # Determine default browser
    default_browser = args.browser if args.browser else None
    if not default_browser:
        for browser in ['chrome', 'brave', 'edge', 'firefox']:
            if browser in browsers:
                default_browser = browser
                break
    
    config_content = f'''"""
WhatsApp Automation Configuration
Auto-generated by setup.py
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Server Configuration
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5001))
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

# Browser Configuration
DEFAULT_BROWSER = os.environ.get('BROWSER', '{default_browser or "chrome"}')
HEADLESS = os.environ.get('HEADLESS', '{"true" if args.headless else "false"}').lower() == 'true'

# Browser Paths (auto-detected)
BROWSER_PATHS = {{
{chr(10).join(f"    '{k}': r'{v}'," for k, v in browsers.items())}
}}

# Session Configuration
SESSION_DIR = BASE_DIR / 'session'
PROFILE_DIR = BASE_DIR / 'whatsapp_profile'
UPLOAD_DIR = BASE_DIR / 'uploads'
ATTACHMENT_DIR = BASE_DIR / 'attachments'

# Create directories
for dir_path in [SESSION_DIR, PROFILE_DIR, UPLOAD_DIR, ATTACHMENT_DIR]:
    dir_path.mkdir(exist_ok=True)

# File Upload Configuration
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

# Selenium Configuration
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 30
PAGE_LOAD_TIMEOUT = 60

# WhatsApp URLs
WHATSAPP_URL = 'https://web.whatsapp.com'

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / 'whatsapp_bot.log'

# Production Settings
WORKERS = int(os.environ.get('WORKERS', 1))
THREADED = True
'''
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    log("Configuration file created", "success")
    return config_path


def create_env_file(base_dir):
    """Create .env template file"""
    env_path = os.path.join(base_dir, '.env.example')
    
    env_content = '''# WhatsApp Automation Environment Configuration
# Copy this file to .env and modify as needed

# Server Settings
HOST=0.0.0.0
PORT=5001
DEBUG=false

# Browser Settings
# Options: chrome, brave, firefox, edge
BROWSER=chrome
HEADLESS=true

# Logging
LOG_LEVEL=INFO

# Production Settings
WORKERS=1
'''
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    # Also create actual .env if it doesn't exist
    actual_env = os.path.join(base_dir, '.env')
    if not os.path.exists(actual_env):
        with open(actual_env, 'w') as f:
            f.write(env_content.replace('.env.example', '.env'))
    
    log("Environment file created", "success")


def create_run_scripts(base_dir, sys_info):
    """Create platform-specific run scripts"""
    
    # Unix script (Mac/Linux)
    run_sh = '''#!/bin/bash
# WhatsApp Automation - Start Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if running in production mode
if [ "$1" == "--production" ] || [ "$1" == "-p" ]; then
    echo "Starting in production mode..."
    gunicorn -w ${WORKERS:-1} -b ${HOST:-0.0.0.0}:${PORT:-5001} app:app
else
    echo "Starting in development mode..."
    python app.py
fi
'''
    
    # Windows batch script
    run_bat = '''@echo off
REM WhatsApp Automation - Start Script

cd /d "%~dp0"

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Load environment variables
if exist .env (
    for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do set %%a
)

REM Check if running in production mode
if "%1"=="--production" (
    echo Starting in production mode...
    gunicorn -w %WORKERS% -b %HOST%:%PORT% app:app
) else if "%1"=="-p" (
    echo Starting in production mode...
    gunicorn -w %WORKERS% -b %HOST%:%PORT% app:app
) else (
    echo Starting in development mode...
    python app.py
)
'''

    # PowerShell script
    run_ps1 = '''# WhatsApp Automation - Start Script (PowerShell)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Activate virtual environment
& .\\venv\\Scripts\\Activate.ps1

# Load environment variables
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -and $_ -notmatch '^#') {
            $name, $value = $_ -split '=', 2
            Set-Item -Path "env:$name" -Value $value
        }
    }
}

# Check if running in production mode
if ($args[0] -eq "--production" -or $args[0] -eq "-p") {
    Write-Host "Starting in production mode..."
    gunicorn -w $env:WORKERS -b "$env:HOST`:$env:PORT" app:app
} else {
    Write-Host "Starting in development mode..."
    python app.py
}
'''

    # Write scripts
    with open(os.path.join(base_dir, 'run.sh'), 'w') as f:
        f.write(run_sh)
    
    with open(os.path.join(base_dir, 'run.bat'), 'w') as f:
        f.write(run_bat)
    
    with open(os.path.join(base_dir, 'run.ps1'), 'w') as f:
        f.write(run_ps1)
    
    # Make shell script executable on Unix
    if not sys_info['is_windows']:
        os.chmod(os.path.join(base_dir, 'run.sh'), 0o755)
    
    log("Run scripts created", "success")


def create_directories(base_dir):
    """Create necessary directories"""
    dirs = ['uploads', 'attachments', 'session', 'whatsapp_profile', 'logs']
    
    for dir_name in dirs:
        dir_path = os.path.join(base_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
    
    log("Directories created", "success")


def print_summary(browsers, sys_info, base_dir):
    """Print setup summary"""
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Setup Complete!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.CYAN}Detected Browsers:{Colors.END}")
    for browser, path in browsers.items():
        print(f"  • {browser.title()}: {path}")
    
    if not browsers:
        print(f"  {Colors.WARNING}No supported browsers found!{Colors.END}")
        print(f"  Please install Chrome, Brave, Firefox, or Edge")
    
    print(f"\n{Colors.CYAN}To start the application:{Colors.END}")
    
    if sys_info['is_windows']:
        print(f"  1. Double-click {Colors.BOLD}run.bat{Colors.END}")
        print(f"     OR")
        print(f"  2. Run in terminal: {Colors.BOLD}.\\run.bat{Colors.END}")
        print(f"  3. For production: {Colors.BOLD}.\\run.bat --production{Colors.END}")
    else:
        print(f"  1. Run: {Colors.BOLD}./run.sh{Colors.END}")
        print(f"  2. For production: {Colors.BOLD}./run.sh --production{Colors.END}")
    
    print(f"\n{Colors.CYAN}Access the web interface:{Colors.END}")
    print(f"  Open in browser: {Colors.BOLD}http://localhost:5001{Colors.END}")
    
    print(f"\n{Colors.CYAN}Configuration:{Colors.END}")
    print(f"  Edit {Colors.BOLD}.env{Colors.END} to customize settings")
    print(f"  Edit {Colors.BOLD}config.py{Colors.END} for advanced options")
    
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}\n")


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description='WhatsApp Automation Setup')
    parser.add_argument('--browser', choices=['chrome', 'brave', 'firefox', 'edge'],
                       help='Preferred browser')
    parser.add_argument('--headless', action='store_true',
                       help='Run in headless mode by default')
    parser.add_argument('--skip-deps', action='store_true',
                       help='Skip dependency installation')
    args = parser.parse_args()
    
    print_banner()
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: Check system
    log("Checking system...", "info")
    sys_info = get_system_info()
    
    # Step 2: Check Python
    if not check_python_version():
        sys.exit(1)
    
    # Step 3: Find browsers
    log("Detecting installed browsers...")
    browsers = find_browsers(sys_info)
    
    if browsers:
        for browser, path in browsers.items():
            log(f"Found {browser.title()}", "success")
    else:
        log("No supported browsers found!", "warning")
    
    # Step 4: Create virtual environment
    log("Setting up Python environment...")
    venv_path = create_virtual_environment(base_dir)
    
    if not venv_path:
        log("Failed to create virtual environment", "error")
        sys.exit(1)
    
    # Step 5: Install dependencies
    if not args.skip_deps:
        install_dependencies(venv_path, sys_info)
    
    # Step 6: Create directories
    create_directories(base_dir)
    
    # Step 7: Create config files
    create_config_file(base_dir, browsers, sys_info, args)
    create_env_file(base_dir)
    
    # Step 8: Create run scripts
    create_run_scripts(base_dir, sys_info)
    
    # Step 9: Print summary
    print_summary(browsers, sys_info, base_dir)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
