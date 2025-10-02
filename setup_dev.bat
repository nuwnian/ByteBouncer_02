@echo off
REM ByteBouncer - Development Environment Setup
REM This script sets up the complete development environment

echo ================================
echo ByteBouncer Development Setup
echo ================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies!
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Run tests
echo Running tests...
python test_app.py
if errorlevel 1 (
    echo Tests failed!
    pause
    exit /b 1
)

echo ================================
echo ✅ Setup Complete!
echo ================================
echo.
echo To run ByteBouncer:
echo   1. run_bytebouncer.bat  (Easy launch)
echo   2. Or manually:
echo      - venv\Scripts\activate
echo      - python app.py
echo.
pause