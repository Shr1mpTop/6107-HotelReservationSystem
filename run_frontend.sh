#!/bin/bash

# Hotel Reservation Management System - Next.js Frontend Startup Script

echo "========================================"
echo "Hotel Reservation Management System"
echo "Next.js Frontend"
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null
then
    echo "Node.js is not installed or not added to the system PATH."
    echo "Please install Node.js 18+ and make sure the 'node' command is available."
    echo "Download from: https://nodejs.org/"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo ""
fi

# Start the development server
echo "Starting Next.js development server..."
echo "Frontend will be available at: http://localhost:3000"
echo "Make sure the FastAPI backend is running on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

npm run dev

echo ""
echo "Frontend server stopped."
