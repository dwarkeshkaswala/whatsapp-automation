@echo off
chcp 65001 >nul 2>&1
REM Add WhatsApp Bot to Windows Startup (runs minimized)

cd /d "%~dp0"

echo.
echo ============================================
echo   Add to Windows Startup
echo ============================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=WhatsApp Bot.bat"
set "CURRENT_DIR=%~dp0"

(
echo @echo off
echo cd /d "%CURRENT_DIR%"
echo start /min "" cmd /c "%CURRENT_DIR%run.bat"
) > "%STARTUP_FOLDER%\%SHORTCUT_NAME%"

if %ERRORLEVEL% equ 0 (
    echo SUCCESS! WhatsApp Bot added to Windows Startup.
    echo.
    echo The bot will start MINIMIZED when Windows boots.
    echo.
    echo To remove: run remove-from-startup.bat
) else (
    echo ERROR: Failed! Try running as Administrator.
)

echo.
pause
