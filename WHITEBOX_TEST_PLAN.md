# White Box Testing Plan

## Hotel Reservation System - Code Coverage & Unit Testing

**Version:** 1.0  
**Date:** 2026-02-01  
**Purpose:** Internal code structure testing, logic verification, and code coverage analysis

---

## 1. Overview

White box testing focuses on:

- Internal code structure and logic
- Code coverage (statement, branch, path)
- Unit testing individual functions and methods
- Integration testing of module interactions
- SQL injection and security vulnerabilities
- Error handling and edge cases

---

## 2. Testing Scope

### 2.1 Backend Modules (Python)

```
src/
├── database/
│   ├── db_manager.py      [Database operations]
│   ├── init_db.py         [Database initialization]
│   └── schema.sql         [Schema validation]
├── services/
│   ├── auth_service.py    [Authentication logic]
│   ├── reservation_service.py [Reservation business logic]
│   ├── room_service.py    [Room management logic]
│   ├── pricing_service.py [Pricing calculations]
│   ├── report_service.py  [Report generation]
│   └── email_service.py   [Email notifications]
├── ui/
│   ├── display.py         [Console display]
│   └── menu.py            [Menu navigation]
└── utils/
    ├── validator.py       [Input validation]
    └── helpers.py         [Utility functions]
```

### 2.2 Backend API (app.py)

- Route handlers
- Request validation
- Response formatting
- Error handling middleware
- Authentication middleware

### 2.3 Frontend (Next.js/React)

- Component rendering
- State management
- API client methods
- Form validation
- Error handling

---

## 3. Test Categories

### 3.1 Unit Tests

Test individual functions/methods in isolation

### 3.2 Integration Tests

Test interaction between modules

### 3.3 Code Coverage Tests

Measure coverage metrics

### 3.4 Security Tests

SQL injection, XSS, authentication bypass

### 3.5 Performance Tests

Query optimization, response times

---

## 4. Backend Unit Tests

### 4.1 Database Manager (db_manager.py)

#### WB-DB-001: Connection Management

- **Test:** `test_database_connection()`
- **Coverage:** Connection creation, closing
- **Assertions:**
  - Connection returns valid cursor
  - Connection closes without errors
  - Multiple connections handled correctly

#### WB-DB-002: CRUD Operations

- **Test:** `test_execute_query()`
- **Coverage:** execute_query() method
- **Test Cases:**
  1. Valid SELECT query returns data
  2. Valid INSERT query returns lastrowid
  3. Invalid SQL raises exception
  4. SQL injection attempts blocked
  5. Transaction rollback on error

#### WB-DB-003: Transaction Handling

- **Test:** `test_transaction_commit_rollback()`
- **Coverage:** commit(), rollback()
- **Test Cases:**
  1. Successful transaction commits
  2. Failed transaction rolls back
  3. Nested transactions handled

---

### 4.2 Authentication Service (auth_service.py)

#### WB-AUTH-001: Password Hashing

- **Test:** `test_hash_password()`
- **Coverage:** hash_password(), verify_password()
- **Test Cases:**
  1. Password hashed correctly (not plaintext)
  2. Same password produces different hashes (salt)
  3. Correct password verification returns True
  4. Wrong password verification returns False
  5. Empty password handled

#### WB-AUTH-002: User Authentication

- **Test:** `test_authenticate_user()`
- **Coverage:** authenticate() method
- **Test Cases:**
  1. Valid credentials return user object
  2. Invalid username returns None
  3. Invalid password returns None
  4. Case-sensitive username check
  5. SQL injection in username blocked

#### WB-AUTH-003: Session Management

- **Test:** `test_create_session()`
- **Coverage:** create_session(), validate_session()
- **Test Cases:**
  1. Session token generated (UUID format)
  2. Session stored in database
  3. Valid token returns user
  4. Expired session returns None
  5. Invalid token returns None

#### WB-AUTH-004: Token Validation

- **Test:** `test_validate_token()`
- **Coverage:** Token format and expiration
- **Test Cases:**
  1. Valid token within expiration
  2. Expired token rejected
  3. Malformed token rejected
  4. Token for deleted user rejected

---

### 4.3 Reservation Service (reservation_service.py)

#### WB-RES-001: Create Reservation

