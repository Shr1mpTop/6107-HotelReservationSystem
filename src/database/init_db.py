"""
Database Initialization Module
Create database table structure and insert initial data
"""

import os
import sys
import bcrypt
from datetime import datetime

# Add project root directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager


def create_tables():
    """Create database tables"""
    print("Creating database tables...")
    
    # Read schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Execute SQL script
    db_manager.execute_script(schema_sql)
    print("✓ Database tables created successfully")


def hash_password(password: str) -> str:
    """Hash password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def insert_initial_users():
    """Insert initial users"""
    print("Creating initial users...")
    
    users = [
        ('admin', hash_password('admin123'), 'System Administrator', 'admin@hotel.com', '1234567890', 'admin'),
        ('frontdesk', hash_password('front123'), 'Front Desk Staff', 'front@hotel.com', '1234567891', 'front_desk'),
        ('housekeeping', hash_password('house123'), 'Housekeeping Staff', 'house@hotel.com', '1234567892', 'housekeeping'),
    ]
    
    query = """
        INSERT INTO users (username, password_hash, full_name, email, phone, role)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    for user in users:
        try:
            db_manager.execute_insert(query, user)
            print(f"✓ Created user: {user[0]}")
        except Exception as e:
            print(f"✗ Failed to create user {user[0]}: {e}")


def insert_initial_room_types():
    """Insert initial room types"""
    print("Creating initial room types...")
    
    room_types = [
        ('Standard Single Room', 'Equipped with single bed, private bathroom, TV, WiFi', 200.00, 1, 'Single bed, WiFi, TV, Air conditioning, Private bathroom'),
        ('Standard Double Room', 'Equipped with double bed, private bathroom, TV, WiFi', 300.00, 2, 'Double bed, WiFi, TV, Air conditioning, Private bathroom'),
        ('Deluxe Suite', 'Equipped with king bed, living room, private bathroom, TV, WiFi, mini bar', 500.00, 2, 'King bed, Living room, WiFi, TV, Air conditioning, Private bathroom, Mini bar'),
        ('Family Room', 'Equipped with two double beds, private bathroom, TV, WiFi', 450.00, 4, 'Double bed×2, WiFi, TV, Air conditioning, Private bathroom'),
    ]
    
    query = """
        INSERT INTO room_types (type_name, description, base_price, max_occupancy, amenities)
        VALUES (?, ?, ?, ?, ?)
    """
    
    for room_type in room_types:
        try:
            db_manager.execute_insert(query, room_type)
            print(f"✓ Created room type: {room_type[0]}")
        except Exception as e:
            print(f"✗ Failed to create room type {room_type[0]}: {e}")


def insert_initial_rooms():
    """Insert initial rooms"""
    print("Creating initial rooms...")
    
    # Get room type IDs
    room_types = db_manager.execute_query("SELECT room_type_id, type_name FROM room_types")
    type_map = {row['type_name']: row['room_type_id'] for row in room_types}
    
    rooms = []
    
    # Standard Single Room: 101-105 (1st floor)
    for i in range(101, 106):
        rooms.append((f"{i}", type_map['Standard Single Room'], 1, 'Clean'))
    
    # Standard Double Room: 201-210 (2nd floor)
    for i in range(201, 211):
        rooms.append((f"{i}", type_map['Standard Double Room'], 2, 'Clean'))
    
    # Deluxe Suite: 301-305 (3rd floor)
    for i in range(301, 306):
        rooms.append((f"{i}", type_map['Deluxe Suite'], 3, 'Clean'))
    
    # Family Room: 401-405 (4th floor)
    for i in range(401, 406):
        rooms.append((f"{i}", type_map['Family Room'], 4, 'Clean'))
    
    query = """
        INSERT INTO rooms (room_number, room_type_id, floor, status)
        VALUES (?, ?, ?, ?)
    """
    
    count = db_manager.execute_many(query, rooms)
    print(f"✓ Created {count} rooms")


def insert_sample_seasonal_pricing():
    """Insert sample seasonal pricing"""
    print("Creating sample seasonal pricing rules...")
    
    # Get room type IDs
    room_types = db_manager.execute_query("SELECT room_type_id, type_name FROM room_types")
    
    pricing_rules = [
        # Chinese New Year Peak Season (double price for all room types)
        (1, 'Chinese New Year Peak Season', '2026-01-24', '2026-02-07', 2.0, None),
        (2, 'Chinese New Year Peak Season', '2026-01-24', '2026-02-07', 2.0, None),
        (3, 'Chinese New Year Peak Season', '2026-01-24', '2026-02-07', 2.0, None),
        (4, 'Chinese New Year Peak Season', '2026-01-24', '2026-02-07', 2.0, None),
        
        # Summer Peak Season (50% price increase in July-August)
        (1, 'Summer Peak Season', '2026-07-01', '2026-08-31', 1.5, None),
        (2, 'Summer Peak Season', '2026-07-01', '2026-08-31', 1.5, None),
        (3, 'Summer Peak Season', '2026-07-01', '2026-08-31', 1.5, None),
        (4, 'Summer Peak Season', '2026-07-01', '2026-08-31', 1.5, None),
    ]
    
    query = """
        INSERT INTO seasonal_pricing 
        (room_type_id, season_name, start_date, end_date, price_multiplier, fixed_price)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    count = db_manager.execute_many(query, pricing_rules)
    print(f"✓ Created {count} seasonal pricing rules")


def initialize_database():
    """Initialize database"""
    print("\n" + "="*50)
    print("Hotel Reservation Management System - Database Initialization")
    print("="*50 + "\n")
    
    try:
        # Create tables
        create_tables()
        
        # Insert initial data
        insert_initial_users()
        insert_initial_room_types()
        insert_initial_rooms()
        insert_sample_seasonal_pricing()
        
        print("\n" + "="*50)
        print("✓ Database initialization completed!")
        print("="*50)
        print("\nDefault user accounts:")
        print("  Administrator  - Username: admin        Password: admin123")
        print("  Front Desk     - Username: frontdesk    Password: front123")
        print("  Housekeeping   - Username: housekeeping Password: house123")
        print("\nPlease use these accounts to log into the system.\n")
        
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    initialize_database()
