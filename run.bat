@echo off
REM WhatsApp Automation - Start Script (Windows)

cd /d "%~dp0"

echo.
echo ============================================
echo        WhatsApp Automation Bot
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Running setup...
    python setup.py
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Load environment variables
if exist .env (
    for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do set %%a
)

REM Default values
if "%HOST%"=="" set HOST=0.0.0.0
if "%PORT%"=="" set PORT=5001

echo Starting server on http://%HOST%:%PORT%
echo Open your browser to: http://localhost:%PORT%
echo.

REM Run the application
python app.py

pause