- **Test:** `test_create_reservation()`
- **Coverage:** create_reservation() logic
- **Test Cases:**
  1. Valid reservation created
  2. Room availability checked
  3. Date overlap detected
  4. Invalid room_id rejected
  5. Past check_in_date rejected
  6. Check_out before check_in rejected
  7. Guest info validation
  8. Special characters in guest name

#### WB-RES-002: Room Availability Check

- **Test:** `test_is_room_available()`
- **Coverage:** Date range overlap logic
- **Test Cases:**
  1. Available room returns True
  2. Fully booked room returns False
  3. Partial overlap detected
  4. Same-day booking logic
  5. Edge case: checkout = next check-in
  6. Cancelled reservations ignored
  7. Multiple reservations checked

#### WB-RES-003: Reservation Status Transition

- **Test:** `test_update_reservation_status()`
- **Coverage:** Status change validation
- **Test Cases:**
  1. Pending → Confirmed allowed
  2. Confirmed → CheckedIn allowed
  3. CheckedIn → CheckedOut allowed
  4. CheckedOut → Cancelled not allowed
  5. Invalid status transition rejected
  6. Status history recorded

#### WB-RES-004: Cancel Reservation

- **Test:** `test_cancel_reservation()`
- **Coverage:** Cancellation logic
- **Test Cases:**
  1. Pending reservation cancelled
  2. Confirmed reservation cancelled
  3. CheckedIn reservation cancellation blocked
  4. CheckedOut reservation cancellation blocked
  5. Refund calculated correctly
  6. Cancellation timestamp recorded

#### WB-RES-005: Search Reservations

- **Test:** `test_search_reservations()`
- **Coverage:** Query filters
- **Test Cases:**
  1. Search by reservation ID
  2. Search by guest name (partial match)
  3. Search by room number
  4. Search by date range
  5. Search by status
  6. Multiple filters combined
  7. SQL injection in search terms blocked

---

### 4.4 Room Service (room_service.py)

#### WB-ROOM-001: Get Available Rooms

- **Test:** `test_get_available_rooms()`
- **Coverage:** Availability query
- **Test Cases:**
  1. No filters returns all rooms
  2. Room type filter applied
  3. Date range filter applied
  4. Price range filter applied
  5. Multiple filters combined
  6. No results handled gracefully

#### WB-ROOM-002: Update Room Status

- **Test:** `test_update_room_status()`
- **Coverage:** Status transition logic
- **Test Cases:**
  1. Available → Occupied
  2. Occupied → Maintenance
  3. Maintenance → Available
  4. Invalid status rejected
  5. Room with active reservation blocked

#### WB-ROOM-003: Room Pricing

- **Test:** `test_calculate_room_price()`
- **Coverage:** Dynamic pricing
- **Test Cases:**
  1. Base price calculation
  2. Weekend surcharge applied
  3. Holiday surcharge applied
  4. Long-stay discount applied
  5. Seasonal pricing adjustments

---

### 4.5 Pricing Service (pricing_service.py)

#### WB-PRICE-001: Calculate Total Price

- **Test:** `test_calculate_total_price()`
- **Coverage:** Price calculation logic
- **Test Cases:**
  1. Base price × nights
  2. Tax calculation
  3. Service charges
  4. Discount codes applied
  5. Negative price prevented
  6. Floating point precision

#### WB-PRICE-002: Dynamic Pricing

- **Test:** `test_get_dynamic_price()`
- **Coverage:** Price adjustment rules
- **Test Cases:**
  1. High demand increases price
  2. Low occupancy decreases price
  3. Advance booking discount
  4. Last-minute booking surcharge
  5. Price floor and ceiling respected

---

### 4.6 Report Service (report_service.py)

#### WB-REPORT-001: Occupancy Report

- **Test:** `test_generate_occupancy_report()`
- **Coverage:** Occupancy calculation
- **Test Cases:**
  1. Current occupancy percentage
  2. Historical occupancy by date
  3. Occupancy by room type
  4. Zero division handled
  5. Date range validation

#### WB-REPORT-002: Revenue Report

- **Test:** `test_generate_revenue_report()`
- **Coverage:** Revenue aggregation
- **Test Cases:**
  1. Total revenue calculation
  2. Revenue by date range
  3. Revenue by room type
  4. Cancelled reservations excluded
  5. Refunds subtracted

#### WB-REPORT-003: Guest Statistics

