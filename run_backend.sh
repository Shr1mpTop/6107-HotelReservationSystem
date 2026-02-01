#!/bin/bash

# Hotel Reservation Management System - Backend API Server

echo "========================================"
echo "HRMS Backend API Server"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null
then
    echo "Python is not installed or not added to the system PATH."
    echo "Please install Python 3.8+ from https://python.org/"
    exit 1
fi

# Install dependencies
echo "Checking Python dependencies..."
pip install -r requirements.txt --quiet

# Initialize database if needed
if [ ! -f "data/hrms.db" ]; then
    echo "Initializing database..."
    python src/database/init_db.py
    echo ""
fi

# Start FastAPI server
echo ""
echo "Starting FastAPI Backend Server..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

python app.py
