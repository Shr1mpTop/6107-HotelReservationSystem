"""
White Box Testing Automation Script
Unit tests, integration tests, and code coverage analysis
"""

import sys
import os
import pytest
import unittest
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.db_manager import DatabaseManager
from services.auth_service import AuthService
from services.reservation_service import ReservationService
from services.room_service import RoomService
from services.pricing_service import PricingService
from utils.validator import Validator

# ============================================================================
# Database Manager Tests
# ============================================================================

class TestDatabaseManager(unittest.TestCase):
    """WB-DB: Database Manager White Box Tests"""
    
    def setUp(self):
        """Setup test database"""
        self.db = DatabaseManager(":memory:")  # In-memory database for testing
    
    def tearDown(self):
        """Cleanup"""
        if hasattr(self.db, 'connection'):
            self.db.connection.close()
    
    def test_database_connection(self):
        """WB-DB-001: Connection Management"""
        # Test connection creation
        self.assertIsNotNone(self.db.connection)
        cursor = self.db.connection.cursor()
        self.assertIsNotNone(cursor)
        cursor.close()
        
        # Test closing connection
        self.db.connection.close()
        self.assertTrue(True)  # No exception raised
    
    def test_execute_query_select(self):
        """WB-DB-002: CRUD Operations - SELECT"""
        # Create test table
        self.db.execute_query("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Insert test data
        self.db.execute_query("INSERT INTO test_table (name) VALUES (?)", ("Test",))
        
        # Test SELECT query
        result = self.db.execute_query("SELECT * FROM test_table")
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Test")
    
    def test_execute_query_insert(self):
        """WB-DB-002: CRUD Operations - INSERT"""
        self.db.execute_query("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Test INSERT returns lastrowid
        cursor = self.db.execute_query("INSERT INTO test_table (name) VALUES (?)", ("Test",))
        self.assertIsNotNone(cursor.lastrowid)
        self.assertGreater(cursor.lastrowid, 0)
    
    def test_sql_injection_prevention(self):
        """WB-DB-002: SQL Injection Protection"""
        self.db.execute_query("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL
            )
        """)
        
        # Test SQL injection attempt with parameterized query
        malicious_input = "'; DROP TABLE users; --"
        
        # This should NOT drop the table
        try:
            self.db.execute_query(
                "SELECT * FROM users WHERE username = ?", 
                (malicious_input,)
            )
        except Exception:
            pass
        
        # Verify table still exists
        result = self.db.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)

# ============================================================================
# Authentication Service Tests
# ============================================================================

class TestAuthService(unittest.TestCase):
    """WB-AUTH: Authentication Service White Box Tests"""
    
    def setUp(self):
        """Setup test environment"""
        self.auth_service = AuthService()
        self.db = DatabaseManager(":memory:")
        # Initialize schema
        with open('src/database/schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
            for statement in schema.split(';'):
                if statement.strip():
                    self.db.execute_query(statement)
        self.auth_service.db_manager = self.db
    
    def test_hash_password(self):
        """WB-AUTH-001: Password Hashing"""
        password = "test123"
        hashed = self.auth_service.hash_password(password)
        
        # Password should be hashed (not plaintext)
        self.assertNotEqual(hashed, password)
        self.assertGreater(len(hashed), 0)
        
        # Same password should produce different hashes (salt)
        hashed2 = self.auth_service.hash_password(password)
        self.assertNotEqual(hashed, hashed2)
    
    def test_verify_password_correct(self):
        """WB-AUTH-001: Password Verification - Correct"""
        password = "test123"
        hashed = self.auth_service.hash_password(password)
        
        result = self.auth_service.verify_password(password, hashed)
        self.assertTrue(result)
    
    def test_verify_password_incorrect(self):
        """WB-AUTH-001: Password Verification - Incorrect"""
        password = "test123"
        hashed = self.auth_service.hash_password(password)
        
        result = self.auth_service.verify_password("wrong", hashed)
        self.assertFalse(result)
    
    def test_verify_password_empty(self):
        """WB-AUTH-001: Password Verification - Empty"""
        password = ""
        hashed = self.auth_service.hash_password(password)
        
        result = self.auth_service.verify_password("", hashed)
        self.assertTrue(result)
    
    def test_authenticate_user_valid(self):
        """WB-AUTH-002: User Authentication - Valid Credentials"""
        # Create test user
        hashed_password = self.auth_service.hash_password("admin123")
        self.db.execute_query("""
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        """, ("admin", hashed_password, "Admin", "Admin User"))
        
        # Test authentication
        user = self.auth_service.authenticate("admin", "admin123")
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], "admin")
        self.assertEqual(user['role'], "Admin")
    
    def test_authenticate_user_invalid_username(self):
        """WB-AUTH-002: User Authentication - Invalid Username"""
        user = self.auth_service.authenticate("nonexistent", "password")
        self.assertIsNone(user)
    
    def test_authenticate_user_invalid_password(self):
        """WB-AUTH-002: User Authentication - Invalid Password"""
        # Create test user
        hashed_password = self.auth_service.hash_password("admin123")
        self.db.execute_query("""
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        """, ("admin", hashed_password, "Admin", "Admin User"))
        
        # Test with wrong password
        user = self.auth_service.authenticate("admin", "wrongpassword")
        self.assertIsNone(user)
    
    def test_authenticate_sql_injection(self):
        """WB-AUTH-002: User Authentication - SQL Injection Prevention"""
        malicious_username = "admin' OR '1'='1"
        user = self.auth_service.authenticate(malicious_username, "password")
        self.assertIsNone(user)
    
    def test_create_session(self):
        """WB-AUTH-003: Session Management - Create"""
        user_id = 1
        session_token = self.auth_service.create_session(user_id)
        
        # Verify token format (UUID)
        self.assertIsNotNone(session_token)
        self.assertGreater(len(session_token), 20)
        
        # Verify session stored in database
        sessions = self.db.execute_query(
            "SELECT * FROM sessions WHERE user_id = ?", (user_id,)
        )
        self.assertGreater(len(sessions), 0)
    
    def test_validate_session_valid(self):
        """WB-AUTH-003: Session Management - Valid Token"""
        # Create session
        user_id = 1
        # First create a user
        hashed_password = self.auth_service.hash_password("test123")
        self.db.execute_query("""
            INSERT INTO users (id, username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, "testuser", hashed_password, "Receptionist", "Test User"))
        
        session_token = self.auth_service.create_session(user_id)
        
        # Validate session
        user = self.auth_service.validate_session(session_token)
        self.assertIsNotNone(user)
        self.assertEqual(user['id'], user_id)
    
    def test_validate_session_invalid_token(self):
        """WB-AUTH-004: Token Validation - Invalid Token"""
        invalid_token = "invalid-token-12345"
        user = self.auth_service.validate_session(invalid_token)
        self.assertIsNone(user)
    
    def test_validate_session_expired(self):
        """WB-AUTH-004: Token Validation - Expired Token"""
        user_id = 1
        
        # Create user
        hashed_password = self.auth_service.hash_password("test123")
        self.db.execute_query("""
            INSERT INTO users (id, username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, "testuser", hashed_password, "Receptionist", "Test User"))
        
        # Create session with past expiration
        import uuid
        token = str(uuid.uuid4())
        past_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        self.db.execute_query("""
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        """, (user_id, token, past_time))
        
        # Validate expired session
        user = self.auth_service.validate_session(token)
        self.assertIsNone(user)

# ============================================================================
# Reservation Service Tests
# ============================================================================

class TestReservationService(unittest.TestCase):
    """WB-RES: Reservation Service White Box Tests"""
    
    def setUp(self):
        """Setup test environment"""
        self.db = DatabaseManager(":memory:")
        # Initialize schema
        with open('src/database/schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
            for statement in schema.split(';'):
                if statement.strip():
                    self.db.execute_query(statement)
        
        self.reservation_service = ReservationService(self.db)
        
        # Create test room
        self.db.execute_query("""
            INSERT INTO rooms (room_number, room_type, price_per_night, status)
            VALUES (?, ?, ?, ?)
        """, ("101", "Standard", 100.0, "Available"))
    
    def test_create_reservation_valid(self):
        """WB-RES-001: Create Reservation - Valid Data"""
        reservation_data = {
            "room_id": 1,
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "guest_phone": "1234567890",
            "check_in_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "num_guests": 2,
            "special_requests": "Late check-in"
        }
        
        reservation_id = self.reservation_service.create_reservation(**reservation_data)
        self.assertIsNotNone(reservation_id)
        self.assertGreater(reservation_id, 0)
        
        # Verify reservation in database
        reservations = self.db.execute_query(
            "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
        )
        self.assertEqual(len(reservations), 1)
    
    def test_create_reservation_invalid_room(self):
        """WB-RES-001: Create Reservation - Invalid Room ID"""
        reservation_data = {
            "room_id": 9999,  # Non-existent room
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "guest_phone": "1234567890",
            "check_in_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "num_guests": 2
        }
        
        with self.assertRaises(Exception):
            self.reservation_service.create_reservation(**reservation_data)
    
    def test_create_reservation_past_date(self):
        """WB-RES-001: Create Reservation - Past Check-in Date"""
        reservation_data = {
            "room_id": 1,
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "guest_phone": "1234567890",
            "check_in_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "check_out_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "num_guests": 2
        }
        
        with self.assertRaises(ValueError):
            self.reservation_service.create_reservation(**reservation_data)
    
    def test_create_reservation_checkout_before_checkin(self):
        """WB-RES-001: Create Reservation - Checkout Before Check-in"""
        reservation_data = {
            "room_id": 1,
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "guest_phone": "1234567890",
            "check_in_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "check_out_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "num_guests": 2
        }
        
        with self.assertRaises(ValueError):
            self.reservation_service.create_reservation(**reservation_data)
    
    def test_is_room_available_true(self):
        """WB-RES-002: Room Availability Check - Available"""
        room_id = 1
        check_in = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d")
        
        available = self.reservation_service.is_room_available(room_id, check_in, check_out)
        self.assertTrue(available)
    
    def test_is_room_available_overlap(self):
        """WB-RES-002: Room Availability Check - Overlap Detected"""
        # Create existing reservation
        self.db.execute_query("""
            INSERT INTO reservations (
                room_id, guest_name, guest_email, guest_phone,
                check_in_date, check_out_date, num_guests, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, "Existing Guest", "exist@example.com", "9876543210",
            (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"),
            2, "Confirmed"
        ))
        
        # Try to book overlapping dates
        room_id = 1
        check_in = (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d")
        check_out = (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d")
        
        available = self.reservation_service.is_room_available(room_id, check_in, check_out)
        self.assertFalse(available)
    
    def test_cancel_reservation_pending(self):
        """WB-RES-004: Cancel Reservation - Pending Status"""
        # Create reservation
        reservation_id = self.db.execute_query("""
            INSERT INTO reservations (
                room_id, guest_name, guest_email, guest_phone,
                check_in_date, check_out_date, num_guests, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, "John Doe", "john@example.com", "1234567890",
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            2, "Pending"
        )).lastrowid
        
        # Cancel reservation
        result = self.reservation_service.cancel_reservation(reservation_id)
        self.assertTrue(result)
        
        # Verify status changed
        reservations = self.db.execute_query(
            "SELECT status FROM reservations WHERE id = ?", (reservation_id,)
        )
        self.assertEqual(reservations[0][0], "Cancelled")

# ============================================================================
# Room Service Tests
# ============================================================================

class TestRoomService(unittest.TestCase):
    """WB-ROOM: Room Service White Box Tests"""
    
    def setUp(self):
        """Setup test environment"""
        self.db = DatabaseManager(":memory:")
        # Initialize schema
        with open('src/database/schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
            for statement in schema.split(';'):
                if statement.strip():
                    self.db.execute_query(statement)
        
        self.room_service = RoomService(self.db)
        
        # Create test rooms
        self.db.execute_query("""
            INSERT INTO rooms (room_number, room_type, price_per_night, status)
            VALUES 
            ('101', 'Standard', 100.0, 'Available'),
            ('102', 'Standard', 100.0, 'Available'),
            ('201', 'Deluxe', 150.0, 'Available'),
            ('301', 'Suite', 250.0, 'Maintenance')
        """)
    
    def test_get_available_rooms_all(self):
        """WB-ROOM-001: Get Available Rooms - No Filters"""
        rooms = self.room_service.get_available_rooms()
        self.assertGreaterEqual(len(rooms), 3)  # 3 available rooms
    
    def test_get_available_rooms_by_type(self):
        """WB-ROOM-001: Get Available Rooms - Room Type Filter"""
        rooms = self.room_service.get_available_rooms(room_type="Standard")
        self.assertEqual(len(rooms), 2)
        for room in rooms:
            self.assertEqual(room['room_type'], "Standard")
    
    def test_get_available_rooms_by_price_range(self):
        """WB-ROOM-001: Get Available Rooms - Price Range Filter"""
        rooms = self.room_service.get_available_rooms(
            min_price=100.0,
            max_price=150.0
        )
        self.assertGreaterEqual(len(rooms), 2)
        for room in rooms:
            self.assertGreaterEqual(room['price_per_night'], 100.0)
            self.assertLessEqual(room['price_per_night'], 150.0)
    
    def test_update_room_status_valid(self):
        """WB-ROOM-002: Update Room Status - Valid Transition"""
        room_id = 1
        result = self.room_service.update_room_status(room_id, "Occupied")
        self.assertTrue(result)
        
        # Verify status changed
        rooms = self.db.execute_query(
            "SELECT status FROM rooms WHERE id = ?", (room_id,)
        )
        self.assertEqual(rooms[0][0], "Occupied")
    
    def test_update_room_status_invalid(self):
        """WB-ROOM-002: Update Room Status - Invalid Status"""
        room_id = 1
        with self.assertRaises(ValueError):
            self.room_service.update_room_status(room_id, "InvalidStatus")

# ============================================================================
# Pricing Service Tests
# ============================================================================

class TestPricingService(unittest.TestCase):
    """WB-PRICE: Pricing Service White Box Tests"""
    
    def setUp(self):
        """Setup test environment"""
        self.pricing_service = PricingService()
    
    def test_calculate_total_price_basic(self):
        """WB-PRICE-001: Calculate Total Price - Basic"""
        base_price = 100.0
        nights = 3
        total = self.pricing_service.calculate_total_price(base_price, nights)
        
        # Base calculation: 100 * 3 = 300
        self.assertEqual(total, 300.0)
    
    def test_calculate_total_price_with_tax(self):
        """WB-PRICE-001: Calculate Total Price - With Tax"""
        base_price = 100.0
        nights = 3
        tax_rate = 0.1  # 10% tax
        
        total = self.pricing_service.calculate_total_price(
            base_price, nights, tax_rate=tax_rate
        )
        
        # 300 + 10% tax = 330
        self.assertEqual(total, 330.0)
    
    def test_calculate_total_price_with_discount(self):
        """WB-PRICE-001: Calculate Total Price - With Discount"""
        base_price = 100.0
        nights = 3
        discount = 0.2  # 20% discount
        
        total = self.pricing_service.calculate_total_price(
            base_price, nights, discount=discount
        )
        
        # 300 - 20% = 240
        self.assertEqual(total, 240.0)
    
    def test_calculate_total_price_negative_prevention(self):
        """WB-PRICE-001: Calculate Total Price - Negative Prevention"""
        base_price = 100.0
        nights = 3
        discount = 2.0  # 200% discount (invalid)
        
        with self.assertRaises(ValueError):
            self.pricing_service.calculate_total_price(
                base_price, nights, discount=discount
            )

# ============================================================================
# Validator Tests
# ============================================================================

class TestValidator(unittest.TestCase):
    """WB-VAL: Validator Utils White Box Tests"""
    
    def setUp(self):
        """Setup test environment"""
        self.validator = Validator()
    
    def test_validate_email_valid(self):
        """WB-VAL-001: Email Validation - Valid"""
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            self.assertTrue(self.validator.validate_email(email))
    
    def test_validate_email_invalid(self):
        """WB-VAL-001: Email Validation - Invalid"""
        invalid_emails = [
            "invalid",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com"
        ]
        
        for email in invalid_emails:
            self.assertFalse(self.validator.validate_email(email))
    
    def test_validate_phone_valid(self):
        """WB-VAL-002: Phone Validation - Valid"""
        valid_phones = [
            "1234567890",
            "123-456-7890",
            "+1-234-567-8900",
            "(123) 456-7890"
        ]
        
        for phone in valid_phones:
            self.assertTrue(self.validator.validate_phone(phone))
    
    def test_validate_phone_invalid(self):
        """WB-VAL-002: Phone Validation - Invalid"""
        invalid_phones = [
            "123",  # Too short
            "abcdefghij",  # Letters
            "12345678901234567890",  # Too long
        ]
        
        for phone in invalid_phones:
            self.assertFalse(self.validator.validate_phone(phone))
    
    def test_validate_date_valid(self):
        """WB-VAL-003: Date Validation - Valid"""
        valid_dates = [
            "2026-02-01",
            "2026-12-31",
            "2024-02-29"  # Leap year
        ]
        
        for date in valid_dates:
            self.assertTrue(self.validator.validate_date(date))
    
    def test_validate_date_invalid(self):
        """WB-VAL-003: Date Validation - Invalid"""
        invalid_dates = [
            "2026-13-01",  # Invalid month
            "2026-02-30",  # Invalid day
            "2023-02-29",  # Not a leap year
            "26-02-01",    # Wrong format
            "2026/02/01"   # Wrong separator
        ]
        
        for date in invalid_dates:
            self.assertFalse(self.validator.validate_date(date))

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
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthService))
    suite.addTests(loader.loadTestsFromTestCase(TestReservationService))
    suite.addTests(loader.loadTestsFromTestCase(TestRoomService))
    suite.addTests(loader.loadTestsFromTestCase(TestPricingService))
    suite.addTests(loader.loadTestsFromTestCase(TestValidator))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("Test Result Summary")
    print("="*80)
    print(f"Total Tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # Save results
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "success_rate": f"{(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.2f}%"
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
