"""
房间服务模块
处理房间查询、状态管理等功能
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from database.db_manager import db_manager


class RoomService:
    """房间服务类"""
    
    # 房间状态常量
    STATUS_CLEAN = 'Clean'
    STATUS_DIRTY = 'Dirty'
    STATUS_OCCUPIED = 'Occupied'
    STATUS_MAINTENANCE = 'Maintenance'
    
    @staticmethod
    def get_available_rooms(check_in_date: str, check_out_date: str, 
                           room_type_id: int = None) -> List[Dict[str, Any]]:
        """
        查询可用房间
        
        Args:
            check_in_date: 入住日期（YYYY-MM-DD）
            check_out_date: 退房日期（YYYY-MM-DD）
            room_type_id: 房型ID（可选）
            
        Returns:
            可用房间列表
        """
        # 基础查询
        query = """
            SELECT r.room_id, r.room_number, r.floor, r.status,
                   rt.room_type_id, rt.type_name, rt.description, 
                   rt.base_price, rt.max_occupancy, rt.amenities
            FROM rooms r
            JOIN room_types rt ON r.room_type_id = rt.room_type_id
            WHERE r.is_active = 1 
                AND rt.is_active = 1
                AND r.status = 'Clean'
                AND r.room_id NOT IN (
                    SELECT room_id 
                    FROM reservations
                    WHERE status IN ('Confirmed', 'CheckedIn')
                        AND (
                            (check_in_date < ? AND check_out_date > ?)
                            OR (check_in_date >= ? AND check_in_date < ?)
                        )
                )
        """
        
        params = [check_out_date, check_in_date, check_in_date, check_out_date]
        
        if room_type_id:
            query += " AND rt.room_type_id = ?"
            params.append(room_type_id)
        
        query += " ORDER BY rt.type_name, r.room_number"
        
        result = db_manager.execute_query(query, tuple(params))
        return db_manager.rows_to_dict_list(result)
    
    @staticmethod
    def get_room_by_id(room_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取房间信息
        
        Args:
            room_id: 房间ID
            
        Returns:
            房间信息
        """
        query = """
            SELECT r.*, rt.type_name, rt.description, rt.base_price, 
                   rt.max_occupancy, rt.amenities
            FROM rooms r
            JOIN room_types rt ON r.room_type_id = rt.room_type_id
            WHERE r.room_id = ?
        """
        result = db_manager.execute_query(query, (room_id,))
        
        if result:
            return dict(result[0])
        return None
    
    @staticmethod
    def get_room_by_number(room_number: str) -> Optional[Dict[str, Any]]:
        """
        根据房间号获取房间信息
        
        Args:
            room_number: 房间号
            
        Returns:
            房间信息
        """
        query = """
            SELECT r.*, rt.type_name, rt.description, rt.base_price, 
                   rt.max_occupancy, rt.amenities
            FROM rooms r
            JOIN room_types rt ON r.room_type_id = rt.room_type_id
            WHERE r.room_number = ?
        """
        result = db_manager.execute_query(query, (room_number,))
        
        if result:
            return dict(result[0])
        return None
    
    @staticmethod
    def update_room_status(room_id: int, new_status: str, 
                          user_id: int = None) -> tuple:
        """
        更新房间状态
        
        Args:
            room_id: 房间ID
            new_status: 新状态
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息)
        """
        # 验证状态
        valid_statuses = [
            RoomService.STATUS_CLEAN,
            RoomService.STATUS_DIRTY,
            RoomService.STATUS_OCCUPIED,
            RoomService.STATUS_MAINTENANCE
        ]
        
        if new_status not in valid_statuses:
            return False, f"无效的房间状态: {new_status}"
        
        # 获取当前状态
        current_room = RoomService.get_room_by_id(room_id)
        if not current_room:
            return False, "房间不存在"
        
        old_status = current_room['status']
        
        # 更新状态
        query = """
            UPDATE rooms 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE room_id = ?
        """
        
        try:
            db_manager.execute_update(query, (new_status, room_id))
            
            # 记录审计日志
            if user_id:
                RoomService._log_audit(
                    user_id,
                    'STATUS_UPDATE',
                    'rooms',
                    room_id,
                    f"Status: {old_status}",
                    f"Changed room {current_room['room_number']} status from {old_status} to {new_status}"
                )
            
            return True, f"房间状态已更新为: {new_status}"
            
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    @staticmethod
    def list_all_rooms(status: str = None, room_type_id: int = None,
                      floor: int = None) -> List[Dict[str, Any]]:
        """
        列出所有房间
        
        Args:
            status: 房间状态过滤
            room_type_id: 房型ID过滤
            floor: 楼层过滤
            
        Returns:
            房间列表
        """
        query = """
            SELECT r.*, rt.type_name, rt.base_price, rt.max_occupancy
            FROM rooms r
            JOIN room_types rt ON r.room_type_id = rt.room_type_id
            WHERE r.is_active = 1
        """
        params = []
        
        if status:
            query += " AND r.status = ?"
            params.append(status)
        
        if room_type_id:
            query += " AND r.room_type_id = ?"
            params.append(room_type_id)
        
        if floor is not None:
            query += " AND r.floor = ?"
            params.append(floor)
        
        query += " ORDER BY r.room_number"
        
        result = db_manager.execute_query(query, tuple(params) if params else None)
        return db_manager.rows_to_dict_list(result)
    
    @staticmethod
    def get_room_types() -> List[Dict[str, Any]]:
        """
        获取所有活动的房型
        
        Returns:
            房型列表
        """
        query = """
            SELECT * FROM room_types 
            WHERE is_active = 1
            ORDER BY base_price
        """
        result = db_manager.execute_query(query)
        return db_manager.rows_to_dict_list(result)
    
    @staticmethod
    def get_room_type_by_id(room_type_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取房型信息
        
        Args:
            room_type_id: 房型ID
            
        Returns:
            房型信息
        """
        query = "SELECT * FROM room_types WHERE room_type_id = ?"
        result = db_manager.execute_query(query, (room_type_id,))
        
        if result:
            return dict(result[0])
        return None
    
    @staticmethod
    def add_room_type(type_name: str, description: str, base_price: float,
                     max_occupancy: int, amenities: str, 
                     user_id: int = None) -> tuple:
        """
        添加新房型
        
        Args:
            type_name: 房型名称
            description: 描述
            base_price: 基础价格
            max_occupancy: 最大入住人数
            amenities: 设施
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息, 房型ID)
        """
        # 检查房型名称是否已存在
        check_query = "SELECT room_type_id FROM room_types WHERE type_name = ?"
        existing = db_manager.execute_query(check_query, (type_name,))
        
        if existing:
            return False, "房型名称已存在", None
        
        # 插入新房型
        query = """
            INSERT INTO room_types 
            (type_name, description, base_price, max_occupancy, amenities)
            VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            room_type_id = db_manager.execute_insert(
                query,
                (type_name, description, base_price, max_occupancy, amenities)
            )
            
            # 记录审计日志
            if user_id:
                RoomService._log_audit(
                    user_id,
                    'CREATE',
                    'room_types',
                    room_type_id,
                    None,
                    f"Added new room type: {type_name}"
                )
            
            return True, "房型添加成功", room_type_id
            
        except Exception as e:
            return False, f"添加失败: {str(e)}", None
    
    @staticmethod
    def update_room_type(room_type_id: int, type_name: str = None,
                        description: str = None, base_price: float = None,
                        max_occupancy: int = None, amenities: str = None,
                        user_id: int = None) -> tuple:
        """
        更新房型信息
        
        Args:
            room_type_id: 房型ID
            type_name: 房型名称
            description: 描述
            base_price: 基础价格
            max_occupancy: 最大入住人数
            amenities: 设施
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息)
        """
        # 获取当前房型
        current = RoomService.get_room_type_by_id(room_type_id)
        if not current:
            return False, "房型不存在"
        
        # 构建更新字段
        updates = []
        params = []
        
        if type_name:
            # 检查新名称是否与其他房型重复
            check_query = """
                SELECT room_type_id FROM room_types 
                WHERE type_name = ? AND room_type_id != ?
            """
            existing = db_manager.execute_query(check_query, (type_name, room_type_id))
            if existing:
                return False, "房型名称已被使用"
            
            updates.append("type_name = ?")
            params.append(type_name)
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if base_price is not None:
            updates.append("base_price = ?")
            params.append(base_price)
        
        if max_occupancy is not None:
            updates.append("max_occupancy = ?")
            params.append(max_occupancy)
        
        if amenities is not None:
            updates.append("amenities = ?")
            params.append(amenities)
        
        if not updates:
            return False, "没有需要更新的内容"
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(room_type_id)
        
        # 执行更新
        query = f"UPDATE room_types SET {', '.join(updates)} WHERE room_type_id = ?"
        
        try:
            db_manager.execute_update(query, tuple(params))
            
            # 记录审计日志
            if user_id:
                RoomService._log_audit(
                    user_id,
                    'UPDATE',
                    'room_types',
                    room_type_id,
                    str(current),
                    f"Updated room type {room_type_id}"
                )
            
            return True, "房型更新成功"
            
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    @staticmethod
    def add_room(room_number: str, room_type_id: int, floor: int,
                user_id: int = None) -> tuple:
        """
        添加新房间
        
        Args:
            room_number: 房间号
            room_type_id: 房型ID
            floor: 楼层
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息, 房间ID)
        """
        # 检查房间号是否已存在
        check_query = "SELECT room_id FROM rooms WHERE room_number = ?"
        existing = db_manager.execute_query(check_query, (room_number,))
        
        if existing:
            return False, "房间号已存在", None
        
        # 验证房型是否存在
        room_type = RoomService.get_room_type_by_id(room_type_id)
        if not room_type:
            return False, "房型不存在", None
        
        # 插入新房间
        query = """
            INSERT INTO rooms (room_number, room_type_id, floor, status)
            VALUES (?, ?, ?, 'Clean')
        """
        
        try:
            room_id = db_manager.execute_insert(
                query,
                (room_number, room_type_id, floor)
            )
            
            # 记录审计日志
            if user_id:
                RoomService._log_audit(
                    user_id,
                    'CREATE',
                    'rooms',
                    room_id,
                    None,
                    f"Added new room: {room_number}"
                )
            
            return True, "房间添加成功", room_id
            
        except Exception as e:
            return False, f"添加失败: {str(e)}", None
    
    @staticmethod
    def get_room_statistics() -> Dict[str, Any]:
        """
        获取房间统计信息
        
        Returns:
            统计数据字典
        """
        query = """
            SELECT 
                COUNT(*) as total_rooms,
                SUM(CASE WHEN status = 'Clean' THEN 1 ELSE 0 END) as clean_rooms,
                SUM(CASE WHEN status = 'Dirty' THEN 1 ELSE 0 END) as dirty_rooms,
                SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) as occupied_rooms,
                SUM(CASE WHEN status = 'Maintenance' THEN 1 ELSE 0 END) as maintenance_rooms
            FROM rooms
            WHERE is_active = 1
        """
        result = db_manager.execute_query(query)
        
        if result:
            return dict(result[0])
        return {}
    
    @staticmethod
    def _log_audit(user_id: int, operation_type: str, table_name: str,
                   record_id: int, old_value: str, description: str):
        """记录审计日志"""
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
