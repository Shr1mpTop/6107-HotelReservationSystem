#!/bin/bash

# Hotel Reservation Management System - Full Stack Startup

echo "========================================"
echo "Hotel Reservation Management System"
echo "Full Stack Startup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null
then
    echo "ERROR: Python is not installed!"
    echo "Please install Python 3.8+ from https://python.org/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null
then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "All prerequisites are installed."
echo ""

# Make scripts executable
chmod +x run_backend.sh
chmod +x run_frontend.sh

echo "Starting Backend Server..."
./run_backend.sh &
BACKEND_PID=$!

echo "Waiting 5 seconds for backend to start..."
sleep 5

echo "Starting Frontend Server..."
./run_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "System Started Successfully!"
echo "========================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all servers..."
echo "========================================"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
