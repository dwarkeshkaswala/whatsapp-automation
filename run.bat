@echo off@echo off@echo off@echo off@echo off

cd /d "%~dp0"

python launcher.pysetlocal EnableDelayedExpansion

pause

chcp 65001 >nul 2>&1chcp 65001 >nul 2>&1



cd /d "%~dp0"REM WhatsApp Automation - Run Script (Windows)chcp 65001 >nul 2>&1REM WhatsApp Automation - Start Script (Windows)



title WhatsApp Automation BotREM Keeps running in background with auto-restart



echo.REM WhatsApp Automation - Start Script (Windows)

echo ============================================

echo   WhatsApp Automation Botcd /d "%~dp0"

echo ============================================

echo.REM This script will keep running and restart on errorscd /d "%~dp0"



REM Check if setup was donetitle WhatsApp Automation Bot

if not exist "venv" (

    echo ERROR: Setup not complete!

    echo.

    echo Please run setup.bat first.REM Check if setup was done

    echo.

    pauseif not exist "venv" (cd /d "%~dp0"echo.

    exit /b 1

)    echo Setup not complete! Running setup first...



REM Check if activate script exists    call setup.batecho ============================================

if not exist "venv\Scripts\activate.bat" (

    echo ERROR: Virtual environment is corrupted!    exit /b

    echo.

    echo Please delete the venv folder and run setup.bat again.)echo.echo        WhatsApp Automation Bot

    echo.

    pause

    exit /b 1

)REM Activate virtual environmentecho ============================================echo ============================================



REM Activate virtual environmentcall venv\Scripts\activate.bat

echo Activating virtual environment...

call venv\Scripts\activate.batecho        WhatsApp Automation Botecho.

if !ERRORLEVEL! neq 0 (

    echo ERROR: Failed to activate virtual environment!REM Default values

    echo.

    pauseset HOST=0.0.0.0echo ============================================

    exit /b 1

)set PORT=5001

echo Virtual environment activated.

echo.echo.REM Create required folder structure



REM Check if app.py existsREM Load .env if exists

if not exist "app.py" (

    echo ERROR: app.py not found!if exist .env (echo Checking folder structure...

    echo.

    echo Make sure you have all project files.    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (

    echo.

    pause        set "%%a=%%b"REM Create required folder structureif not exist "data" mkdir data

    exit /b 1

)    )



REM Default values)echo Checking folder structure...if not exist "uploads" mkdir uploads

set HOST=0.0.0.0

set PORT=5001



REM Load .env if existsecho.if not exist "data" mkdir dataif not exist "uploads\images" mkdir uploads\images

if exist .env (

    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (echo ============================================

        set "%%a=%%b"

    )echo   WhatsApp Automation Bot - RUNNINGif not exist "uploads" mkdir uploadsif not exist "attachments" mkdir attachments

)

echo ============================================

echo ============================================

echo   Server starting...echo.if not exist "uploads\images" mkdir uploads\imagesif not exist "invitations" mkdir invitations

echo   URL: http://localhost:!PORT!

echo ============================================echo   URL: http://localhost:%PORT%

echo.

echo Press Ctrl+C to stop the server.echo.if not exist "attachments" mkdir attachmentsif not exist "whatsapp_profile" mkdir whatsapp_profile

echo.

echo   Press Ctrl+C to stop

:LOOP

echo [%date% %time%] Starting server...echo ============================================if not exist "invitations" mkdir invitationsif not exist "static\images" mkdir static\images

echo.

echo.

python app.py

if not exist "whatsapp_profile" mkdir whatsapp_profileecho Folders ready!

set EXIT_CODE=!ERRORLEVEL!

echo.:LOOP

echo ============================================

echo   Server stopped! Exit code: !EXIT_CODE!python app.pyif not exist "static\images" mkdir static\imagesecho.

echo ============================================

echo.



if !EXIT_CODE! neq 0 (echo.if not exist "logs" mkdir logs

    echo There was an error running the server.

    echo Check the error message above.echo [%date% %time%] Server stopped. Restarting in 5 seconds...

    echo.

)echo Press Ctrl+C to exit completely.echo Folders ready!REM Check if virtual environment exists



echo Restarting in 5 seconds...timeout /t 5 /nobreak >nul

echo Press Ctrl+C to exit, or close this window.

echo.goto LOOPecho.if not exist "venv" (

timeout /t 5

goto LOOP

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
