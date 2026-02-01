#!/bin/bash

# Hotel Reservation Management System - Web Server Startup Script

echo "========================================"
echo "Hotel Reservation Management System (HRMS)"
echo "Web Interface"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null
then
    echo "Python is not installed or not added to the system PATH."
    echo "Please install Python 3.x and make sure the 'python' command is available."
    exit 1
fi

# Check and install dependencies
echo "Checking and installing required dependencies..."
pip install -r requirements.txt --quiet
echo "All dependencies are installed."
echo ""

# Check and initialize the database
if [ ! -f "data/hrms.db" ]; then
    echo "Initializing database..."
    python src/database/init_db.py
    echo ""
else
    echo "Database already exists, skipping initialization."
    echo ""
fi

# Start the web server
echo "Starting the Hotel Reservation Management System Web Server..."
echo "Web interface will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

python app.py

echo ""
echo "Web server stopped."