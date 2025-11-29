@echo off
chcp 65001 >nul 2>&1
REM Add WhatsApp Bot to Windows Startup (completely hidden)

cd /d "%~dp0"

echo.
echo ============================================
echo   Add to Windows Startup
echo ============================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_NAME=WhatsApp Bot.vbs"
set "CURRENT_DIR=%~dp0"

REM Create a VBScript to run bat file completely hidden
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%CURRENT_DIR%"
echo WshShell.Run """%CURRENT_DIR%run.bat""", 0, False
) > "%STARTUP_FOLDER%\%VBS_NAME%"

if %ERRORLEVEL% equ 0 (
    echo SUCCESS! WhatsApp Bot added to Windows Startup.
    echo.
    echo The bot will run COMPLETELY HIDDEN on startup.
    echo No window will appear!
    echo.
    echo To check if running: Open http://localhost:5001
    echo To stop: Use Task Manager to end Python process
    echo To remove from startup: run remove-from-startup.bat
) else (
    echo ERROR: Failed! Try running as Administrator.
)

echo.
pause
