import sqlite3
import sys
import os
sys.path.insert(0, 'src')

from services.auth_service import AuthService

conn = sqlite3.connect('data/hotel.db')
cursor = conn.cursor()

# Check existing users
users = cursor.execute('SELECT username, role FROM users').fetchall()
print('Existing users:')
for u in users:
    print(f'  - {u[0]} ({u[1]})')

# Check if receptionist exists
has_receptionist = any(u[0] == 'receptionist' for u in users)
print(f'\nHas receptionist: {has_receptionist}')

if not has_receptionist:
    print('\nCreating receptionist user...')
    auth = AuthService()
    hashed = auth.hash_password('receptionist123')
    cursor.execute('''
        INSERT INTO users (username, password_hash, role, full_name, email, created_at)
        VALUES (?, ?, ?, ?, ?, datetime("now"))
    ''', ('receptionist', hashed, 'Receptionist', 'Front Desk', 'receptionist@hotel.com'))
    conn.commit()
    print('✅ Receptionist user created!')
else:
    print('\n✅ Receptionist user already exists')

conn.close()
