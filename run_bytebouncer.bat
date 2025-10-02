@echo off
REM ByteBouncer - Activate Virtual Environment and Run App
REM This batch file activates the virtual environment and runs ByteBouncer

echo Activating ByteBouncer virtual environment...
call venv\Scripts\activate.bat

echo Starting ByteBouncer...
python app.py

pause