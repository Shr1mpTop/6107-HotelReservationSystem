"""
Authentication Service Module
Handles user login, logout and session management
"""

import bcrypt
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database.db_manager import db_manager


class AuthService:
    """Authentication Service Class"""

    # Session timeout (seconds) - 30 minutes
    SESSION_TIMEOUT = 1800

    # Current active sessions (memory storage)
    _active_sessions: Dict[str, Dict[str, Any]] = {}
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify password
        
        Args:
            password: Plain text password
            password_hash: Hashed password
            
        Returns:
            Whether password matches
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate session token"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def login(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        User login
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Returns user info and session token on success, None on failure
        """
        # Query user
        query = """
            SELECT user_id, username, password_hash, full_name, email, 
                   phone, role, is_active
            FROM users
            WHERE username = ? AND is_active = 1
        """
        result = db_manager.execute_query(query, (username,))
        
        if not result:
            return None
        
        user = dict(result[0])
        
        # Verify password
        if not cls.verify_password(password, user['password_hash']):
            return None
        
        # Generate session token
        session_token = cls.generate_session_token()
        
        # Save session to database
        session_query = """
            INSERT INTO user_sessions (user_id, session_token, login_time, last_activity)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        session_id = db_manager.execute_insert(
            session_query, 
            (user['user_id'], session_token)
        )
        
        # Update user's last login time
        update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?"
        db_manager.execute_update(update_query, (user['user_id'],))
        
        # Save to memory session
        session_info = {
            'session_id': session_id,
            'user_id': user['user_id'],
            'username': user['username'],
            'full_name': user['full_name'],
            'role': user['role'],
            'email': user['email'],
            'phone': user['phone'],
            'login_time': datetime.now(),
            'last_activity': datetime.now()
        }
        cls._active_sessions[session_token] = session_info
        
        # Record audit log
        cls._log_audit(
            user['user_id'],
            'LOGIN',
            'users',
            user['user_id'],
            None,
            f"User {username} logged in successfully"
        )
        
        return {
            'session_token': session_token,
            'user': session_info
        }
    
    @classmethod
    def logout(cls, session_token: str) -> bool:
        """
        User logout
        
        Args:
            session_token: Session token
            
        Returns:
            Whether logout was successful
        """
        if session_token not in cls._active_sessions:
            return False
        
        session = cls._active_sessions[session_token]
        
        # Record audit log
        cls._log_audit(
            session['user_id'],
            'LOGOUT',
            'users',
            session['user_id'],
            None,
            f"User {session['username']} logged out"
        )
        
        # Mark session as inactive in database
        query = "UPDATE user_sessions SET is_active = 0 WHERE session_token = ?"
        db_manager.execute_update(query, (session_token,))
        
        # Remove session from memory
        del cls._active_sessions[session_token]
        
        return True
    
    @classmethod
    def validate_session(cls, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate session validity
        
        Args:
            session_token: Session token
            
        Returns:
            Returns user info if valid, None if invalid
        """
        if session_token not in cls._active_sessions:
            return None
        
        session = cls._active_sessions[session_token]
        
        # Check if session has timed out
        time_diff = (datetime.now() - session['last_activity']).total_seconds()
        if time_diff > cls.SESSION_TIMEOUT:
            # Session timed out, auto logout
            cls.logout(session_token)
            return None
        
        # Update last activity time
        session['last_activity'] = datetime.now()
        
        # Update activity time in database
        query = "UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_token = ?"
        db_manager.execute_update(query, (session_token,))
        
        return session
    
    @classmethod
    def get_session_info(cls, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get session information
        
        Args:
            session_token: Session token
            
        Returns:
            Session information
        """
        return cls._active_sessions.get(session_token)
    
    @classmethod
    def check_permission(cls, session_token: str, required_roles: list) -> bool:
        """
        Check user permissions
        
        Args:
            session_token: Session token
            required_roles: List of required roles
            
        Returns:
            Whether user has permission
        """
        session = cls.validate_session(session_token)
        if not session:
            return False
        
        return session['role'] in required_roles
    
    @classmethod
    def is_admin(cls, session_token: str) -> bool:
        """Check if user is admin"""
        return cls.check_permission(session_token, ['admin'])
    
    @classmethod
    def is_front_desk(cls, session_token: str) -> bool:
        """Check if user is front desk staff"""
        return cls.check_permission(session_token, ['admin', 'front_desk'])
    
    @classmethod
    def is_housekeeping(cls, session_token: str) -> bool:
        """Check if user is housekeeping staff"""
        return cls.check_permission(session_token, ['admin', 'housekeeping'])
    
    @classmethod
    def get_active_sessions_count(cls) -> int:
        """Get active sessions count"""
        return len(cls._active_sessions)
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Clean up expired sessions"""
        expired_tokens = []
        current_time = datetime.now()
        
        for token, session in cls._active_sessions.items():
            time_diff = (current_time - session['last_activity']).total_seconds()
            if time_diff > cls.SESSION_TIMEOUT:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            cls.logout(token)
    
    @staticmethod
    def _log_audit(user_id: int, operation_type: str, table_name: str,
                   record_id: int, old_value: str, description: str):
        """
        Record audit log
        
        Args:
            user_id: User ID
            operation_type: Operation type
            table_name: Table name
            record_id: Record ID
            old_value: Old value
            description: Description
        """
        query = """
            INSERT INTO audit_logs 
            (user_id, operation_type, table_name, record_id, old_value, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            db_manager.execute_insert(
                query,
                (user_id, operation_type, table_name, record_id, old_value, description)
            )
        except Exception as e:
            print(f"Failed to record audit log: {e}")
    
    @classmethod
    def change_password(cls, user_id: int, old_password: str, new_password: str) -> tuple:
        """
        Change password
        
        Args:
            user_id: User ID
            old_password: Old password
            new_password: New password
            
        Returns:
            (Success status, Message)
        """
        # Get user's current password hash
        query = "SELECT password_hash FROM users WHERE user_id = ?"
        result = db_manager.execute_query(query, (user_id,))
        
        if not result:
            return False, "User does not exist"
        
        current_hash = result[0]['password_hash']
        
        # Verify old password
        if not cls.verify_password(old_password, current_hash):
            return False, "Old password is incorrect"
        
        # Update password
        new_hash = cls.hash_password(new_password)
        update_query = "UPDATE users SET password_hash = ? WHERE user_id = ?"
        db_manager.execute_update(update_query, (new_hash, user_id))
        
        # Record audit log
        cls._log_audit(
            user_id,
            'PASSWORD_CHANGE',
            'users',
            user_id,
            None,
            "User changed password"
        )
        
        return True, "Password changed successfully"
