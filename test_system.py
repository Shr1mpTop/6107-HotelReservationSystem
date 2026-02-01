"""
System test script
Used to verify that all system modules are working properly
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.db_manager import db_manager
from services.auth_service import AuthService
from services.room_service import RoomService
from services.pricing_service import PricingService
from services.reservation_service import ReservationService


def test_database():
    """Test database connection"""
    print("Testing database connection...")
    try:
        # Check if tables exist
        tables = ['users', 'rooms', 'room_types', 'reservations', 'guests']
        for table in tables:
            assert db_manager.table_exists(table), f"Table {table} does not exist"
        print("✓ Database connection normal")
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_authentication():
    """Test authentication system"""
    print("\nTesting authentication system...")
    try:
        # Test login
        result = AuthService.login('admin', 'admin123')
        assert result is not None, "Login failed"
        
        session_token = result['session_token']
        assert session_token is not None, "Session token is empty"
        
        # Test session validation
        session = AuthService.validate_session(session_token)
        assert session is not None, "Session validation failed"
        assert session['username'] == 'admin', "Username does not match"
        
        # Test permission check
        assert AuthService.is_admin(session_token), "Admin permission check failed"
        
        # Test logout
        assert AuthService.logout(session_token), "Logout failed"
        
        print("✓ Authentication system normal")
        return True
    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        return False


def test_room_service():
    """Test room service"""
    print("\nTesting room service...")
    try:
        # Test getting room types
        room_types = RoomService.get_room_types()
        assert len(room_types) > 0, "No room type data"
        
        # Test getting all rooms
        rooms = RoomService.list_all_rooms()
        assert len(rooms) > 0, "No room data"
        
        # Test querying available rooms
        available = RoomService.get_available_rooms('2026-02-01', '2026-02-05')
        assert isinstance(available, list), "Available rooms query failed"
        
        # Test room statistics
        stats = RoomService.get_room_statistics()
        assert 'total_rooms' in stats, "Room statistics failed"
        
        print(f"✓ Room service normal (Total {stats['total_rooms']} rooms)")
        return True
    except Exception as e:
        print(f"✗ Room service test failed: {e}")
        return False


def test_pricing_service():
    """Test pricing service"""
    print("\nTesting pricing service...")
    try:
        # Test getting base price
        price = PricingService.get_room_base_price(1)
        assert price is not None and price > 0, "Base price retrieval failed"
        
        # Test price calculation
        pricing_info = PricingService.calculate_total_price(
            1, '2026-02-01', '2026-02-05'
        )
        assert 'total' in pricing_info, "Price calculation failed"
        assert pricing_info['total'] > 0, "Total price is 0"
        assert pricing_info['nights'] == 4, "Nights calculation error"
        
        # Test seasonal pricing list
        seasonal = PricingService.list_seasonal_pricing()
        assert isinstance(seasonal, list), "Seasonal pricing query failed"
        
        print(f"✓ Pricing service normal (4 nights total: ¥{pricing_info['total']:.2f})")
        return True
    except Exception as e:
        print(f"✗ Pricing service test failed: {e}")
        return False


def test_reservation_service():
    """Test reservation service"""
    print("\nTesting reservation service...")
    try:
        # Login to get user ID
        login_result = AuthService.login('admin', 'admin123')
        user_id = login_result['user']['user_id']
        
        # Test creating reservation
        guest_info = {
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '13800138000',
            'email': 'test@example.com'
        }
        
        success, message, reservation_id = ReservationService.create_reservation(
            guest_info, 1, '2026-03-01', '2026-03-05', 1, 'Test reservation', user_id
        )
        
        if not success:
            # May be room conflict, try other room
            available = RoomService.get_available_rooms('2026-03-01', '2026-03-05')
            if available:
                success, message, reservation_id = ReservationService.create_reservation(
                    guest_info, available[0]['room_id'], 
                    '2026-03-01', '2026-03-05', 1, 'Test reservation', user_id
                )
        
        assert success, f"Create reservation failed: {message}"
        assert reservation_id is not None, "Reservation ID is empty"
        
        # Test querying reservation
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        assert reservation is not None, "Query reservation failed"
        assert reservation['reservation_id'] == reservation_id, "Reservation ID does not match"
        
        # Test canceling reservation
        success, message = ReservationService.cancel_reservation(reservation_id, user_id)
        assert success, f"Cancel reservation failed: {message}"
        
        # Logout
        AuthService.logout(login_result['session_token'])
        
        # Note: Do not delete test data, keep as example
        
        print(f"✓ Reservation service normal (Test reservation ID: {reservation_id})")
        return True
    except Exception as e:
        print(f"✗ Reservation service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("Hotel Reservation Management System - System Test")
    print("="*60)
    
    results = []
    
    # Run module tests
    results.append(("Database", test_database()))
    results.append(("Authentication", test_authentication()))
    results.append(("Room Service", test_room_service()))
    results.append(("Pricing Service", test_pricing_service()))
    results.append(("Reservation Service", test_reservation_service()))
    
    # Output test results
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for module, result in results:
        status = "✓ Passed" if result else "✗ Failed"
        print(f"{module:<15}: {status}")
    
    # Statistics
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "="*60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! System is running normally.")
        print("="*60)
        return True
    else:
        print("✗ Some tests failed, please check error messages.")
        print("="*60)
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
