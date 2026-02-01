# Hotel Reservation Management System (HRMS)

A full-stack Hotel Reservation Management System with a **Next.js React frontend** and **FastAPI Python backend**. This system provides comprehensive hotel operations management including room booking, guest check-in/check-out, dynamic pricing, and real-time dashboard analytics.

## ✨ Features

### Core Functionality

- **Room Management**: Track room status (Clean, Occupied, Maintenance), room types, and floor layouts
- **Reservation System**: Create, modify, search, and cancel reservations with conflict detection
- **Check-in/Check-out**: Streamlined guest arrival and departure processing with payment handling
- **Dynamic Pricing**: Seasonal pricing rules with automatic price calculations
- **Dashboard Analytics**: Real-time occupancy rates, revenue statistics, and operational metrics

### Technical Features

- **Role-Based Access Control**: Three user roles (Admin, Front Desk, Housekeeping)
- **RESTful API**: Comprehensive API with Swagger/OpenAPI documentation
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Type-Safe Frontend**: Built with TypeScript for reliability

## 🛠 Technology Stack

| Layer    | Technology                       |
| -------- | -------------------------------- |
| Frontend | Next.js 16, React 19, TypeScript |
| Backend  | Python 3.8+, FastAPI, Uvicorn    |
| Database | SQLite 3                         |
| Styling  | CSS3 with CSS Variables          |

## 📁 Project Structure

```
HotelReservationSystem/
├── frontend/                 # Next.js React frontend
│   ├── app/
│   │   ├── components/       # Reusable React components
│   │   ├── lib/              # API client and utilities
│   │   ├── login/            # Login page
│   │   └── dashboard/        # Main dashboard
│   ├── package.json
│   └── next.config.js
├── src/                      # Python backend modules
│   ├── database/             # Database schema and manager
│   ├── services/             # Business logic services
│   ├── ui/                   # CLI interface (optional)
│   └── utils/                # Helper functions
├── data/                     # SQLite database (auto-generated)
├── app.py                    # FastAPI backend server
├── requirements.txt          # Python dependencies
├── start.bat / start.sh      # Quick start scripts
├── blackbox_test.py          # Black-box test suite
└── whitebox_test.py          # White-box test suite
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **npm** (comes with Node.js)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Shr1mpTop/6107-HotelReservationSystem.git
   cd 6107-HotelReservationSystem
   ```

2. **Start the application**

   **Windows:**

   ```bat
   start.bat
   ```

   **Linux/macOS:**

   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   This will automatically:
   - Install Python dependencies
   - Install Node.js dependencies
   - Initialize the database with sample data
   - Start the backend API server (http://localhost:8000)
   - Start the frontend dev server (http://localhost:3000)

3. **Open your browser** and navigate to: **http://localhost:3000**

### Manual Start (Advanced)

If you prefer to start services separately:

```bash
# Terminal 1: Start backend
run_backend.bat    # Windows
./run_backend.sh   # Linux/macOS

# Terminal 2: Start frontend
run_frontend.bat   # Windows
./run_frontend.sh  # Linux/macOS
```

## 👤 Default Login Credentials

| Role          | Username       | Password   |
| ------------- | -------------- | ---------- |
| Administrator | `admin`        | `admin123` |
| Front Desk    | `frontdesk`    | `front123` |
| Housekeeping  | `housekeeping` | `house123` |

## 📖 User Guide

### Dashboard

The main dashboard displays:

- **Room Statistics**: Total, available, reserved, and occupied rooms
- **Occupancy Rate**: Visual chart showing current occupancy
- **Hotel Map**: Interactive floor-by-floor room layout with status colors
- **Quick Actions**: Fast access to common operations

### Room Management

- View all rooms organized by floor
- Update room status (Clean → Occupied → Maintenance)
- Manage room types and base pricing
- Configure seasonal pricing rules

### Reservations

- **New Reservation**: Search available rooms by date range, select room, enter guest details
- **All Reservations**: View, search, modify, or cancel existing reservations
- **Check-in**: View pending arrivals, select reservation, confirm check-in
- **Check-out**: View current guests, process payment, complete check-out

### Reports (Admin Only)

- Occupancy reports by date range
- Revenue analytics
- Database backup and restore

## 🧪 Testing

Run the automated test suites:

```bash
# Black-box tests (16 test cases)
python blackbox_test.py

# White-box tests (37 test cases)
python whitebox_test.py

# Quick system verification
python test_system.py
```

## 📡 API Documentation

When the backend is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

| Endpoint                           | Method   | Description                        |
| ---------------------------------- | -------- | ---------------------------------- |
| `/api/auth/login`                  | POST     | User authentication                |
| `/api/dashboard/stats`             | GET      | Dashboard statistics               |
| `/api/rooms`                       | GET      | List all rooms                     |
| `/api/rooms/available`             | GET      | Get available rooms for date range |
| `/api/reservations`                | GET/POST | List/create reservations           |
| `/api/reservations/{id}/check-in`  | POST     | Process guest check-in             |
| `/api/reservations/{id}/check-out` | POST     | Process guest check-out            |
| `/api/pricing/calculate`           | GET      | Calculate reservation price        |

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Backend settings
DATABASE_PATH=data/hrms.db
SECRET_KEY=your-secret-key

# Frontend settings (in frontend/.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔧 Development

### Backend Development

```bash
cd 6107-HotelReservationSystem
pip install -r requirements.txt
python app.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## 📝 License

This project is for educational purposes as part of COMP6107 coursework.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
