@echo off@echo off

chcp 65001 >nul 2>&1REM WhatsApp Automation - Start Script (Windows)

REM WhatsApp Automation - Start Script (Windows)

REM This script will keep running and restart on errorscd /d "%~dp0"



cd /d "%~dp0"echo.

echo ============================================

echo.echo        WhatsApp Automation Bot

echo ============================================echo ============================================

echo        WhatsApp Automation Botecho.

echo ============================================

echo.REM Create required folder structure

echo Checking folder structure...

REM Create required folder structureif not exist "data" mkdir data

echo Checking folder structure...if not exist "uploads" mkdir uploads

if not exist "data" mkdir dataif not exist "uploads\images" mkdir uploads\images

if not exist "uploads" mkdir uploadsif not exist "attachments" mkdir attachments

if not exist "uploads\images" mkdir uploads\imagesif not exist "invitations" mkdir invitations

if not exist "attachments" mkdir attachmentsif not exist "whatsapp_profile" mkdir whatsapp_profile

if not exist "invitations" mkdir invitationsif not exist "static\images" mkdir static\images

if not exist "whatsapp_profile" mkdir whatsapp_profileecho Folders ready!

if not exist "static\images" mkdir static\imagesecho.

if not exist "logs" mkdir logs

echo Folders ready!REM Check if virtual environment exists

echo.if not exist "venv" (

    echo Virtual environment not found. Running setup...

REM Check if Python is installed    python setup.py

where python >nul 2>&1)

if %ERRORLEVEL% neq 0 (

    echo ERROR: Python is not installed or not in PATH!REM Activate virtual environment

    echo Please install Python from https://www.python.org/downloads/call venv\Scripts\activate.bat

    echo Make sure to check "Add Python to PATH" during installation.

    echo.REM Load environment variables

    pauseif exist .env (

    exit /b 1    for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do set %%a

))



REM Check if virtual environment existsREM Default values

if not exist "venv" (if "%HOST%"=="" set HOST=0.0.0.0

    echo Virtual environment not found. Creating...if "%PORT%"=="" set PORT=5001

    python -m venv venv

    if %ERRORLEVEL% neq 0 (echo Starting server on http://%HOST%:%PORT%

        echo ERROR: Failed to create virtual environment!echo Open your browser to: http://localhost:%PORT%

        pauseecho.

        exit /b 1

    )REM Run the application

    echo Virtual environment created!python app.py

    echo.

)pause


REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements if needed
if not exist "venv\Lib\site-packages\flask" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
    echo Dependencies installed!
    echo.
)

REM Default values
set HOST=0.0.0.0
set PORT=5001

REM Load environment variables from .env if exists
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "%%a=%%b"
    )
)

echo.
echo ============================================
echo   Server starting on http://localhost:%PORT%
echo ============================================
echo.
echo Press Ctrl+C to stop the server
echo.

:START
REM Run the application
python app.py

REM If we get here, the app crashed or was stopped
echo.
echo ============================================
echo   Server stopped or crashed!
echo ============================================
echo.
echo Press any key to restart, or Ctrl+C to exit...
pause >nul
echo Restarting server...
echo.
goto START
