@echo off
chcp 65001 >nul 2>&1
REM Remove WhatsApp Bot from Windows Startup

echo.
echo ============================================
echo   Remove from Windows Startup
echo ============================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Remove VBS file (new hidden method)
if exist "%STARTUP_FOLDER%\WhatsApp Bot.vbs" (
    del "%STARTUP_FOLDER%\WhatsApp Bot.vbs"
    echo Removed WhatsApp Bot.vbs from Startup.
)

REM Remove BAT file (old method)
if exist "%STARTUP_FOLDER%\WhatsApp Bot.bat" (
    del "%STARTUP_FOLDER%\WhatsApp Bot.bat"
    echo Removed WhatsApp Bot.bat from Startup.
)

echo.
echo WhatsApp Bot will no longer start automatically.
echo.
pause