- **Test:** `test_generate_guest_stats()`
- **Coverage:** Guest analytics
- **Test Cases:**
  1. Unique guest count
  2. Repeat guest identification
  3. Average stay duration
  4. Guest demographics

---

### 4.7 Validation Utils (validator.py)

#### WB-VAL-001: Email Validation

- **Test:** `test_validate_email()`
- **Coverage:** Email regex
- **Test Cases:**
  1. Valid email accepted
  2. Invalid format rejected
  3. Missing @ rejected
  4. Missing domain rejected
  5. Special characters handled

#### WB-VAL-002: Phone Validation

- **Test:** `test_validate_phone()`
- **Coverage:** Phone number formats
- **Test Cases:**
  1. Valid 10-digit number
  2. International format
  3. With/without dashes
  4. Letters rejected
  5. Too short/long rejected

#### WB-VAL-003: Date Validation

- **Test:** `test_validate_date()`
- **Coverage:** Date format and logic
- **Test Cases:**
  1. Valid ISO format
  2. Invalid format rejected
  3. Past dates rejected (if required)
  4. Future dates accepted
  5. Leap year dates

#### WB-VAL-004: ID Number Validation

- **Test:** `test_validate_id_number()`
- **Coverage:** ID format validation
- **Test Cases:**
  1. Valid 18-digit ID
  2. Valid passport format
  3. Invalid length rejected
  4. Invalid characters rejected
  5. Checksum validation

---

## 5. Backend API Tests (app.py)

### 5.1 Authentication Endpoints

#### WB-API-AUTH-001: POST /api/auth/login

- **Coverage:** Login route handler
- **Test Cases:**
  1. Valid credentials return 200 + token
  2. Invalid credentials return 401
  3. Missing username returns 400
  4. Missing password returns 400
  5. SQL injection blocked
  6. XSS in username sanitized

#### WB-API-AUTH-002: POST /api/auth/logout

- **Coverage:** Logout route handler
- **Test Cases:**
  1. Valid token logs out successfully
  2. Invalid token returns 401
  3. Missing token returns 401
  4. Session deleted from database

---

### 5.2 Room Endpoints

#### WB-API-ROOM-001: GET /api/rooms

- **Coverage:** List rooms route
- **Test Cases:**
  1. Returns all rooms
  2. Authentication required
  3. Response format validation
  4. Database error handled

#### WB-API-ROOM-002: GET /api/rooms/available

- **Coverage:** Available rooms query
- **Test Cases:**
  1. Valid query params accepted
  2. Invalid dates return 400
  3. Missing params return 400
  4. Results filtered correctly

#### WB-API-ROOM-003: GET /api/rooms/with-reservations

- **Coverage:** Rooms with reservation status
- **Test Cases:**
  1. Returns room + reservation data
  2. Reserved rooms flagged
  3. Check-in dates included
  4. Query optimization verified

---

### 5.3 Reservation Endpoints

#### WB-API-RES-001: POST /api/reservations

- **Coverage:** Create reservation route
- **Test Cases:**
  1. Valid data creates reservation
  2. Missing required fields return 422
  3. Invalid room_id returns 404
  4. Date validation errors return 400
  5. Room unavailable returns 409
  6. Guest_info structure validated

#### WB-API-RES-002: GET /api/reservations/:id

- **Coverage:** Get reservation by ID
- **Test Cases:**
  1. Valid ID returns reservation
  2. Invalid ID returns 404
  3. Unauthorized access blocked
  4. Response includes all fields

#### WB-API-RES-003: PUT /api/reservations/:id

- **Coverage:** Update reservation
- **Test Cases:**
  1. Valid update succeeds
  2. Status transition validated
  3. Unauthorized update blocked
  4. Non-existent ID returns 404

---

### 5.4 Dashboard Endpoints

#### WB-API-DASH-001: GET /api/dashboard/stats

- **Coverage:** Dashboard statistics
- **Test Cases:**
  1. Returns all required fields
  2. Calculations accurate
  3. Date filtering works
  4. Caching implemented (if applicable)

---

## 6. Frontend Unit Tests

### 6.1 API Client (lib/api.ts)

#### WB-FE-API-001: Authentication Methods

- **Test:** `test_api_client_auth()`
- **Coverage:** login(), logout()
- **Test Cases:**
  1. Login stores token in localStorage
  2. Logout clears token
  3. Axios interceptor adds token to headers
  4. 401 error triggers logout

