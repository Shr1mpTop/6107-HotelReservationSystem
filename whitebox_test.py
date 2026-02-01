"""
White Box Testing Automation Script
Unit tests, integration tests, and code coverage analysis

Refactored to match actual service implementations
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ============================================================================
# Validator Tests (Module-level functions)
# ============================================================================

class TestValidator(unittest.TestCase):
    """WB-VAL: Validator Utils White Box Tests"""
    
    def test_validate_email_valid(self):
        """WB-VAL-001: Email Validation - Valid"""
        from utils import validator
        
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            self.assertTrue(validator.validate_email(email), f"Email should be valid: {email}")
    
    def test_validate_email_invalid(self):
        """WB-VAL-001: Email Validation - Invalid"""
        from utils import validator
        
        invalid_emails = [
            "invalid",
            "@example.com",
            "user@",
            "user@.com"
        ]
        
        for email in invalid_emails:
            self.assertFalse(validator.validate_email(email), f"Email should be invalid: {email}")
    
    def test_validate_phone_valid(self):
        """WB-VAL-002: Phone Validation - Valid (11 digits)"""
        from utils import validator
        
        valid_phones = [
            "13812345678",
            "15012345678",
            "18612345678"
        ]
        
        for phone in valid_phones:
            self.assertTrue(validator.validate_phone(phone), f"Phone should be valid: {phone}")
    
    def test_validate_phone_invalid(self):
        """WB-VAL-002: Phone Validation - Invalid"""
        from utils import validator
        
        invalid_phones = [
            "123",           # Too short
            "1234567890",    # 10 digits (not 11)
            "abcdefghijk",   # Letters
            "123456789012",  # 12 digits (too long)
        ]
        
        for phone in invalid_phones:
            self.assertFalse(validator.validate_phone(phone), f"Phone should be invalid: {phone}")
    
    def test_validate_date_valid(self):
        """WB-VAL-003: Date Validation - Valid"""
        from utils import validator
        
        valid_dates = [
            "2026-02-01",
            "2026-12-31",
            "2024-02-29"  # Leap year
        ]
        
        for date in valid_dates:
            self.assertTrue(validator.validate_date(date), f"Date should be valid: {date}")
    
    def test_validate_date_invalid(self):
        """WB-VAL-003: Date Validation - Invalid"""
        from utils import validator
        
        invalid_dates = [
            "2026-13-01",  # Invalid month
            "2026-02-30",  # Invalid day
            "2023-02-29",  # Not a leap year
            "26-02-01",    # Wrong format
            "2026/02/01"   # Wrong separator
        ]
        
        for date in invalid_dates:
            self.assertFalse(validator.validate_date(date), f"Date should be invalid: {date}")
    
    def test_validate_id_number_valid(self):
        """WB-VAL-004: ID Number Validation - Valid"""
        from utils import validator
        
        valid_ids = [
            "123456789012345",     # 15 digits
            "123456789012345678",  # 18 digits
            "12345678901234567X",  # 18 chars with X
        ]
        
        for id_num in valid_ids:
            self.assertTrue(validator.validate_id_number(id_num), f"ID should be valid: {id_num}")
    
    def test_validate_id_number_invalid(self):
        """WB-VAL-004: ID Number Validation - Invalid"""
        from utils import validator
        
        invalid_ids = [
            "123456",              # Too short
            "1234567890123456",    # 16 digits (neither 15 nor 18)
            "12345678901234567A",  # Invalid char (A instead of X)
        ]
        
        for id_num in invalid_ids:
            self.assertFalse(validator.validate_id_number(id_num), f"ID should be invalid: {id_num}")
    
    def test_sanitize_input(self):
        """WB-VAL-005: Input Sanitization"""
        from utils import validator
        
        self.assertEqual(validator.sanitize_input("  hello  "), "hello")
        self.assertEqual(validator.sanitize_input("test"), "test")
        self.assertEqual(validator.sanitize_input(""), "")
        self.assertEqual(validator.sanitize_input(None), "")


# ============================================================================
# Auth Service Tests
# ============================================================================

class TestAuthService(unittest.TestCase):
    """WB-AUTH: Authentication Service White Box Tests"""
    
    def test_hash_password(self):
        """WB-AUTH-001: Password Hashing"""
        from services.auth_service import AuthService
        
        password = "test123"
        hashed = AuthService.hash_password(password)
        
        # Password should be hashed (not plaintext)
        self.assertNotEqual(hashed, password)
        self.assertGreater(len(hashed), 0)
        
        # Same password should produce different hashes (salt)
        hashed2 = AuthService.hash_password(password)
        self.assertNotEqual(hashed, hashed2)
    
    def test_verify_password_correct(self):
        """WB-AUTH-001: Password Verification - Correct"""
        from services.auth_service import AuthService
        
        password = "test123"
        hashed = AuthService.hash_password(password)
        
        result = AuthService.verify_password(password, hashed)
        self.assertTrue(result)
    
    def test_verify_password_incorrect(self):
        """WB-AUTH-001: Password Verification - Incorrect"""
        from services.auth_service import AuthService
        
        password = "test123"
        hashed = AuthService.hash_password(password)
        
        result = AuthService.verify_password("wrong", hashed)
        self.assertFalse(result)
    
    def test_verify_password_empty(self):
        """WB-AUTH-001: Password Verification - Empty"""
        from services.auth_service import AuthService
        
        password = ""
        hashed = AuthService.hash_password(password)
        
        result = AuthService.verify_password("", hashed)
        self.assertTrue(result)
    
    def test_generate_session_token(self):
        """WB-AUTH-002: Session Token Generation"""
        from services.auth_service import AuthService
        
        token1 = AuthService.generate_session_token()
        token2 = AuthService.generate_session_token()
        
        # Tokens should be non-empty
        self.assertIsNotNone(token1)
        self.assertGreater(len(token1), 20)
        
        # Each token should be unique
        self.assertNotEqual(token1, token2)
    
    def test_validate_session_invalid_token(self):
        """WB-AUTH-003: Session Validation - Invalid Token"""
        from services.auth_service import AuthService
        
        invalid_token = "invalid-token-12345"
        user = AuthService.validate_session(invalid_token)
        self.assertIsNone(user)


# ============================================================================
# Database Integration Tests (using actual database)
# ============================================================================

class TestDatabaseIntegration(unittest.TestCase):
    """WB-DB: Database Integration Tests"""
    
    def test_database_connection(self):
        """WB-DB-001: Database Connection"""
        from database.db_manager import db_manager
        
        # Should be able to get connection
        conn = db_manager.get_connection()
        self.assertIsNotNone(conn)
        
        # Connection should work
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
        
        cursor.close()
        conn.close()
    
    def test_execute_query(self):
        """WB-DB-002: Execute Query"""
        from database.db_manager import db_manager
        
        # Should be able to query existing tables
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM users")
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
    
    def test_rows_to_dict_list(self):
        """WB-DB-003: Row Conversion"""
        from database.db_manager import db_manager
        
        result = db_manager.execute_query("SELECT user_id, username FROM users LIMIT 1")
        dict_list = db_manager.rows_to_dict_list(result)
        
        if dict_list:
            self.assertIsInstance(dict_list, list)
            self.assertIsInstance(dict_list[0], dict)
            self.assertIn('username', dict_list[0])


# ============================================================================
# Room Service Tests (using actual database)
# ============================================================================

class TestRoomService(unittest.TestCase):
    """WB-ROOM: Room Service White Box Tests"""
    
    def test_list_all_rooms(self):
        """WB-ROOM-001: List All Rooms"""
        from services.room_service import RoomService
        
        rooms = RoomService.list_all_rooms()
        
        self.assertIsInstance(rooms, list)
        self.assertGreater(len(rooms), 0)
        
        # Each room should have required fields
        for room in rooms:
            self.assertIn('room_id', room)
            self.assertIn('room_number', room)
            self.assertIn('status', room)
    
    def test_get_available_rooms(self):
        """WB-ROOM-002: Get Available Rooms"""
        from services.room_service import RoomService
        
        # Use future dates
        check_in = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        check_out = (datetime.now() + timedelta(days=32)).strftime('%Y-%m-%d')
        
        rooms = RoomService.get_available_rooms(check_in, check_out)
        
        self.assertIsInstance(rooms, list)
        # All returned rooms should have Clean status
        for room in rooms:
            self.assertEqual(room['status'], 'Clean')
    
    def test_get_room_by_id(self):
        """WB-ROOM-003: Get Room By ID"""
        from services.room_service import RoomService
        
        # Get first room
        rooms = RoomService.list_all_rooms()
        if rooms:
            room_id = rooms[0]['room_id']
            room = RoomService.get_room_by_id(room_id)
            
            self.assertIsNotNone(room)
            self.assertEqual(room['room_id'], room_id)
    
    def test_get_room_by_id_not_found(self):
        """WB-ROOM-004: Get Room By ID - Not Found"""
        from services.room_service import RoomService
        
        room = RoomService.get_room_by_id(99999)
        self.assertIsNone(room)
    
    def test_get_room_statistics(self):
        """WB-ROOM-005: Get Room Statistics"""
        from services.room_service import RoomService
        
        stats = RoomService.get_room_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_rooms', stats)
        self.assertIn('occupied_rooms', stats)
        self.assertIn('clean_rooms', stats)
    
    def test_room_status_constants(self):
        """WB-ROOM-006: Room Status Constants"""
        from services.room_service import RoomService
        
        self.assertEqual(RoomService.STATUS_CLEAN, 'Clean')
        self.assertEqual(RoomService.STATUS_DIRTY, 'Dirty')
        self.assertEqual(RoomService.STATUS_OCCUPIED, 'Occupied')
        self.assertEqual(RoomService.STATUS_MAINTENANCE, 'Maintenance')


# ============================================================================
# Pricing Service Tests
# ============================================================================

class TestPricingService(unittest.TestCase):
    """WB-PRICE: Pricing Service White Box Tests"""
    
    def test_get_room_base_price(self):
        """WB-PRICE-001: Get Room Base Price"""
        from services.pricing_service import PricingService
        
        # Get first room type
        from database.db_manager import db_manager
        result = db_manager.execute_query("SELECT room_type_id FROM room_types LIMIT 1")
        
        if result:
            room_type_id = result[0]['room_type_id']
            price = PricingService.get_room_base_price(room_type_id)
            
            self.assertIsNotNone(price)
            self.assertIsInstance(price, float)
            self.assertGreater(price, 0)
    
    def test_get_room_base_price_not_found(self):
        """WB-PRICE-002: Get Room Base Price - Not Found"""
        from services.pricing_service import PricingService
        
        price = PricingService.get_room_base_price(99999)
        self.assertIsNone(price)
    
    def test_calculate_daily_price(self):
        """WB-PRICE-003: Calculate Daily Price"""
        from services.pricing_service import PricingService
        
        # Get first room type
        from database.db_manager import db_manager
        result = db_manager.execute_query("SELECT room_type_id FROM room_types LIMIT 1")
        
        if result:
            room_type_id = result[0]['room_type_id']
            date = datetime.now().strftime('%Y-%m-%d')
            
            daily_price = PricingService.calculate_daily_price(room_type_id, date)
            
            self.assertIsInstance(daily_price, float)
            self.assertGreaterEqual(daily_price, 0)
    
    def test_calculate_total_price(self):
        """WB-PRICE-004: Calculate Total Price"""
        from services.pricing_service import PricingService
        
        # Get first room type
        from database.db_manager import db_manager
        result = db_manager.execute_query("SELECT room_type_id FROM room_types LIMIT 1")
        
        if result:
            room_type_id = result[0]['room_type_id']
            check_in = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            check_out = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
            
            pricing_info = PricingService.calculate_total_price(room_type_id, check_in, check_out)
            
            self.assertIsInstance(pricing_info, dict)
            self.assertIn('total', pricing_info)
            self.assertIn('nights', pricing_info)
            self.assertEqual(pricing_info['nights'], 2)
            self.assertGreater(pricing_info['total'], 0)


# ============================================================================
# Reservation Service Tests
# ============================================================================

class TestReservationService(unittest.TestCase):
    """WB-RES: Reservation Service White Box Tests"""
    
    def test_reservation_status_constants(self):
        """WB-RES-001: Reservation Status Constants"""
        from services.reservation_service import ReservationService
        
        self.assertEqual(ReservationService.STATUS_CONFIRMED, 'Confirmed')
        self.assertEqual(ReservationService.STATUS_CHECKED_IN, 'CheckedIn')
        self.assertEqual(ReservationService.STATUS_CHECKED_OUT, 'CheckedOut')
        self.assertEqual(ReservationService.STATUS_CANCELLED, 'Cancelled')
    
    def test_get_reservation_by_id(self):
        """WB-RES-002: Get Reservation By ID"""
        from services.reservation_service import ReservationService
        
        # Try to get an existing reservation
        from database.db_manager import db_manager
        result = db_manager.execute_query("SELECT reservation_id FROM reservations LIMIT 1")
        
        if result:
            reservation_id = result[0]['reservation_id']
            reservation = ReservationService.get_reservation_by_id(reservation_id)
            
            self.assertIsNotNone(reservation)
            self.assertEqual(reservation['reservation_id'], reservation_id)
    
    def test_get_reservation_by_id_not_found(self):
        """WB-RES-003: Get Reservation By ID - Not Found"""
        from services.reservation_service import ReservationService
        
        reservation = ReservationService.get_reservation_by_id(99999)
        self.assertIsNone(reservation)
    
    def test_search_reservations_by_guest_name(self):
        """WB-RES-004: Search Reservations By Guest Name"""
        from services.reservation_service import ReservationService
        
        # Search with partial name
        results = ReservationService.search_reservations(guest_name="Test")
        
        self.assertIsInstance(results, list)
    
    def test_get_current_checkins(self):
        """WB-RES-005: Get Current Check-ins"""
        from services.reservation_service import ReservationService
        
        checkins = ReservationService.get_current_checkins()
        
        self.assertIsInstance(checkins, list)
    
    def test_get_upcoming_checkins(self):
        """WB-RES-006: Get Upcoming Check-ins"""
        from services.reservation_service import ReservationService
        
        checkins = ReservationService.get_upcoming_checkins(days=1)
        
        self.assertIsInstance(checkins, list)


# ============================================================================
# Email Service Tests
# ============================================================================

class TestEmailService(unittest.TestCase):
    """WB-EMAIL: Email Service White Box Tests"""
    
    def test_send_reservation_confirmation(self):
        """WB-EMAIL-001: Send Reservation Confirmation"""
        from services.email_service import EmailService
        
        reservation = {
            'reservation_id': 1,
            'guest_name': 'John Doe',
            'room_number': '101',
            'room_type': 'Standard',
            'check_in_date': '2026-02-10',
            'check_out_date': '2026-02-12',
            'num_guests': 2,
            'total_price': 500.00,
            'guest_email': 'test@example.com'
        }
        
        result = EmailService.send_reservation_confirmation(reservation)
        
        # Should return boolean
        self.assertIsInstance(result, bool)


# ============================================================================
# Report Service Tests
# ============================================================================

class TestReportService(unittest.TestCase):
    """WB-REPORT: Report Service White Box Tests"""
    
    def test_generate_occupancy_report(self):
        """WB-REPORT-001: Generate Occupancy Report"""
        from services.report_service import ReportService
        
        # Use date range (start_date must be before end_date)
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        report = ReportService.generate_occupancy_report(start_date, end_date)
        
        self.assertIsInstance(report, dict)
        self.assertIn('total_rooms', report)
        self.assertIn('daily_data', report)
        self.assertIn('average_occupancy_rate', report)
        # Verify daily_data structure
        if report['daily_data']:
            self.assertIn('occupied_rooms', report['daily_data'][0])
    
    def test_generate_revenue_report(self):
        """WB-REPORT-002: Generate Revenue Report"""
        from services.report_service import ReportService
        
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        report = ReportService.generate_revenue_report(start_date, end_date)
        
        self.assertIsInstance(report, dict)
        self.assertIn('total_revenue', report)


# ============================================================================
# Test Runner
# ============================================================================

def run_all_tests():
    """Run all white box tests and generate report"""
    print("\n" + "#"*80)
    print("  Hotel Reservation System - White Box Test Suite")
    print("#"*80 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes in order
    test_classes = [
        TestValidator,
        TestAuthService,
        TestDatabaseIntegration,
        TestRoomService,
        TestPricingService,
        TestReservationService,
        TestEmailService,
        TestReportService,
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("Test Result Summary")
    print("="*80)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if total > 0:
        print(f"Success Rate: {passed/total*100:.2f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Save results
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": len(result.failures),
            "errors": len(result.errors),
            "success_rate": f"{passed/total*100:.2f}%" if total > 0 else "0%"
        },
        "failures": [
            {"test": str(test), "traceback": traceback}
            for test, traceback in result.failures
        ],
        "errors": [
            {"test": str(test), "traceback": traceback}
            for test, traceback in result.errors
        ]
    }
    
    with open('whitebox_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    
    print("\nTest results saved to whitebox_test_results.json")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Starting white box tests...")
    success = run_all_tests()
    print("\nTesting completed!")
    sys.exit(0 if success else 1)
