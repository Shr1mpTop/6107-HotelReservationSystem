# Hotel Reservation Management System (HRMS)

A comprehensive Hotel Reservation Management System built with Python and SQLite, featuring both **command-line interface (CLI)** and **modern web interface** powered by FastAPI. This system provides a complete solution for managing hotel operations, including user authentication, room and reservation management, dynamic pricing, and reporting. The entire application, including the user interface, codebase, and database, is presented in English.

## Features

- **Dual Interface Support**:
  - **Web Interface**: Modern, responsive web dashboard with intuitive user experience
  - **CLI Interface**: Traditional command-line interface for system administration
- **Role-Based Access Control**: Pre-defined roles (Administrator, Front Desk, Housekeeping) with specific permissions to ensure secure access to system functionalities.
- **User Authentication & Session Management**: Secure user login with hashed passwords and session token management.
- **Room Management**:
  - Manage room types (e.g., Single, Double, Suite).
  - Manage individual rooms, including their status (Clean, Dirty, Under Maintenance).
  - View room availability based on dates.
- **Reservation Management**:
  - Create new reservations for guests.
  - View detailed reservation information.
  - Cancel existing reservations.
- **Guest Management**: Store and manage guest information for reservations.
- **Dynamic Pricing**: Implement seasonal pricing rules (e.g., peak season, holidays) with price multipliers.
- **Real-time Dashboard**: Live statistics and occupancy rates with visual indicators.
- **Responsive Design**: Web interface optimized for desktop and mobile devices.
- **RESTful API**: Complete REST API for integration with other systems.
- **Automated Setup**: Simple startup scripts for Windows and Linux/macOS that automatically install dependencies and initialize the database.

## Technology Stack

- **Backend**: Python 3
- **Web Framework**: FastAPI (for REST API and web interface)
- **Database**: SQLite 3
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Core Libraries**:
  - `bcrypt`: For hashing user passwords.
  - `colorama`: To create a colorful and user-friendly CLI.
  - `tabulate`: To display data in well-formatted tables.
  - `uvicorn`: ASGI server for serving the FastAPI application.
  - `jinja2`: Template engine for HTML rendering.

## Project Structure

The project is organized into a modular structure for clarity and maintainability:

```
/
├── data/
│   └── hrms.db           # SQLite database file (auto-generated)
├── src/
│   ├── database/         # Database connection, initialization, and schema
│   ├── services/         # Business logic for all modules
│   ├── ui/               # CLI User interface components (menus, display)
│   └── utils/            # Helper functions and validators
├── templates/            # HTML templates for web interface
│   ├── index.html        # Main dashboard page
│   └── login.html        # Login page
├── static/               # Static files for web interface
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
├── app.py                # FastAPI web application
├── test_system.py        # Automated system test script
├── requirements.txt      # Python dependencies
├── run.bat               # CLI startup script for Windows
├── run.sh                # CLI startup script for Linux/macOS
├── run_web.bat           # Web server startup script for Windows
└── run_web.sh            # Web server startup script for Linux/macOS
```

## Getting Started

### Prerequisites

- Python 3.8 or newer.

### Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Shr1mpTop/6107-HotelReservationSystem.git
    cd 6107-HotelReservationSystem
    ```

2.  **Run the startup script:**
    - **On Windows:**
      ```bat
      run.bat
      ```
    - **On Linux or macOS:**
      ```bash
      chmod +x run.sh
      ./run.sh
      ```

    The script will automatically perform the following steps:
    - Check if Python is installed.
    - Install all required dependencies from `requirements.txt`.
    - Create the `data/` directory if it doesn't exist.
    - Initialize the `hrms.db` database with tables and default data on the first run.

## How to Use

After running the startup script, the system will launch, and you can log in with one of the default user accounts.

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
