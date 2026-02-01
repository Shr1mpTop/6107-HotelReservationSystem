"""
Database Manager Module
Responsible for SQLite database connection, operation and transaction management
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import threading


class DatabaseManager:
    """Database Manager Class"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = None):
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = None):
        """Initialize database manager"""
        if not hasattr(self, 'initialized'):
            self.db_path = db_path or os.path.join('data', 'hrms.db')
            self.initialized = True
            self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Use Row factory, support column name access
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    @contextmanager
    def get_cursor(self, commit: bool = False):
        """
        Context manager to get database cursor
        
        Args:
            commit: Whether to automatically commit transaction at the end
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
        Execute query and return results
        
        Args:
            query: SQL query statement
            params: Query parameters
            
        Returns:
            List of query results
        """
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        Execute update operation (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL statement
            params: Parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_cursor(commit=True) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: Tuple = None) -> int:
        """
        Execute insert operation and return ID of newly inserted record
        
        Args:
            query: INSERT statement
            params: Parameters
            
        Returns:
            ID of newly inserted record
        """
        with self.get_cursor(commit=True) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.lastrowid
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute SQL statements in batch
        
        Args:
            query: SQL statement
            params_list: List of parameters
            
        Returns:
            Total number of affected rows
        """
        with self.get_cursor(commit=True) as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def execute_script(self, script: str):
        """
        Execute SQL script
        
        Args:
            script: SQL script content
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
        Check if table exists
        
        Args:
            table_name: Table name
            
        Returns:
            Whether table exists
        """
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.execute_query(query, (table_name,))
        return len(result) > 0
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get table structure information
        
        Args:
            table_name: Table name
            
        Returns:
            List of table structure information
        """
        query = f"PRAGMA table_info({table_name})"
        rows = self.execute_query(query)
        return [dict(row) for row in rows]
    
    def backup_database(self, backup_path: str):
        """
        Backup database
        
        Args:
            backup_path: Backup file path
        """
        # Ensure backup directory exists
        backup_dir = os.path.dirname(backup_path)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Perform backup
        source = self.get_connection()
        dest = sqlite3.connect(backup_path)
        
        try:
            source.backup(dest)
        finally:
            source.close()
            dest.close()
    
    def get_database_size(self) -> int:
        """
        Get database file size (bytes)
        
        Returns:
            Database file size
        """
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path)
        return 0
    
    def vacuum(self):
        """Optimize database, reclaim space"""
        conn = self.get_connection()
        try:
            conn.execute("VACUUM")
            conn.commit()
        finally:
            conn.close()
    
    def row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """
        Convert sqlite3.Row object to dictionary
        
        Args:
            row: Row object
            
        Returns:
            Data in dictionary form
        """
        if row is None:
            return None
        return dict(row)
    
    def rows_to_dict_list(self, rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
        """
        Convert list of Row objects to list of dictionaries
        
        Args:
            rows: List of Row objects
            
        Returns:
            List of dictionaries
        """
        return [dict(row) for row in rows]


# Create global database manager instance
db_manager = DatabaseManager()
