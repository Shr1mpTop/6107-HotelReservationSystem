# Hotel Reservation Management System (HRMS)

A comprehensive, command-line based Hotel Reservation Management System built with Python and SQLite. This system provides a complete solution for managing hotel operations, including user authentication, room and reservation management, dynamic pricing, and reporting. The entire application, including the user interface, codebase, and database, is presented in English.

## Features

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
- **Reporting**: Generate system reports, such as reservation summaries and occupancy statistics (feature can be extended).
- **Interactive CLI**: A user-friendly and colorful command-line interface for easy navigation and operation.
- **Automated Setup**: Simple startup scripts for Windows and Linux/macOS that automatically install dependencies and initialize the database.

## Technology Stack

- **Backend**: Python 3
- **Database**: SQLite 3
- **Core Libraries**:
  - `bcrypt`: For hashing user passwords.
  - `colorama`: To create a colorful and user-friendly CLI.
  - `tabulate`: To display data in well-formatted tables.

## Project Structure

The project is organized into a modular structure for clarity and maintainability:

```
/
├── data/
│   └── hrms.db           # SQLite database file (auto-generated)
├── src/
│   ├── database/         # Database connection, initialization, and schema
│   ├── services/         # Business logic for all modules
│   ├── ui/               # User interface components (menus, display)
│   └── utils/            # Helper functions and validators
├── test_system.py        # Automated system test script
├── requirements.txt      # Python dependencies
├── run.bat               # Startup script for Windows
└── run.sh                # Startup script for Linux/macOS
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

---

This project serves as a practical example of building a robust, modular, and user-friendly console application in Python.
