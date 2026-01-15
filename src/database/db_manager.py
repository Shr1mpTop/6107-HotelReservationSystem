"""
数据库管理器模块
负责SQLite数据库连接、操作和事务管理
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import threading


class DatabaseManager:
    """数据库管理器类"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = None):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = None):
        """初始化数据库管理器"""
        if not hasattr(self, 'initialized'):
            self.db_path = db_path or os.path.join('data', 'hrms.db')
            self.initialized = True
            self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # 使用Row工厂，支持列名访问
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    @contextmanager
    def get_cursor(self, commit: bool = False):
        """
        上下文管理器获取数据库游标
        
        Args:
            commit: 是否在结束时自动提交事务
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def execute_query(self, query: str, params: Tuple = None) -> List[sqlite3.Row]:
        """
        执行查询并返回结果
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        执行更新操作（INSERT, UPDATE, DELETE）
        
        Args:
            query: SQL语句
            params: 参数
            
        Returns:
            受影响的行数
        """
        with self.get_cursor(commit=True) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: Tuple = None) -> int:
        """
        执行插入操作并返回新插入记录的ID
        
        Args:
            query: INSERT语句
            params: 参数
            
        Returns:
            新插入记录的ID
        """
        with self.get_cursor(commit=True) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.lastrowid
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        批量执行SQL语句
        
        Args:
            query: SQL语句
            params_list: 参数列表
            
        Returns:
            受影响的总行数
        """
        with self.get_cursor(commit=True) as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def execute_script(self, script: str):
        """
        执行SQL脚本
        
        Args:
            script: SQL脚本内容
        """
        conn = self.get_connection()
        try:
            conn.executescript(script)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            表是否存在
        """
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,))
        return len(result) > 0
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            表结构信息列表
        """
        query = f"PRAGMA table_info({table_name})"
        rows = self.execute_query(query)
        return [dict(row) for row in rows]
    
    def backup_database(self, backup_path: str):
        """
        备份数据库
        
        Args:
            backup_path: 备份文件路径
        """
        # 确保备份目录存在
        backup_dir = os.path.dirname(backup_path)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # 执行备份
        source = self.get_connection()
        dest = sqlite3.connect(backup_path)
        
        try:
            source.backup(dest)
        finally:
            source.close()
            dest.close()
    
    def get_database_size(self) -> int:
        """
        获取数据库文件大小（字节）
        
        Returns:
            数据库文件大小
        """
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path)
        return 0
    
    def vacuum(self):
        """优化数据库，回收空间"""
        conn = self.get_connection()
        try:
            conn.execute("VACUUM")
            conn.commit()
        finally:
            conn.close()
    
    def row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """
        将sqlite3.Row对象转换为字典
        
        Args:
            row: Row对象
            
        Returns:
            字典形式的数据
        """
        if row is None:
            return None
        return dict(row)
    
    def rows_to_dict_list(self, rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        """
        将Row对象列表转换为字典列表
        
        Args:
            rows: Row对象列表
            
        Returns:
            字典列表
        """
        return [dict(row) for row in rows]


# 创建全局数据库管理器实例
db_manager = DatabaseManager()
