@echo off
REM ByteBouncer - Administrator Launch
REM This script launches ByteBouncer with administrator privileges

echo ================================
echo ByteBouncer Administrator Launch
echo ================================

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ⚠️ Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo 🚀 Starting ByteBouncer with Administrator privileges...
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if "%VIRTUAL_ENV%"=="" (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

REM Run ByteBouncer
echo 🎯 Launching ByteBouncer as Administrator...
echo ⚠️ CAUTION: You can now delete system files - be careful!
echo.

python app.py

echo.
echo ByteBouncer closed.
pause