#### WB-FE-API-002: Room Methods

- **Test:** `test_api_client_rooms()`
- **Coverage:** getRooms(), getRoomsWithReservations()
- **Test Cases:**
  1. Request format correct
  2. Response parsed correctly
  3. Error handled gracefully

---

### 6.2 Components

#### WB-FE-COMP-001: ReservationForm

- **Test:** `test_reservation_form()`
- **Coverage:** Form submission
- **Test Cases:**
  1. Valid data submits correctly
  2. Required fields validated
  3. Date validation prevents past dates
  4. Guest info structure correct
  5. Loading state displayed
  6. Error message displayed

#### WB-FE-COMP-002: HotelMap

- **Test:** `test_hotel_map()`
- **Coverage:** Room status display
- **Test Cases:**
  1. Rooms rendered by floor
  2. Status colors correct
  3. Reserved rooms flagged
  4. Click interaction works
  5. Loading state displayed

---

## 7. Integration Tests

### 7.1 End-to-End Scenarios

#### WB-INT-001: Complete Reservation Flow

- **Steps:**
  1. User logs in
  2. Searches available rooms
  3. Creates reservation
  4. Reservation appears in system
  5. Room status updates
  6. User logs out
- **Verify:** Database consistency, state transitions

#### WB-INT-002: Check-in Flow

- **Steps:**
  1. Search reservation by ID
  2. Verify guest identity
  3. Update status to CheckedIn
  4. Room status updates to Occupied
  5. Generate invoice
- **Verify:** Status synchronization

#### WB-INT-003: Cancel and Rebook

- **Steps:**
  1. Cancel existing reservation
  2. Room becomes available
  3. Create new reservation for same room
  4. Verify no conflicts
- **Verify:** Availability logic

---

## 8. Security Tests

### 8.1 SQL Injection

#### WB-SEC-001: SQL Injection in Search

- **Test Input:** `'; DROP TABLE users; --`
- **Expected:** Input sanitized, no execution
- **Locations:** All search fields, login form

#### WB-SEC-002: SQL Injection in Filters

- **Test Input:** `' OR '1'='1`
- **Expected:** Query returns no results or errors
- **Locations:** Room filters, reservation filters

---

### 8.2 Authentication Bypass

#### WB-SEC-003: Token Tampering

- **Test:** Modify JWT payload
- **Expected:** Request rejected with 401

#### WB-SEC-004: Expired Token

- **Test:** Use token after expiration
- **Expected:** Request rejected with 401

#### WB-SEC-005: Missing Token

- **Test:** Access protected route without token
- **Expected:** Request rejected with 401

---

### 8.3 Authorization

#### WB-SEC-006: Role-Based Access

- **Test:** Receptionist accessing admin-only routes
- **Expected:** Request rejected with 403

---

### 8.4 XSS Prevention

#### WB-SEC-007: XSS in Guest Name

- **Test Input:** `<script>alert('XSS')</script>`
- **Expected:** Script tags escaped or removed

#### WB-SEC-008: XSS in Special Requests

- **Test Input:** Malicious HTML/JS
- **Expected:** Content sanitized

---

## 9. Code Coverage Targets

### 9.1 Coverage Metrics

- **Statement Coverage:** ≥ 80%
- **Branch Coverage:** ≥ 70%
- **Function Coverage:** ≥ 85%
- **Line Coverage:** ≥ 80%

### 9.2 Critical Paths (100% Coverage)

- Authentication logic
- Payment processing
- Reservation creation
- Date availability checks
- Security validation

### 9.3 Tools

- **Python:** pytest + pytest-cov
- **JavaScript:** Jest + Istanbul

---

## 10. Test Execution Plan

### 10.1 Test Order

1. Unit tests (individual functions)
2. Integration tests (module interactions)
3. API tests (route handlers)
4. Security tests (vulnerabilities)
5. Coverage analysis

### 10.2 Continuous Integration

- Run tests on every commit
- Block merge if tests fail
- Generate coverage reports
- Alert on coverage drop

---

## 11. Test Implementation

### 11.1 Python Test Structure

```python
# test_auth_service.py
import pytest
from src.services.auth_service import AuthService

class TestAuthService:
    def setup_method(self):
        self.auth_service = AuthService()

    def test_hash_password(self):
        password = "test123"
        hashed = self.auth_service.hash_password(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        password = "test123"
        hashed = self.auth_service.hash_password(password)
        assert self.auth_service.verify_password(password, hashed) == True

    def test_verify_password_incorrect(self):
        password = "test123"
        hashed = self.auth_service.hash_password(password)
        assert self.auth_service.verify_password("wrong", hashed) == False
```

