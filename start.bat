@echo off
REM Hotel Reservation Management System - Full Stack Startup

echo ========================================
echo Hotel Reservation Management System
echo Full Stack Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8+ from https://python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo All prerequisites are installed.
echo.
echo Starting Backend Server...
start "HRMS Backend" cmd /k "%~dp0run_backend.bat"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo Starting Frontend Server...
start "HRMS Frontend" cmd /k "%~dp0run_frontend.bat"

echo.
echo ========================================
echo System Started Successfully!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo ========================================
