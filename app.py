"""
FastAPI Web Application for Hotel Reservation Management System
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
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
from services.report_service import ReportService
from database.db_manager import db_manager

# Initialize FastAPI app
app = FastAPI(
    title="Hotel Reservation Management System",
    description="A comprehensive hotel management system REST API",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ReservationUpdateRequest(BaseModel):
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    num_guests: Optional[int] = None
    special_requests: Optional[str] = None

class CheckInRequest(BaseModel):
    reservation_id: int

class CheckOutRequest(BaseModel):
    reservation_id: int
    payment_method: str
    payment_amount: float

class ReservationSearchRequest(BaseModel):
    guest_name: Optional[str] = None
    phone: Optional[str] = None
    reservation_id: Optional[int] = None
    room_number: Optional[str] = None

class RoomAddRequest(BaseModel):
    room_number: str
    room_type_id: int
    floor: int

class RoomTypeRequest(BaseModel):
    type_name: str
    description: str
    base_price: float
    max_occupancy: int
    amenities: str

class RoomTypeUpdateRequest(BaseModel):
    type_name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    max_occupancy: Optional[int] = None
    amenities: Optional[str] = None

class SeasonalPricingRequest(BaseModel):
    room_type_id: int
    season_name: str
    start_date: str
    end_date: str
    price_multiplier: Optional[float] = None
    fixed_price: Optional[float] = None

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

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

# API Routes
@app.get("/")
async def read_root():
    """API root endpoint"""
    return {
        "message": "Hotel Reservation Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "frontend": "http://localhost:3000"
    }

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
        rooms = RoomService.list_all_rooms()
        return {"success": True, "data": rooms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/with-reservations")
async def get_rooms_with_reservations(current_user: UserInfo = Depends(get_current_user)):
    """Get all rooms with reservation status for today and future"""
    try:
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get all rooms
        rooms = RoomService.list_all_rooms()
        
        # Get confirmed reservations from today onwards
        query = """
            SELECT room_id, check_in_date, check_out_date
            FROM reservations
            WHERE status IN ('Confirmed', 'CheckedIn')
                AND check_out_date >= ?
            ORDER BY check_in_date
        """
        reservations = db_manager.execute_query(query, (today,))
        
        # Map reservations to rooms
        reservation_map = {}
        for res in reservations:
            room_id = res[0]
            check_in = res[1]
            if room_id not in reservation_map:
                reservation_map[room_id] = check_in
        
        # Add reservation info to rooms
        for room in rooms:
            if room['room_id'] in reservation_map:
                room['has_reservation'] = True
                room['reservation_check_in'] = reservation_map[room['room_id']]
            else:
                room['has_reservation'] = False
                room['reservation_check_in'] = None
        
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
        # Use a query to get all reservations with guest and room details
        query = """
            SELECT 
                r.reservation_id, r.check_in_date, r.check_out_date, r.num_guests,
                r.total_price, r.status, r.special_requests, r.created_at,
                g.first_name as guest_first_name, g.last_name as guest_last_name,
                g.email as guest_email, g.phone as guest_phone,
                rm.room_number, rt.type_name as room_type
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            JOIN room_types rt ON rm.room_type_id = rt.room_type_id
            ORDER BY r.created_at DESC
        """
        result = db_manager.execute_query(query)
        reservations = db_manager.rows_to_dict_list(result)
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
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get basic statistics using room statistics method
        room_stats = RoomService.get_room_statistics()
        total_rooms = room_stats.get('total_rooms', 0)
        occupied_rooms = room_stats.get('occupied_rooms', 0)
        
        # Get rooms with active reservations (Confirmed status, overlapping with today)
        reserved_query = """
            SELECT COUNT(DISTINCT room_id) as count FROM reservations 
            WHERE status = 'Confirmed'
                AND check_in_date <= ?
                AND check_out_date > ?
        """
        reserved_result = db_manager.execute_query(reserved_query, (today, today))
        reserved_rooms = reserved_result[0]['count'] if reserved_result else 0
        
        # Available = Total - Occupied - Reserved (but not yet checked in)
        available_rooms = total_rooms - occupied_rooms - reserved_rooms
        
        # Get total reservations count
        reservations_query = "SELECT COUNT(*) as count FROM reservations"
        reservations_result = db_manager.execute_query(reservations_query)
        total_reservations = reservations_result[0]['count'] if reservations_result else 0
        
        # Get active reservations (Confirmed or CheckedIn)
        active_query = """
            SELECT COUNT(*) as count FROM reservations 
            WHERE status IN ('Confirmed', 'CheckedIn')
        """
        active_result = db_manager.execute_query(active_query)
        active_reservations = active_result[0]['count'] if active_result else 0
        
        # Get today's check-ins
        checkins_query = """
            SELECT COUNT(*) as count FROM reservations 
            WHERE check_in_date = ? AND status IN ('Confirmed', 'CheckedIn')
        """
        checkins_result = db_manager.execute_query(checkins_query, (today,))
        today_checkins = checkins_result[0]['count'] if checkins_result else 0
        
        # Calculate occupancy including reserved rooms
        total_used = occupied_rooms + reserved_rooms
        
        return {
            "success": True,
            "stats": {
                "total_rooms": total_rooms,
                "occupied_rooms": occupied_rooms,
                "reserved_rooms": reserved_rooms,
                "available_rooms": available_rooms,
                "total_reservations": total_reservations,
                "active_reservations": active_reservations,
                "today_checkins": today_checkins,
                "occupancy_rate": round((total_used / total_rooms * 100), 2) if total_rooms > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Extended Reservation APIs ====================

@app.post("/api/reservations/search")
async def search_reservations(
    search_data: ReservationSearchRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Search reservations by criteria"""
    try:
        reservations = ReservationService.search_reservations(
            guest_name=search_data.guest_name,
            phone=search_data.phone,
            reservation_id=search_data.reservation_id,
            room_number=search_data.room_number
        )
        return {"success": True, "data": reservations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reservations/today-checkins")
async def get_today_checkins(
    current_user: UserInfo = Depends(get_current_user)
):
    """Get list of reservations scheduled for check-in today (status = Confirmed)"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        query = """
            SELECT r.reservation_id, 
                   g.first_name || ' ' || g.last_name as guest_name,
                   rm.room_number,
                   r.check_in_date, r.check_out_date
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.room_id
            JOIN guests g ON r.guest_id = g.guest_id
            WHERE r.status = 'Confirmed'
            AND r.check_in_date <= ?
            ORDER BY r.check_in_date ASC
        """
        result = db_manager.execute_query(query, (today,))
        return {"success": True, "data": result if result else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reservations/current-guests")
async def get_current_guests(
    current_user: UserInfo = Depends(get_current_user)
):
    """Get list of reservations with checked-in guests (status = CheckedIn)"""
    try:
        query = """
            SELECT r.reservation_id, 
                   g.first_name || ' ' || g.last_name as guest_name,
                   rm.room_number,
                   r.check_in_date, r.check_out_date, r.total_price
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.room_id
            JOIN guests g ON r.guest_id = g.guest_id
            WHERE r.status = 'CheckedIn'
            ORDER BY r.check_out_date ASC
        """
        result = db_manager.execute_query(query)
        return {"success": True, "data": result if result else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reservations/{reservation_id}/detail")
async def get_reservation_detail(
    reservation_id: int,
    current_user: UserInfo = Depends(get_current_user)
):
    """Get detailed information for a specific reservation"""
    try:
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return {"success": True, "data": reservation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/reservations/{reservation_id}")
async def update_reservation(
    reservation_id: int,
    update_data: ReservationUpdateRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Update reservation details"""
    try:
        if current_user.role not in ['admin', 'front_desk']:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success, message = ReservationService.modify_reservation(
            reservation_id,
            new_check_in=update_data.check_in_date,
            new_check_out=update_data.check_out_date,
            new_num_guests=update_data.num_guests,
            new_special_requests=update_data.special_requests,
            user_id=current_user.user_id
        )
        
        if success:
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reservations/{reservation_id}/check-in")
async def check_in_guest(
    reservation_id: int,
    current_user: UserInfo = Depends(get_current_user)
):
    """Check in a guest"""
    try:
        if current_user.role not in ['admin', 'front_desk']:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success, message = ReservationService.check_in(reservation_id, current_user.user_id)
        if success:
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reservations/{reservation_id}/check-out")
async def check_out_guest(
    reservation_id: int,
    payment_data: CheckOutRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Check out a guest with payment"""
    try:
        if current_user.role not in ['admin', 'front_desk']:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        success, message = ReservationService.check_out(
            reservation_id,
            payment_data.payment_method,
            payment_data.payment_amount,
            current_user.user_id
        )
        
        if success:
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reservations/today-checkins")
async def get_today_checkins(current_user: UserInfo = Depends(get_current_user)):
    """Get reservations checking in today"""
    try:
        reservations = ReservationService.get_upcoming_checkins(days=0)
        return {"success": True, "data": reservations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reservations/current-guests")
async def get_current_guests(current_user: UserInfo = Depends(get_current_user)):
    """Get all currently checked-in guests"""
    try:
        reservations = ReservationService.get_current_checkins()
        return {"success": True, "data": reservations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Room Type Management APIs ====================

@app.get("/api/room-types")
async def get_room_types(current_user: UserInfo = Depends(get_current_user)):
    """Get all room types"""
    try:
        room_types = RoomService.get_room_types()
        return {"success": True, "data": room_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/room-types/{room_type_id}")
async def get_room_type_detail(
    room_type_id: int,
    current_user: UserInfo = Depends(get_current_user)
):
    """Get room type details"""
    try:
        room_type = RoomService.get_room_type_by_id(room_type_id)
        if not room_type:
            raise HTTPException(status_code=404, detail="Room type not found")
        return {"success": True, "data": room_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/room-types")
async def add_room_type(
    room_type_data: RoomTypeRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Add a new room type"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success, message, room_type_id = RoomService.add_room_type(
            room_type_data.type_name,
            room_type_data.description,
            room_type_data.base_price,
            room_type_data.max_occupancy,
            room_type_data.amenities,
            current_user.user_id
        )
        
        if success:
            return {"success": True, "message": message, "room_type_id": room_type_id}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/room-types/{room_type_id}")
async def update_room_type(
    room_type_id: int,
    update_data: RoomTypeUpdateRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Update room type"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success, message = RoomService.update_room_type(
            room_type_id,
            type_name=update_data.type_name,
            description=update_data.description,
            base_price=update_data.base_price,
            max_occupancy=update_data.max_occupancy,
            amenities=update_data.amenities,
            user_id=current_user.user_id
        )
        
        if success:
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Room Management APIs ====================

@app.post("/api/rooms")
async def add_room(
    room_data: RoomAddRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Add a new room"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success, message, room_id = RoomService.add_room(
            room_data.room_number,
            room_data.room_type_id,
            room_data.floor,
            current_user.user_id
        )
        
        if success:
            return {"success": True, "message": message, "room_id": room_id}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rooms/statistics")
async def get_room_statistics(current_user: UserInfo = Depends(get_current_user)):
    """Get room statistics"""
    try:
        stats = RoomService.get_room_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Pricing Management APIs ====================

@app.get("/api/pricing/seasonal")
async def get_seasonal_pricing(current_user: UserInfo = Depends(get_current_user)):
    """Get all seasonal pricing rules"""
    try:
        pricing_rules = PricingService.list_seasonal_pricing()
        return {"success": True, "data": pricing_rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pricing/seasonal")
async def add_seasonal_pricing(
    pricing_data: SeasonalPricingRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Add a seasonal pricing rule"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success, message, pricing_id = PricingService.add_seasonal_pricing(
            pricing_data.room_type_id,
            pricing_data.season_name,
            pricing_data.start_date,
            pricing_data.end_date,
            pricing_data.price_multiplier,
            pricing_data.fixed_price,
            current_user.user_id
        )
        
        if success:
            return {"success": True, "message": message, "pricing_id": pricing_id}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/pricing/seasonal/{pricing_id}")
async def delete_seasonal_pricing(
    pricing_id: int,
    current_user: UserInfo = Depends(get_current_user)
):
    """Delete a seasonal pricing rule"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success, message = PricingService.delete_seasonal_pricing(pricing_id, current_user.user_id)
        if success:
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Report APIs ====================

@app.get("/api/reports/occupancy")
async def get_occupancy_report(
    start_date: str,
    end_date: str,
    current_user: UserInfo = Depends(get_current_user)
):
    """Generate occupancy report"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        report = ReportService.generate_occupancy_report(start_date, end_date)
        return {"success": True, "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/revenue")
async def get_revenue_report(
    start_date: str,
    end_date: str,
    current_user: UserInfo = Depends(get_current_user)
):
    """Generate revenue report"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        report = ReportService.generate_revenue_report(start_date, end_date)
        return {"success": True, "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audit-logs")
async def get_audit_logs(
    operation_type: Optional[str] = None,
    table_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    current_user: UserInfo = Depends(get_current_user)
):
    """Get audit logs"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        logs = ReportService.get_audit_logs(
            operation_type=operation_type,
            table_name=table_name,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        return {"success": True, "data": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backup")
async def create_backup(
    backup_name: str = "hrms_backup",
    current_user: UserInfo = Depends(get_current_user)
):
    """Create database backup"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        success, result = ReportService.backup_database(backup_name, current_user.user_id)
        if success:
            return {"success": True, "message": "Backup created successfully", "path": result}
        else:
            return {"success": False, "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backups")
async def get_backup_history(current_user: UserInfo = Depends(get_current_user)):
    """Get backup history"""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        backups = ReportService.list_backups()
        return {"success": True, "data": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== User Management APIs ====================

@app.put("/api/users/{user_id}/password")
async def change_password(
    user_id: int,
    password_data: PasswordChangeRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Users can only change their own password
        if current_user.user_id != user_id:
            raise HTTPException(status_code=403, detail="You can only change your own password")
        
        success, message = AuthService.change_password(
            user_id,
            password_data.old_password,
            password_data.new_password
        )
        
        if success:
            return {"success": True, "message": message}
        else:
            return {"success": False, "message": message}
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