# Testing Documentation

## Hotel Reservation System - Complete Testing Guide

**Version:** 1.0  
**Date:** 2026-02-01

---

## Overview

This document describes the complete testing strategy for the Hotel Reservation System, including both **Black Box Testing** (functional testing) and **White Box Testing** (structural testing).

---

## Test Types

### 1. Black Box Testing (Functional Testing)

- **Purpose:** Test system functionality from user perspective
- **Focus:** Input/output behavior without knowing internal code
- **Coverage:** User workflows, API endpoints, UI components
- **Script:** `blackbox_test.py`
- **Documentation:** `BLACKBOX_TEST_PLAN.md`

### 2. White Box Testing (Structural Testing)

- **Purpose:** Test internal code structure and logic
- **Focus:** Code paths, branches, conditions
- **Coverage:** Unit tests, integration tests, code coverage
- **Script:** `whitebox_test.py`
- **Documentation:** `WHITEBOX_TEST_PLAN.md`

---

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install pytest pytest-cov requests

# Install Node.js dependencies (for frontend tests)
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom jest
```

### Run All Tests

```bash
# Backend Black Box Tests
python blackbox_test.py

# Backend White Box Tests
python whitebox_test.py

# With Coverage Report
pytest whitebox_test.py --cov=src --cov-report=html

# Frontend Tests
cd frontend
npm test
```

---

## Black Box Testing

### What It Tests

- ✅ Authentication (login, logout, permissions)
- ✅ Dashboard statistics
- ✅ Hotel room map display
- ✅ Create reservations
- ✅ Search reservations
- ✅ Check-in/check-out workflows
- ✅ Reports generation
- ✅ System settings

### Test Modules

#### Module 1: Authentication

- **TC-AUTH-001:** Admin login
- **TC-AUTH-002:** Receptionist login
- **TC-AUTH-003:** Wrong password rejection
- **TC-AUTH-004:** Non-existent user rejection
- **TC-AUTH-005:** Logout

#### Module 2: Dashboard

- **TC-DASH-001:** Dashboard statistics data

#### Module 3: Hotel Map

- **TC-MAP-001:** Load all rooms
- **TC-MAP-002:** Room status display
- **TC-MAP-004:** Reservation info display

#### Module 4: Create Reservation

- **TC-RES-001:** Search available rooms
- **TC-RES-002:** Date validation
- **TC-RES-010:** Create reservation

#### Module 5: Search Reservations

- **TC-SEARCH-001:** Search by ID
- **TC-SEARCH-002:** Search by guest name

#### Module 6: Permissions

- **TC-PERM-001:** Unauthenticated access rejection

#### Module 7: Settings

- **TC-SETTINGS-002:** Password validation

### Running Black Box Tests

```bash
# Run all black box tests
python blackbox_test.py

# View results
cat test_results.json
```

### Test Results

Results are saved to `test_results.json` with:

- Test summary (total, passed, failed)
- Passed test list
- Failed test list with error details
- Timestamp

---

## White Box Testing

### What It Tests

- ✅ Database operations (CRUD, transactions)
- ✅ Password hashing and verification
- ✅ User authentication logic
- ✅ Session management
- ✅ Reservation business logic
- ✅ Room availability algorithms
- ✅ Pricing calculations
- ✅ Input validation (email, phone, date)
- ✅ SQL injection prevention
- ✅ Edge cases and error handling

### Test Categories

#### WB-DB: Database Manager

- **WB-DB-001:** Connection management
- **WB-DB-002:** CRUD operations
- **WB-DB-003:** Transaction handling

#### WB-AUTH: Authentication Service

- **WB-AUTH-001:** Password hashing
- **WB-AUTH-002:** User authentication
- **WB-AUTH-003:** Session management
- **WB-AUTH-004:** Token validation

#### WB-RES: Reservation Service

- **WB-RES-001:** Create reservation
- **WB-RES-002:** Room availability check
- **WB-RES-004:** Cancel reservation

#### WB-ROOM: Room Service

- **WB-ROOM-001:** Get available rooms
- **WB-ROOM-002:** Update room status

#### WB-PRICE: Pricing Service

- **WB-PRICE-001:** Calculate total price

#### WB-VAL: Validator Utils

- **WB-VAL-001:** Email validation
- **WB-VAL-002:** Phone validation
- **WB-VAL-003:** Date validation

### Running White Box Tests

```bash
# Run all white box tests
python whitebox_test.py

# Run with pytest
pytest whitebox_test.py -v

# Generate coverage report
pytest whitebox_test.py --cov=src --cov-report=html
```

### Coverage Targets

- **Statement Coverage:** ≥ 80%
- **Branch Coverage:** ≥ 70%
- **Function Coverage:** ≥ 85%
- **Critical Paths:** 100%

---

## Test Execution Strategy

### Development Workflow

1. **Write code** → Implement feature
2. **Write tests** → Create unit tests
3. **Run tests** → Verify functionality
4. **Fix issues** → Address failures
5. **Check coverage** → Ensure adequate coverage
6. **Commit** → Push to repository

---

## Security Testing

### SQL Injection Tests

```python
malicious_inputs = [
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "admin'--"
]
# Expected: Input sanitized, no execution
```

### XSS Prevention Tests

```python
xss_inputs = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>"
]
# Expected: Content escaped
```

---

## Performance Testing

### Response Time Targets

- **Simple queries:** < 100ms
- **Complex joins:** < 500ms
- **API endpoints:** < 200ms
- **Report generation:** < 1s

---

## Test Results

### Black Box Test Results

- **Total Tests:** 13
- **Pass Rate:** ~77%
- **Results File:** `test_results.json`

### White Box Test Results

- **Total Tests:** 45+
- **Success Rate:** ~95%
- **Results File:** `whitebox_test_results.json`

---

## Resources

### Documentation

- [BLACKBOX_TEST_PLAN.md](BLACKBOX_TEST_PLAN.md) - 118 test cases
- [WHITEBOX_TEST_PLAN.md](WHITEBOX_TEST_PLAN.md) - Unit test specifications
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - System overview

### Tools

- **pytest:** Python testing framework
- **pytest-cov:** Code coverage plugin
- **requests:** HTTP client for API testing
- **unittest:** Python standard library testing

---

**Last Updated:** 2026-02-01  
**Maintained By:** Development Team
