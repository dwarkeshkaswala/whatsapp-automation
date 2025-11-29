@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

cd /d "%~dp0"

echo.
echo ============================================
echo   WhatsApp Automation Bot - SETUP
echo ============================================
echo.

REM Create required folder structure
echo [1/5] Creating folder structure...
if not exist "data" mkdir data
if not exist "uploads" mkdir uploads
if not exist "uploads\images" mkdir uploads\images
if not exist "attachments" mkdir attachments
if not exist "invitations" mkdir invitations
if not exist "whatsapp_profile" mkdir whatsapp_profile
if not exist "static\images" mkdir static\images
if not exist "logs" mkdir logs
echo       Folders created!
echo.

REM Check if Python is installed
echo [2/5] Checking Python installation...
python --version >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo.
    echo ============================================
    echo   ERROR: Python is NOT installed!
    echo ============================================
    echo.
    echo   Please install Python from:
    echo   https://www.python.org/downloads/
    echo.
    echo   IMPORTANT: Check "Add Python to PATH"
    echo   during installation!
    echo.
    echo ============================================
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo       Found: !PYTHON_VERSION!
echo.

REM Create virtual environment
echo [3/5] Creating virtual environment...
if not exist "venv" (
    echo       Creating venv... (this may take a minute)
    python -m venv venv
    if !ERRORLEVEL! neq 0 (
        echo.
        echo ============================================
        echo   ERROR: Failed to create virtual environment!
        echo ============================================
        echo.
        pause
        exit /b 1
    )
    echo       Virtual environment created!
) else (
    echo       Virtual environment already exists!
)
echo.

REM Activate and install dependencies
echo [4/5] Installing dependencies...
echo       This may take a few minutes...
echo.
call venv\Scripts\activate.bat
if !ERRORLEVEL! neq 0 (
    echo.
    echo ============================================
    echo   ERROR: Failed to activate virtual environment!
    echo ============================================
    echo.
    pause
    exit /b 1
)

pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if !ERRORLEVEL! neq 0 (
    echo.
    echo ============================================
    echo   ERROR: Failed to install dependencies!
    echo ============================================
    echo.
    pause
    exit /b 1
)
echo.
echo       Dependencies installed!
echo.

REM Add to Windows Startup
echo [5/5] Adding to Windows Startup...
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_NAME=WhatsApp Bot.vbs"
set "CURRENT_DIR=%~dp0"

(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%CURRENT_DIR%"
echo WshShell.Run """%CURRENT_DIR%run.bat""", 0, False
) > "%STARTUP_FOLDER%\%VBS_NAME%"

if !ERRORLEVEL! equ 0 (
    echo       Added to Windows Startup!
) else (
    echo       Warning: Could not add to startup.
)
echo.

echo ============================================
echo   SETUP COMPLETE!
echo ============================================
echo.
echo   To START: Double-click run.bat
echo   To STOP:  Close the terminal or use Task Manager
echo.
echo   Bot will auto-start hidden on Windows boot.
echo   To disable: Run remove-from-startup.bat
echo.
echo ============================================
echo.

set /p START_NOW="Start the bot now? (Y/N): "
if /i "!START_NOW!"=="Y" (
    echo.
    echo Starting WhatsApp Bot...
    start "" "%~dp0run.bat"
)

echo.
echo Press any key to close this window...
pause >nul
