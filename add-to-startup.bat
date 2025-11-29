@echo off
chcp 65001 >nul 2>&1
REM Install WhatsApp Bot to Windows Startup
REM Run this once to make the bot start automatically on Windows boot

cd /d "%~dp0"

echo.
echo ============================================
echo   WhatsApp Bot - Startup Installer
echo ============================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=WhatsApp Bot.bat"
set "CURRENT_DIR=%~dp0"

REM Create a startup batch file
echo Creating startup shortcut...

(
echo @echo off
echo cd /d "%CURRENT_DIR%"
echo start "" "%CURRENT_DIR%run.bat"
) > "%STARTUP_FOLDER%\%SHORTCUT_NAME%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ============================================
    echo   SUCCESS! Bot added to Windows Startup
    echo ============================================
    echo.
    echo The WhatsApp Bot will now start automatically
    echo when Windows starts.
    echo.
    echo Startup file created at:
    echo %STARTUP_FOLDER%\%SHORTCUT_NAME%
    echo.
    echo To remove from startup, delete that file or
    echo run: remove-from-startup.bat
    echo.
) else (
    echo.
    echo ERROR: Failed to create startup shortcut!
    echo Please run this script as Administrator.
    echo.
)

pause
