@echo off
chcp 65001 >nul 2>&1

echo.
echo ============================================
echo   Remove WhatsApp Bot from Startup
echo ============================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

if exist "%STARTUP_FOLDER%\WhatsApp Bot.vbs" (
    del "%STARTUP_FOLDER%\WhatsApp Bot.vbs"
    echo Removed from Windows Startup.
) else (
    echo WhatsApp Bot was not in Startup.
)

echo.
pause
