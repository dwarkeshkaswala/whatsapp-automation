@echo off@echo off@echo off

chcp 65001 >nul 2>&1

REM WhatsApp Automation - Run Script (Windows)chcp 65001 >nul 2>&1REM WhatsApp Automation - Start Script (Windows)

REM Keeps running in background with auto-restart

REM WhatsApp Automation - Start Script (Windows)

cd /d "%~dp0"

REM This script will keep running and restart on errorscd /d "%~dp0"

title WhatsApp Automation Bot



REM Check if setup was done

if not exist "venv" (cd /d "%~dp0"echo.

    echo Setup not complete! Running setup first...

    call setup.batecho ============================================

    exit /b

)echo.echo        WhatsApp Automation Bot



REM Activate virtual environmentecho ============================================echo ============================================

call venv\Scripts\activate.bat

echo        WhatsApp Automation Botecho.

REM Default values

set HOST=0.0.0.0echo ============================================

set PORT=5001

echo.REM Create required folder structure

REM Load .env if exists

if exist .env (echo Checking folder structure...

    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (

        set "%%a=%%b"REM Create required folder structureif not exist "data" mkdir data

    )

)echo Checking folder structure...if not exist "uploads" mkdir uploads



echo.if not exist "data" mkdir dataif not exist "uploads\images" mkdir uploads\images

echo ============================================

echo   WhatsApp Automation Bot - RUNNINGif not exist "uploads" mkdir uploadsif not exist "attachments" mkdir attachments

echo ============================================

echo.if not exist "uploads\images" mkdir uploads\imagesif not exist "invitations" mkdir invitations

echo   URL: http://localhost:%PORT%

echo.if not exist "attachments" mkdir attachmentsif not exist "whatsapp_profile" mkdir whatsapp_profile

echo   Press Ctrl+C to stop

echo ============================================if not exist "invitations" mkdir invitationsif not exist "static\images" mkdir static\images

echo.

if not exist "whatsapp_profile" mkdir whatsapp_profileecho Folders ready!

:LOOP

python app.pyif not exist "static\images" mkdir static\imagesecho.



echo.if not exist "logs" mkdir logs

echo [%date% %time%] Server stopped. Restarting in 5 seconds...

echo Press Ctrl+C to exit completely.echo Folders ready!REM Check if virtual environment exists

timeout /t 5 /nobreak >nul

goto LOOPecho.if not exist "venv" (


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
