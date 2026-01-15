"""
数据库初始化模块
创建数据库表结构并插入初始数据
"""

import os
import sys
import bcrypt
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager


def create_tables():
    """创建数据库表"""
    print("正在创建数据库表...")
    
    # 读取schema.sql文件
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # 执行SQL脚本
    db_manager.execute_script(schema_sql)
    print("✓ 数据库表创建成功")


def hash_password(password: str) -> str:
    """哈希密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def insert_initial_users():
    """插入初始用户"""
    print("正在创建初始用户...")
    
    users = [
        ('admin', hash_password('admin123'), '系统管理员', 'admin@hotel.com', '1234567890', 'admin'),
        ('frontdesk', hash_password('front123'), '前台员工', 'front@hotel.com', '1234567891', 'front_desk'),
        ('housekeeping', hash_password('house123'), '客房员工', 'house@hotel.com', '1234567892', 'housekeeping'),
    ]
    
    query = """
        INSERT INTO users (username, password_hash, full_name, email, phone, role)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    for user in users:
        try:
            db_manager.execute_insert(query, user)
            print(f"✓ 创建用户: {user[0]}")
        except Exception as e:
            print(f"✗ 创建用户 {user[0]} 失败: {e}")


def insert_initial_room_types():
    """插入初始房型"""
    print("正在创建初始房型...")
    
    room_types = [
        ('标准单人间', '配备单人床、独立卫浴、电视、WiFi', 200.00, 1, '单人床, WiFi, 电视, 空调, 独立卫浴'),
        ('标准双人间', '配备双人床、独立卫浴、电视、WiFi', 300.00, 2, '双人床, WiFi, 电视, 空调, 独立卫浴'),
        ('豪华套房', '配备大床、客厅、独立卫浴、电视、WiFi、迷你吧', 500.00, 2, '大床, 客厅, WiFi, 电视, 空调, 独立卫浴, 迷你吧'),
        ('家庭房', '配备两张双人床、独立卫浴、电视、WiFi', 450.00, 4, '双人床×2, WiFi, 电视, 空调, 独立卫浴'),
    ]
    
    query = """
        INSERT INTO room_types (type_name, description, base_price, max_occupancy, amenities)
        VALUES (?, ?, ?, ?, ?)
    """
    
    for room_type in room_types:
        try:
            db_manager.execute_insert(query, room_type)
            print(f"✓ 创建房型: {room_type[0]}")
        except Exception as e:
            print(f"✗ 创建房型 {room_type[0]} 失败: {e}")


def insert_initial_rooms():
    """插入初始房间"""
    print("正在创建初始房间...")
    
    # 获取房型ID
    room_types = db_manager.execute_query("SELECT room_type_id, type_name FROM room_types")
    type_map = {row['type_name']: row['room_type_id'] for row in room_types}
    
    rooms = []
    
    # 标准单人间: 101-105 (1楼)
    for i in range(101, 106):
        rooms.append((f"{i}", type_map['标准单人间'], 1, 'Clean'))
    
    # 标准双人间: 201-210 (2楼)
    for i in range(201, 211):
        rooms.append((f"{i}", type_map['标准双人间'], 2, 'Clean'))
    
    # 豪华套房: 301-305 (3楼)
    for i in range(301, 306):
        rooms.append((f"{i}", type_map['豪华套房'], 3, 'Clean'))
    
    # 家庭房: 401-405 (4楼)
    for i in range(401, 406):
        rooms.append((f"{i}", type_map['家庭房'], 4, 'Clean'))
    
    query = """
        INSERT INTO rooms (room_number, room_type_id, floor, status)
        VALUES (?, ?, ?, ?)
    """
    
    count = db_manager.execute_many(query, rooms)
    print(f"✓ 创建了 {count} 个房间")


def insert_sample_seasonal_pricing():
    """插入示例季节性定价"""
    print("正在创建示例季节性定价规则...")
    
    # 获取房型ID
    room_types = db_manager.execute_query("SELECT room_type_id, type_name FROM room_types")
    
    pricing_rules = [
        # 春节旺季（所有房型价格翻倍）
        (1, '春节旺季', '2026-01-24', '2026-02-07', 2.0, None),
        (2, '春节旺季', '2026-01-24', '2026-02-07', 2.0, None),
        (3, '春节旺季', '2026-01-24', '2026-02-07', 2.0, None),
        (4, '春节旺季', '2026-01-24', '2026-02-07', 2.0, None),
        
        # 暑期旺季（7-8月价格上涨50%）
        (1, '暑期旺季', '2026-07-01', '2026-08-31', 1.5, None),
        (2, '暑期旺季', '2026-07-01', '2026-08-31', 1.5, None),
        (3, '暑期旺季', '2026-07-01', '2026-08-31', 1.5, None),
        (4, '暑期旺季', '2026-07-01', '2026-08-31', 1.5, None),
    ]
    
    query = """
        INSERT INTO seasonal_pricing 
        (room_type_id, season_name, start_date, end_date, price_multiplier, fixed_price)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    count = db_manager.execute_many(query, pricing_rules)
    print(f"✓ 创建了 {count} 条季节性定价规则")


def initialize_database():
    """初始化数据库"""
    print("\n" + "="*50)
    print("酒店预订管理系统 - 数据库初始化")
    print("="*50 + "\n")
    
    try:
        # 创建表
        create_tables()
        
        # 插入初始数据
        insert_initial_users()
        insert_initial_room_types()
        insert_initial_rooms()
        insert_sample_seasonal_pricing()
        
        print("\n" + "="*50)
        print("✓ 数据库初始化完成!")
        print("="*50)
        print("\n默认用户账户:")
        print("  管理员    - 用户名: admin        密码: admin123")
        print("  前台员工  - 用户名: frontdesk    密码: front123")
        print("  客房员工  - 用户名: housekeeping 密码: house123")
        print("\n请使用这些账户登录系统。\n")
        
    except Exception as e:
        print(f"\n✗ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    initialize_database()
