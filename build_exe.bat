@echo off
chcp 65001 >nul 2>&1
echo.
echo ============================================
echo   Building WhatsApp Bot Launcher EXE
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python first.
    pause
    exit /b 1
)

REM Install PyInstaller if not installed
echo Installing PyInstaller...
pip install pyinstaller >nul 2>&1

REM Build the exe
echo.
echo Building executable...
echo This may take a few minutes...
echo.

pyinstaller --onefile --name "WhatsApp Bot" --icon=NONE --console launcher.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ============================================
    echo   BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo   EXE file created at:
    echo   dist\WhatsApp Bot.exe
    echo.
    echo   Copy "WhatsApp Bot.exe" to your project folder
    echo   and double-click to run!
    echo.
) else (
    echo.
    echo BUILD FAILED!
    echo.
)

pause
