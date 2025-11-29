@echo off
chcp 65001 >nul 2>&1
REM WhatsApp Automation - Setup Script (Windows)
REM Run this ONCE to install everything

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
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo       Found: %PYTHON_VERSION%
echo.

REM Create virtual environment
echo [3/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create virtual environment!
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
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo       Dependencies installed!
echo.

REM Add to Windows Startup
echo [5/5] Adding to Windows Startup...
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_NAME=WhatsApp Bot.vbs"
set "CURRENT_DIR=%~dp0"

REM Create VBScript to run completely hidden (no window)
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%CURRENT_DIR%"
echo WshShell.Run """%CURRENT_DIR%run.bat""", 0, False
) > "%STARTUP_FOLDER%\%VBS_NAME%"

if %ERRORLEVEL% equ 0 (
    echo       Added to Windows Startup (hidden)!
) else (
    echo       Warning: Could not add to startup. Run as Administrator.
)
echo.

echo ============================================
echo   SETUP COMPLETE!
echo ============================================
echo.
echo   To START the bot: Double-click run.bat
echo   To STOP the bot:  Use Task Manager (end python.exe)
echo.
echo   The bot will auto-start HIDDEN when Windows boots.
echo   To disable: Run remove-from-startup.bat
echo.
echo ============================================
echo.

set /p START_NOW="Start the bot now? (Y/N): "
if /i "%START_NOW%"=="Y" (
    echo.
    echo Starting WhatsApp Bot...
    start "" "%~dp0run.bat"
)

pause
