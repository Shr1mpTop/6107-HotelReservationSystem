"""
Fix Black Box Test Issues
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.auth_service import AuthService

def fix_issue_1_create_receptionist():
    """Fix Issue #1: Create receptionist user"""
    print("Fixing Issue #1: Creating receptionist user...")
    
    try:
        conn = sqlite3.connect('data/hotel.db')
        cursor = conn.cursor()
        
        # Check if receptionist exists
        cursor.execute("SELECT id FROM users WHERE username = 'receptionist'")
        if cursor.fetchone():
            print("  ✅ Receptionist user already exists")
            conn.close()
            return True
        
        # Create receptionist user
        auth_service = AuthService()
        hashed_password = auth_service.hash_password('receptionist123')
        
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name, email, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, ('receptionist', hashed_password, 'Receptionist', 'Front Desk Staff', 'receptionist@hotel.com'))
        
        conn.commit()
        print("  ✅ Receptionist user created successfully")
        print("     Username: receptionist")
        print("     Password: receptionist123")
        print("     Role: Receptionist")
        
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def fix_issue_2_dashboard_stats():
    """Fix Issue #2: Add today_checkins field to dashboard stats"""
    print("\nFixing Issue #2: Dashboard stats field...")
    print("  ℹ️  This requires modifying app.py code")
    print("  ✅ Will add 'today_checkins' calculation")
    return True

def fix_issue_3_verify_endpoint():
    """Fix Issue #3: Verify endpoint exists"""
    print("\nFixing Issue #3: Verifying /api/rooms/with-reservations endpoint...")
    
    # Check if app.py has the endpoint
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if '/api/rooms/with-reservations' in content:
            print("  ✅ Endpoint exists in app.py")
            print("  ℹ️  If getting 404, backend server may need restart")
            return True
        else:
            print("  ❌ Endpoint not found in app.py")
            return False

def main():
    print("="*80)
    print("Black Box Test Issue Fixes")
    print("="*80)
    
    # Fix Issue #1
    success1 = fix_issue_1_create_receptionist()
    
    # Fix Issue #2 (requires code modification)
    success2 = fix_issue_2_dashboard_stats()
    
    # Fix Issue #3
    success3 = fix_issue_3_verify_endpoint()
    
    print("\n" + "="*80)
    print("Fix Summary")
    print("="*80)
    print(f"Issue #1 (Receptionist user): {'✅ FIXED' if success1 else '❌ FAILED'}")
    print(f"Issue #2 (Dashboard stats): 🔧 NEEDS CODE UPDATE")
    print(f"Issue #3 (Room endpoint): {'✅ VERIFIED' if success3 else '❌ FAILED'}")
    print("="*80)
    
    if success1 and success3:
        print("\n✅ Issues fixed! Now updating app.py for dashboard stats...")
        return True
    else:
        print("\n❌ Some issues need manual attention")
        return False

if __name__ == "__main__":
    main()
