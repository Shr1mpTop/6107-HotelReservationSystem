# Hotel Reservation Management System (HRMS)

A professional, enterprise-grade Hotel Reservation Management System built with modern web technologies. Features a **Next.js React frontend** and **FastAPI Python backend**, providing a complete solution for managing hotel operations with role-based access control, real-time dashboards, and comprehensive reservation management. The entire application is fully internationalized in English.

## Features

- **Modern Web Interface**:
  - **Next.js 14 Frontend**: Professional React-based interface with TypeScript
  - **FastAPI Backend**: High-performance Python REST API
  - **Real-time Updates**: Live dashboard with occupancy statistics
  - **Professional Design**: Clean, emoji-free interface for business environments
- **Dual Access Methods**:
  - **Web Dashboard**: Modern responsive interface accessible from any device
  - **CLI Interface**: Command-line tools for system administration and automation
- **Role-Based Access Control**: Secure authentication with pre-defined roles (Administrator, Front Desk, Housekeeping)
- **Comprehensive Management**:
  - Room and room type management with status tracking
  - Guest information and reservation lifecycle management
  - Dynamic seasonal pricing with automatic calculations
  - Availability search and conflict prevention
- **Technical Excellence**:
  - RESTful API with OpenAPI/Swagger documentation
  - SQLite database with efficient query optimization
  - Session-based authentication with JWT tokens
  - Responsive design for desktop and mobile devices

## Technology Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Backend**: Python 3.8+, FastAPI, Uvicorn
- **Database**: SQLite 3
- **Database**: SQLite 3
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Core Libraries**:
  - `bcrypt`: For hashing user passwords.
  - `colorama`: To create a colorful and user-friendly CLI.
  - `tabulate`: To display data in well-formatted tables.
  - `uvicorn`: ASGI server for serving the FastAPI application.
  - `jinja2`: Template engine for HTML rendering.

## Project Structure

```
/
├── data/                 # SQLite database (auto-generated)
├── src/                  # Python backend source code
│   ├── database/         # Database connection, schema, initialization
│   ├── services/         # Business logic (auth, rooms, reservations, etc.)
│   ├── ui/               # CLI interface components
│   └── utils/            # Helper functions and validators
├── frontend/             # Next.js React frontend
│   ├── app/              # Next.js 14 app directory
│   │   ├── components/   # React components
│   │   ├── lib/          # API client and utilities
│   │   ├── login/        # Login page
│   │   └── dashboard/    # Main dashboard page
│   ├── package.json      # Node.js dependencies
│   └── next.config.js    # Next.js configuration
├── app.py                # FastAPI backend server
├── requirements.txt      # Python dependencies
├── start.bat/sh          # Full stack startup (recommended)
├── run_backend.bat/sh    # Backend API server only
├── run_frontend.bat/sh   # Frontend dev server only
└── run.bat/sh            # CLI interface
```

## Getting Started

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 18+** (for Next.js frontend)
- **npm or yarn** (Node package manager)

### Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Shr1mpTop/6107-HotelReservationSystem.git
    cd 6107-HotelReservationSystem
    ```

2.  **Start the Backend Server:**

    The FastAPI backend must be running for the frontend to work.
    - **On Windows:**
      ```bat
      run_web.bat
      ```
    - **On Linux or macOS:**
      ```bash
      chmod +x run_web.sh
      ./run_web.sh
      ```

    The backend will start on `http://localhost:8000`

3.  **Start the Next.js Frontend (Recommended):**

    In a new terminal window:
    - **On Windows:**
      ```bat
      run_frontend.bat
      ```
    - **On Linux or macOS:**
      ```bash
      chmod +x run_frontend.sh
      ./run_frontend.sh
      ```

    The frontend will start on `http://localhost:3000`

4.  **Alternative: CLI Interface**

    For command-line access:
    - **On Windows:**
      ```bat
      run.bat
      ```
    - **On Linux or macOS:**
      ```bash
      chmod +x run.sh
      ./run.sh
      ```

    The startup scripts will automatically:
    - Check if required dependencies are installed
    - Install all required packages from `requirements.txt` (Python) or `package.json` (Node.js)
    - Check if Python is installed.
    - Install all required dependencies from `requirements.txt`.
    - Create the `data/` directory if it doesn't exist.
    - Initialize the `hrms.db` database with tables and default data on the first run.

## How to Use

### Next.js Web Interface (Recommended)

1. **Start the backend server** (see installation steps above)
2. **Start the frontend server** using `run_frontend.bat` or `run_frontend.sh`
3. **Open your browser** and navigate to: `http://localhost:3000`
4. **Login** with one of the demo accounts (see credentials below)

The Next.js interface provides:

- **Professional Dashboard**: Clean, business-focused design without emojis
- **Real-time Statistics**: Live occupancy rates and room status updates
- **Intuitive Navigation**: Easy-to-use sidebar menu system
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Type-safe Development**: Built with TypeScript for reliability

### Legacy HTML Interface

For the original HTML/JavaScript interface, start only the backend and navigate to: `http://localhost:8000`

### CLI Interface

Run the CLI startup scripts for command-line access with full system functionality.

### Login Credentials

### Default User Accounts

| Role          | Username       | Password   |
| ------------- | -------------- | ---------- |
| Administrator | `admin`        | `admin123` |
| Front Desk    | `frontdesk`    | `front123` |
| Housekeeping  | `housekeeping` | `house123` |

## Testing

To ensure the system is functioning correctly, you can run the automated test script. This script verifies the database connection, authentication, and core service functionalities.

```bash
python test_system.py
```

You should see a summary indicating that all tests have passed.

## API Documentation

The web interface is powered by a comprehensive REST API. When the web server is running, you can access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

- `POST /api/auth/login` - User authentication
- `GET /api/rooms` - Get all rooms
- `GET /api/rooms/available` - Get available rooms for date range
- `PUT /api/rooms/{room_id}/status` - Update room status
- `GET /api/reservations` - Get all reservations
- `POST /api/reservations` - Create new reservation
- `DELETE /api/reservations/{reservation_id}` - Cancel reservation
- `GET /api/dashboard/stats` - Get dashboard statistics

## Features Comparison

| Feature                | Web Interface | CLI Interface |
| ---------------------- | ------------- | ------------- |
| User Authentication    | ✅            | ✅            |
| Room Management        | ✅            | ✅            |
| Reservation Management | ✅            | ✅            |
| Real-time Dashboard    | ✅            | ❌            |
| Visual Interface       | ✅            | ❌            |
| Mobile Support         | ✅            | ❌            |
| API Access             | ✅            | ❌            |
| System Reports         | ❌            | ✅            |

---

This project serves as a practical example of building a robust, modular, and user-friendly application in Python with both web and command-line interfaces.
