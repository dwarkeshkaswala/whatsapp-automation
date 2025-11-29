@echo off
chcp 65001 >nul 2>&1
REM Remove WhatsApp Bot from Windows Startup

echo.
echo ============================================
echo   WhatsApp Bot - Remove from Startup
echo ============================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=WhatsApp Bot.bat"

if exist "%STARTUP_FOLDER%\%SHORTCUT_NAME%" (
    del "%STARTUP_FOLDER%\%SHORTCUT_NAME%"
    echo WhatsApp Bot removed from Windows Startup.
    echo.
) else (
    echo WhatsApp Bot was not in Windows Startup.
    echo.
)

pause
