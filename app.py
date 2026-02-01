"""
FastAPI Web Application for Hotel Reservation Management System
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.auth_service import AuthService
from services.room_service import RoomService
from services.reservation_service import ReservationService
from services.pricing_service import PricingService
from database.db_manager import db_manager

# Initialize FastAPI app
app = FastAPI(
    title="Hotel Reservation Management System",
    description="A comprehensive hotel management system with web interface",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBearer()

# Pydantic models for API requests/responses
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    session_token: Optional[str] = None
    user: Optional[Dict] = None

class ReservationRequest(BaseModel):
    guest_info: Dict[str, str]
    room_id: int
    check_in_date: str
    check_out_date: str
    num_guests: int
    special_requests: str = ""

class RoomUpdateRequest(BaseModel):
    status: str

class UserInfo(BaseModel):
    user_id: int
    username: str
    role: str
    full_name: str

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInfo:
    """Verify JWT token and return current user"""
    session_token = credentials.credentials
    
    # Validate session token
    session = AuthService.validate_session(session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )
    
    return UserInfo(
        user_id=session['user_id'],
        username=session['username'],
        role=session['role'],
        full_name=session['full_name']
    )

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page"""
    return templates.TemplateResponse("login.html", {"request": request})

# API Endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and create session"""
    try:
        result = AuthService.login(login_data.username, login_data.password)
        if result:
            return LoginResponse(
                success=True,
                message="Login successful",
                session_token=result['session_token'],
                user=result['user']
            )
        else:
            return LoginResponse(
                success=False,
                message="Invalid username or password"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/logout")
async def logout(current_user: UserInfo = Depends(get_current_user)):
    """Logout current user"""
    # In a real implementation, we would invalidate the session token
    return {"success": True, "message": "Logged out successfully"}

@app.get("/api/rooms")
async def get_rooms(current_user: UserInfo = Depends(get_current_user)):
    """Get all rooms with their details"""
    try:
        rooms = RoomService.get_all_rooms_with_types()
        return {"success": True, "data": rooms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/available")
async def get_available_rooms(
    check_in: str, 
    check_out: str,
    current_user: UserInfo = Depends(get_current_user)
):
    """Get available rooms for given date range"""
    try:
        available_rooms = RoomService.get_available_rooms(check_in, check_out)
        return {"success": True, "data": available_rooms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/rooms/{room_id}/status")
async def update_room_status(
    room_id: int,
    update_data: RoomUpdateRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Update room status"""
    try:
        if current_user.role not in ['admin', 'housekeeping']:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success, message = RoomService.update_room_status(room_id, update_data.status, current_user.user_id)
        if success:
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reservations")
async def get_reservations(current_user: UserInfo = Depends(get_current_user)):
    """Get all reservations"""
    try:
        reservations = ReservationService.get_all_reservations()
        return {"success": True, "data": reservations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reservations")
async def create_reservation(
    reservation_data: ReservationRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Create a new reservation"""
    try:
        if current_user.role not in ['admin', 'front_desk']:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success, message, reservation_id = ReservationService.create_reservation(
            reservation_data.guest_info,
            reservation_data.room_id,
            reservation_data.check_in_date,
            reservation_data.check_out_date,
            reservation_data.num_guests,
            reservation_data.special_requests,
            current_user.user_id
        )
        
        if success:
            return {"success": True, "message": message, "reservation_id": reservation_id}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/reservations/{reservation_id}")
async def cancel_reservation(
    reservation_id: int,
    current_user: UserInfo = Depends(get_current_user)
):
    """Cancel a reservation"""
    try:
        if current_user.role not in ['admin', 'front_desk']:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success, message = ReservationService.cancel_reservation(reservation_id, current_user.user_id)
        if success:
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pricing/calculate")
async def calculate_price(
    room_type_id: int,
    check_in: str,
    check_out: str,
    current_user: UserInfo = Depends(get_current_user)
):
    """Calculate price for a room and date range"""
    try:
        price = PricingService.calculate_price(room_type_id, check_in, check_out)
        return {"success": True, "price": price}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: UserInfo = Depends(get_current_user)):
    """Get dashboard statistics"""
    try:
        # Get basic statistics
        total_rooms = len(RoomService.get_all_rooms())
        occupied_rooms = len([r for r in RoomService.get_all_rooms() if r.get('status') == 'Occupied'])
        available_rooms = total_rooms - occupied_rooms
        total_reservations = len(ReservationService.get_all_reservations())
        
        return {
            "success": True,
            "stats": {
                "total_rooms": total_rooms,
                "occupied_rooms": occupied_rooms,
                "available_rooms": available_rooms,
                "total_reservations": total_reservations,
                "occupancy_rate": round((occupied_rooms / total_rooms * 100), 2) if total_rooms > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Ensure database is initialized
    if not os.path.exists("data/hrms.db"):
        print("Initializing database...")
        from database.init_db import initialize_database
        initialize_database()
    
    print("Starting Hotel Reservation Management System Web Server...")
    print("Access the web interface at: http://localhost:8000")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)