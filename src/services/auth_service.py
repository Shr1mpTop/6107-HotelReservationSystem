"""
认证服务模块
处理用户登录、登出和会话管理
"""

import bcrypt
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database.db_manager import db_manager


class AuthService:
    """认证服务类"""
    
    # 会话超时时间（秒）- 30分钟
    SESSION_TIMEOUT = 1800
    
    # 当前活动会话（内存存储）
    _active_sessions: Dict[str, Dict[str, Any]] = {}
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            password_hash: 哈希密码
            
        Returns:
            密码是否匹配
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
        """生成会话令牌"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def login(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            成功返回用户信息和会话令牌，失败返回None
        """
        # 查询用户
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
        
        # 验证密码
        if not cls.verify_password(password, user['password_hash']):
            return None
        
        # 生成会话令牌
        session_token = cls.generate_session_token()
        
        # 保存会话到数据库
        session_query = """
            INSERT INTO user_sessions (user_id, session_token, login_time, last_activity)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        session_id = db_manager.execute_insert(
            session_query, 
            (user['user_id'], session_token)
        )
        
        # 更新用户最后登录时间
        update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?"
        db_manager.execute_update(update_query, (user['user_id'],))
        
        # 保存到内存会话
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
        
        # 记录审计日志
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
        用户登出
        
        Args:
            session_token: 会话令牌
            
        Returns:
            是否成功登出
        """
        if session_token not in cls._active_sessions:
            return False
        
        session = cls._active_sessions[session_token]
        
        # 记录审计日志
        cls._log_audit(
            session['user_id'],
            'LOGOUT',
            'users',
            session['user_id'],
            None,
            f"User {session['username']} logged out"
        )
        
        # 从数据库中标记会话为非活动
        query = "UPDATE user_sessions SET is_active = 0 WHERE session_token = ?"
        db_manager.execute_update(query, (session_token,))
        
        # 从内存中删除会话
        del cls._active_sessions[session_token]
        
        return True
    
    @classmethod
    def validate_session(cls, session_token: str) -> Optional[Dict[str, Any]]:
        """
        验证会话有效性
        
        Args:
            session_token: 会话令牌
            
        Returns:
            有效返回用户信息，无效返回None
        """
        if session_token not in cls._active_sessions:
            return None
        
        session = cls._active_sessions[session_token]
        
        # 检查会话是否超时
        time_diff = (datetime.now() - session['last_activity']).total_seconds()
        if time_diff > cls.SESSION_TIMEOUT:
            # 会话超时，自动登出
            cls.logout(session_token)
            return None
        
        # 更新最后活动时间
        session['last_activity'] = datetime.now()
        
        # 更新数据库中的活动时间
        query = "UPDATE user_sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_token = ?"
        db_manager.execute_update(query, (session_token,))
        
        return session
    
    @classmethod
    def get_session_info(cls, session_token: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息
        
        Args:
            session_token: 会话令牌
            
        Returns:
            会话信息
        """
        return cls._active_sessions.get(session_token)
    
    @classmethod
    def check_permission(cls, session_token: str, required_roles: list) -> bool:
        """
        检查用户权限
        
        Args:
            session_token: 会话令牌
            required_roles: 需要的角色列表
            
        Returns:
            是否有权限
        """
        session = cls.validate_session(session_token)
        if not session:
            return False
        
        return session['role'] in required_roles
    
    @classmethod
    def is_admin(cls, session_token: str) -> bool:
        """检查是否是管理员"""
        return cls.check_permission(session_token, ['admin'])
    
    @classmethod
    def is_front_desk(cls, session_token: str) -> bool:
        """检查是否是前台员工"""
        return cls.check_permission(session_token, ['admin', 'front_desk'])
    
    @classmethod
    def is_housekeeping(cls, session_token: str) -> bool:
        """检查是否是客房员工"""
        return cls.check_permission(session_token, ['admin', 'housekeeping'])
    
    @classmethod
    def get_active_sessions_count(cls) -> int:
        """获取活动会话数量"""
        return len(cls._active_sessions)
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """清理过期会话"""
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
        记录审计日志
        
        Args:
            user_id: 用户ID
            operation_type: 操作类型
            table_name: 表名
            record_id: 记录ID
            old_value: 旧值
            description: 描述
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
            print(f"记录审计日志失败: {e}")
    
    @classmethod
    def change_password(cls, user_id: int, old_password: str, new_password: str) -> tuple:
        """
        修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            (是否成功, 消息)
        """
        # 获取用户当前密码哈希
        query = "SELECT password_hash FROM users WHERE user_id = ?"
        result = db_manager.execute_query(query, (user_id,))
        
        if not result:
            return False, "用户不存在"
        
        current_hash = result[0]['password_hash']
        
        # 验证旧密码
        if not cls.verify_password(old_password, current_hash):
            return False, "旧密码不正确"
        
        # 更新密码
        new_hash = cls.hash_password(new_password)
        update_query = "UPDATE users SET password_hash = ? WHERE user_id = ?"
        db_manager.execute_update(update_query, (new_hash, user_id))
        
        # 记录审计日志
        cls._log_audit(
            user_id,
            'PASSWORD_CHANGE',
            'users',
            user_id,
            None,
            "User changed password"
        )
        
        return True, "密码修改成功"