### 11.2 API Test Structure

```python
# test_api_routes.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestAuthRoutes:
    def test_login_valid_credentials(self):
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert response.status_code == 200
        assert "session_token" in response.json()

    def test_login_invalid_credentials(self):
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "wrong"
        })
        assert response.status_code == 401
```

### 11.3 Frontend Test Structure

```typescript
// ReservationForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import ReservationForm from './ReservationForm';

describe('ReservationForm', () => {
  test('renders form fields', () => {
    render(<ReservationForm />);
    expect(screen.getByLabelText('Guest Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Check-in Date')).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    render(<ReservationForm />);
    fireEvent.click(screen.getByText('Submit'));
    expect(await screen.findByText('Guest name is required')).toBeInTheDocument();
  });
});
```

---

## 12. Test Data Management

### 12.1 Test Database

- Use separate test database
- Seed with known test data
- Reset between test runs
- Isolate tests (no shared state)

### 12.2 Mock Data

```python
MOCK_USER = {
    "id": 1,
    "username": "testuser",
    "role": "Admin"
}

MOCK_RESERVATION = {
    "id": 1,
    "room_id": 101,
    "guest_name": "Test Guest",
    "check_in_date": "2026-02-10",
    "check_out_date": "2026-02-15"
}
```

---

## 13. Performance Testing

### 13.1 Database Query Performance

- **Test:** Measure query execution time
- **Target:** < 100ms for simple queries
- **Target:** < 500ms for complex joins

### 13.2 API Response Time

- **Test:** Measure endpoint response time
- **Target:** < 200ms for most endpoints
- **Target:** < 1s for report generation

### 13.3 Load Testing

- **Test:** Concurrent user simulation
- **Target:** Handle 100 concurrent requests
- **Tool:** locust or Apache Bench

---

## 14. Test Automation

### 14.1 Run Commands

```bash
# Backend unit tests
pytest tests/ -v --cov=src --cov-report=html

# Backend API tests
pytest tests/api/ -v

# Frontend tests
cd frontend && npm test

# Coverage report
pytest --cov=src --cov-report=term-missing
```

### 14.2 Pre-commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/ --cov=src --cov-report=term --cov-fail-under=80
if [ $? -ne 0 ]; then
    echo "Tests failed or coverage below 80%"
    exit 1
fi
```

---

## 15. Documentation Requirements

For each test:

- **Purpose:** What is being tested
- **Setup:** Test data and environment
- **Steps:** Execution steps
- **Expected:** Expected results
- **Assertions:** Specific checks
- **Cleanup:** Teardown actions

---

## 16. Issue Tracking

### 16.1 Bug Severity Levels

- **CRITICAL:** System crash, data loss, security breach
- **HIGH:** Major feature broken, no workaround
- **MEDIUM:** Feature impaired, workaround exists
- **LOW:** Minor issue, cosmetic problem

### 16.2 Test Failure Protocol

1. Log failure details
2. Create bug ticket
3. Assign to developer
4. Retest after fix
5. Update test if needed

---

## Appendix A: Test Case Template

```markdown
### Test Case ID: WB-XXX-YYY

**Module:** [Module Name]
**Function:** [Function Name]
**Description:** [What this test validates]

**Preconditions:**

- [Setup requirements]

**Test Steps:**

1. [Step 1]
2. [Step 2]
3. [Step 3]

**Test Data:**

- Input: [Input values]
- Expected Output: [Expected results]

**Assertions:**

- Assert [condition 1]
- Assert [condition 2]

**Code Coverage:**

- Lines: [X-Y]
- Branches: [A, B, C]

**Status:** [ ] Not Started [ ] In Progress [ ] Passed [ ] Failed
```

---

## Appendix B: Coverage Report Example

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/services/auth_service.py         45      5    89%   23-27
src/services/reservation_service.py  120     15    87%   45, 78-92
src/services/room_service.py          80      8    90%   120-127
src/database/db_manager.py            55      2    96%   103, 115
---------------------------------------------------------------
TOTAL                                300     30    90%
```

---

**End of White Box Test Plan**
