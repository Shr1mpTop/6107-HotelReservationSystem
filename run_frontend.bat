@echo off
REM Hotel Reservation Management System - Next.js Frontend Startup Script

echo ========================================
echo Hotel Reservation Management System
echo Next.js Frontend
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed or not added to the system PATH.
    echo Please install Node.js 18+ and make sure the 'node' command is available.
    echo Download from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Navigate to frontend directory
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    echo.
)

REM Start the development server
echo Starting Next.js development server...
echo Frontend will be available at: http://localhost:3000
echo Make sure the FastAPI backend is running on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

npm run dev

echo.
echo Frontend server stopped.
pause
