-- 酒店预订管理系统数据库Schema
-- SQLite 3

-- ============================================
-- 用户和权限表
-- ============================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'front_desk', 'housekeeping')),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 用户会话表
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ============================================
-- 房间和房型表
-- ============================================

-- 房型表
CREATE TABLE IF NOT EXISTS room_types (
    room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    base_price DECIMAL(10, 2) NOT NULL,
    max_occupancy INTEGER NOT NULL,
    amenities TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 房间表
CREATE TABLE IF NOT EXISTS rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number VARCHAR(10) UNIQUE NOT NULL,
    room_type_id INTEGER NOT NULL,
    floor INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'Clean' CHECK(status IN ('Clean', 'Dirty', 'Occupied', 'Maintenance')),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES room_types(room_type_id)
);

-- ============================================
-- 预订相关表
-- ============================================

-- 客人信息表
CREATE TABLE IF NOT EXISTS guests (
    guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20) NOT NULL,
    id_number VARCHAR(50),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预订表
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    num_guests INTEGER NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Confirmed' CHECK(status IN ('Confirmed', 'CheckedIn', 'CheckedOut', 'Cancelled')),
    special_requests TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- 支付记录表
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL CHECK(payment_method IN ('Cash', 'CreditCard', 'DebitCard', 'OnlineTransfer')),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK(payment_status IN ('Pending', 'Paid', 'Refunded')),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_by INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id),
    FOREIGN KEY (processed_by) REFERENCES users(user_id)
);

-- ============================================
-- 定价相关表
-- ============================================

-- 季节性定价规则表
CREATE TABLE IF NOT EXISTS seasonal_pricing (
    pricing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_type_id INTEGER NOT NULL,
    season_name VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    price_multiplier DECIMAL(5, 2) NOT NULL,
    fixed_price DECIMAL(10, 2),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES room_types(room_type_id),
    CHECK (end_date > start_date)
);

-- ============================================
-- 邮件通知表
-- ============================================

-- 邮件通知记录表
CREATE TABLE IF NOT EXISTS email_notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    recipient_email VARCHAR(100) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    body TEXT NOT NULL,
    notification_type VARCHAR(20) NOT NULL CHECK(notification_type IN ('Confirmation', 'Cancellation', 'Modification', 'Reminder')),
    status VARCHAR(20) NOT NULL DEFAULT 'Sent' CHECK(status IN ('Sent', 'Failed', 'Pending')),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id)
);

-- ============================================
-- 审计日志表
-- ============================================

-- 操作审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    description TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- ============================================
-- 数据库备份记录表
-- ============================================

-- 备份记录表
CREATE TABLE IF NOT EXISTS backup_records (
    backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_file VARCHAR(255) NOT NULL,
    backup_size INTEGER,
    backup_type VARCHAR(20) DEFAULT 'Manual' CHECK(backup_type IN ('Manual', 'Automatic')),
    status VARCHAR(20) DEFAULT 'Completed' CHECK(status IN ('Completed', 'Failed', 'InProgress')),
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- ============================================
-- 索引创建
-- ============================================

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- 会话表索引
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);

-- 房间表索引
CREATE INDEX IF NOT EXISTS idx_rooms_type ON rooms(room_type_id);
CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status);
CREATE INDEX IF NOT EXISTS idx_rooms_number ON rooms(room_number);

-- 客人表索引
CREATE INDEX IF NOT EXISTS idx_guests_phone ON guests(phone);
CREATE INDEX IF NOT EXISTS idx_guests_email ON guests(email);
CREATE INDEX IF NOT EXISTS idx_guests_name ON guests(last_name, first_name);

-- 预订表索引
CREATE INDEX IF NOT EXISTS idx_reservations_guest ON reservations(guest_id);
CREATE INDEX IF NOT EXISTS idx_reservations_room ON reservations(room_id);
CREATE INDEX IF NOT EXISTS idx_reservations_dates ON reservations(check_in_date, check_out_date);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);

-- 支付表索引
CREATE INDEX IF NOT EXISTS idx_payments_reservation ON payments(reservation_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(payment_status);

-- 季节性定价索引
CREATE INDEX IF NOT EXISTS idx_seasonal_dates ON seasonal_pricing(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_seasonal_room_type ON seasonal_pricing(room_type_id);

-- 审计日志索引
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_operation ON audit_logs(operation_type);
