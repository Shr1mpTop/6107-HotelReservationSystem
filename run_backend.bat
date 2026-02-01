@echo off
REM Hotel Reservation Management System - Backend API Server

echo ========================================
echo HRMS Backend API Server
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not added to the system PATH.
    echo Please install Python 3.8+ from https://python.org/
    echo.
    pause
    exit /b 1
)

REM Install dependencies
echo Checking Python dependencies...
pip install -r requirements.txt --quiet

REM Initialize database if needed
if not exist "data\hrms.db" (
    echo Initializing database...
    python src/database/init_db.py
    echo.
)

REM Start FastAPI server
echo.
echo Starting FastAPI Backend Server...
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

pause
