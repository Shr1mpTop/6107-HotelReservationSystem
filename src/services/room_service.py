"""
Room Service Module
Handles room queries, status management and other room-related functions
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from database.db_manager import db_manager


class RoomService:
    """Room Service Class"""
    
    # Room status constants
    STATUS_CLEAN = 'Clean'
    STATUS_DIRTY = 'Dirty'
    STATUS_OCCUPIED = 'Occupied'
    STATUS_MAINTENANCE = 'Maintenance'
    
    @staticmethod
    def get_available_rooms(check_in_date: str, check_out_date: str, 
                           room_type_id: int = None) -> List[Dict[str, Any]]:
        """
        Query available rooms
        
        Args:
            check_in_date: Check-in date (YYYY-MM-DD)
            check_out_date: Check-out date (YYYY-MM-DD)
            room_type_id: Room type ID (optional)
            
        Returns:
            Available room list
        """
        # Base query
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
        Get room information by ID
        
        Args:
            room_id: Room ID
            
        Returns:
            Room information
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
        Get room information by room number
        
        Args:
            room_number: Room number
            
        Returns:
            Room information
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
        Update room status
        
        Args:
            room_id: Room ID
            new_status: New status
            user_id: Operating user ID
            
        Returns:
            (Success status, Message)
        """
        # Validate status
        valid_statuses = [
            RoomService.STATUS_CLEAN,
            RoomService.STATUS_DIRTY,
            RoomService.STATUS_OCCUPIED,
            RoomService.STATUS_MAINTENANCE
        ]
        
        if new_status not in valid_statuses:
            return False, f"Invalid room status: {new_status}"
        
        # Get current status
        current_room = RoomService.get_room_by_id(room_id)
        if not current_room:
            return False, "Room does not exist"
        
        old_status = current_room['status']
        
        # Update status
        query = """
            UPDATE rooms 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE room_id = ?
        """
        
        try:
            db_manager.execute_update(query, (new_status, room_id))
            
            # Record audit log
            if user_id:
                RoomService._log_audit(
                    user_id,
                    'STATUS_UPDATE',
                    'rooms',
                    room_id,
                    f"Status: {old_status}",
                    f"Changed room {current_room['room_number']} status from {old_status} to {new_status}"
                )
            
            return True, f"Room status updated to: {new_status}"
            
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    @staticmethod
    def list_all_rooms(status: str = None, room_type_id: int = None,
                      floor: int = None) -> List[Dict[str, Any]]:
        """
        List all rooms
        
        Args:
            status: Room status filter
            room_type_id: Room type ID filter
            floor: Floor filter
            
        Returns:
            Room list
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
        Get all active room types
        
        Returns:
            Room type list
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
        Get room type information by ID
        
        Args:
            room_type_id: Room type ID
            
        Returns:
            Room type information
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
        Add new room type
        
        Args:
            type_name: Room type name
            description: Description
            base_price: Base price
            max_occupancy: Maximum occupancy
            amenities: Amenities
            user_id: Operating user ID
            
        Returns:
            (Success status, Message, Room type ID)
        """
        # Check if room type name already exists
        check_query = "SELECT room_type_id FROM room_types WHERE type_name = ?"
        existing = db_manager.execute_query(check_query, (type_name,))
        
        if existing:
            return False, "Room type name already exists", None
        
        # Insert new room type
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
            
            # Record audit log
            if user_id:
                RoomService._log_audit(
                    user_id,
                    'CREATE',
                    'room_types',
                    room_type_id,
                    None,
                    f"Added new room type: {type_name}"
                )
            
            return True, "Room type added successfully", room_type_id
            
        except Exception as e:
            return False, f"Addition failed: {str(e)}", None
    
    @staticmethod
    def update_room_type(room_type_id: int, type_name: str = None,
                        description: str = None, base_price: float = None,
                        max_occupancy: int = None, amenities: str = None,
                        user_id: int = None) -> tuple:
        """
        Update room type information
        
        Args:
            room_type_id: Room type ID
            type_name: Room type name
            description: Description
            base_price: Base price
            max_occupancy: Maximum occupancy
            amenities: Amenities
            user_id: Operating user ID
            
        Returns:
            (Success status, Message)
        """
        # Get current room type
        current = RoomService.get_room_type_by_id(room_type_id)
        if not current:
            return False, "Room type does not exist"
        
        # Build update fields
        updates = []
        params = []
        
        if type_name:
            # Check if new name conflicts with other room types
            check_query = """
                SELECT room_type_id FROM room_types 
                WHERE type_name = ? AND room_type_id != ?
            """
            existing = db_manager.execute_query(check_query, (type_name, room_type_id))
            if existing:
                return False, "Room type name is already in use"
            
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
            return False, "No content needs to be updated"
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(room_type_id)
        
        # Execute update
        query = f"UPDATE room_types SET {', '.join(updates)} WHERE room_type_id = ?"
        
        try:
            db_manager.execute_update(query, tuple(params))
            
            # Record audit log
            if user_id:
                RoomService._log_audit(
                    user_id,
                    'UPDATE',
                    'room_types',
                    room_type_id,
                    str(current),
                    f"Updated room type {room_type_id}"
                )
            
            return True, "Room type updated successfully"
            
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    @staticmethod
    def add_room(room_number: str, room_type_id: int, floor: int,
                user_id: int = None) -> tuple:
        """
        Add new room
        
        Args:
            room_number: Room number
            room_type_id: Room type ID
            floor: Floor
            user_id: Operating user ID
            
        Returns:
            (Success status, Message, Room ID)
        """
        # Check if room number already exists
        check_query = "SELECT room_id FROM rooms WHERE room_number = ?"
        existing = db_manager.execute_query(check_query, (room_number,))
        
        if existing:
            return False, "Room number already exists", None
        
        # Validate room type exists
        room_type = RoomService.get_room_type_by_id(room_type_id)
        if not room_type:
            return False, "Room type does not exist", None
        
        # Insert new room
        query = """
            INSERT INTO rooms (room_number, room_type_id, floor, status)
            VALUES (?, ?, ?, 'Clean')
        """
        
        try:
            room_id = db_manager.execute_insert(
                query,
                (room_number, room_type_id, floor)
            )
            
            # Record audit log
            if user_id:
                RoomService._log_audit(
                    user_id,
                    'CREATE',
                    'rooms',
                    room_id,
                    None,
                    f"Added new room: {room_number}"
                )
            
            return True, "Room added successfully", room_id
            
        except Exception as e:
            return False, f"Addition failed: {str(e)}", None
    
    @staticmethod
    def get_room_statistics() -> Dict[str, Any]:
        """
        Get room statistics information
        
        Returns:
            Statistics data dictionary
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
        """Record audit log"""
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
