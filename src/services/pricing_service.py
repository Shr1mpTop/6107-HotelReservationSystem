"""
Pricing Service Module
Handles room pricing calculations, including base prices and seasonal pricing
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from database.db_manager import db_manager


class PricingService:
    """Pricing Service Class"""
    
    @staticmethod
    def get_room_base_price(room_type_id: int) -> Optional[float]:
        """
        Get room type base price
        
        Args:
            room_type_id: Room type ID
            
        Returns:
            Base price
        """
        query = "SELECT base_price FROM room_types WHERE room_type_id = ?"
        result = db_manager.execute_query(query, (room_type_id,))
        
        if result:
            return float(result[0]['base_price'])
        return None
    
    @staticmethod
    def get_seasonal_pricing(room_type_id: int, date: str) -> Optional[Dict[str, Any]]:
        """
        Get seasonal pricing rule for specific date
        
        Args:
            room_type_id: Room type ID
            date: Date in YYYY-MM-DD format
            
        Returns:
            Seasonal pricing rule information
        """
        query = """
            SELECT pricing_id, season_name, price_multiplier, fixed_price
            FROM seasonal_pricing
            WHERE room_type_id = ? 
                AND ? BETWEEN start_date AND end_date
                AND is_active = 1
            ORDER BY pricing_id DESC
            LIMIT 1
        """
        result = db_manager.execute_query(query, (room_type_id, date))
        
        if result:
            return dict(result[0])
        return None
    
    @staticmethod
    def calculate_daily_price(room_type_id: int, date: str) -> float:
        """
        Calculate room price for specific date
        
        Args:
            room_type_id: Room type ID
            date: Date in YYYY-MM-DD format
            
        Returns:
            Daily price
        """
        # Get base price
        base_price = PricingService.get_room_base_price(room_type_id)
        if base_price is None:
            return 0.0
        
        # Check for seasonal pricing
        seasonal = PricingService.get_seasonal_pricing(room_type_id, date)
        
        if seasonal:
            # If fixed price exists, use fixed price
            if seasonal['fixed_price']:
                return float(seasonal['fixed_price'])
            # Otherwise use price multiplier
            elif seasonal['price_multiplier']:
                return base_price * float(seasonal['price_multiplier'])
        
        # Return base price
        return base_price
    
    @staticmethod
    def calculate_total_price(room_type_id: int, check_in_date: str, 
                            check_out_date: str) -> Dict[str, Any]:
        """
        Calculate total price (including daily breakdown)
        
        Args:
            room_type_id: Room type ID
            check_in_date: Check-in date (YYYY-MM-DD)
            check_out_date: Check-out date (YYYY-MM-DD)
            
        Returns:
            Dictionary containing total price and daily breakdown
        """
        try:
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d')
        except ValueError:
            return {'total': 0.0, 'nights': 0, 'daily_prices': []}
        
        if check_out <= check_in:
            return {'total': 0.0, 'nights': 0, 'daily_prices': []}
        
        # Calculate daily prices
        total_price = 0.0
        daily_prices = []
        current_date = check_in
        
        while current_date < check_out:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_price = PricingService.calculate_daily_price(room_type_id, date_str)
            
            # Get seasonal pricing info (for display)
            seasonal = PricingService.get_seasonal_pricing(room_type_id, date_str)
            season_name = seasonal['season_name'] if seasonal else None
            
            daily_prices.append({
                'date': date_str,
                'price': daily_price,
                'season': season_name
            })
            
            total_price += daily_price
            current_date += timedelta(days=1)
        
        nights = len(daily_prices)
        
        return {
            'total': round(total_price, 2),
            'nights': nights,
            'daily_prices': daily_prices
        }
    
    @staticmethod
    def add_seasonal_pricing(room_type_id: int, season_name: str,
                           start_date: str, end_date: str,
                           price_multiplier: float = None,
                           fixed_price: float = None,
                           user_id: int = None) -> tuple:
        """
        Add seasonal pricing rule
        
        Args:
            room_type_id: Room type ID
            season_name: Season name
            start_date: Start date
            end_date: End date
            price_multiplier: Price multiplier
            fixed_price: Fixed price
            user_id: Operating user ID
            
        Returns:
            (Success status, Message, Pricing ID)
        """
        # Validate dates
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end <= start:
                return False, "End date must be later than start date", None
        except ValueError:
            return False, "Invalid date format, please use YYYY-MM-DD format", None
        
        # Validate price settings
        if price_multiplier is None and fixed_price is None:
            return False, "Must set either price multiplier or fixed price", None
        
        # Check for date conflicts
        conflict_query = """
            SELECT pricing_id, season_name, start_date, end_date
            FROM seasonal_pricing
            WHERE room_type_id = ? 
                AND is_active = 1
                AND (
                    (start_date <= ? AND end_date >= ?)
                    OR (start_date <= ? AND end_date >= ?)
                    OR (start_date >= ? AND end_date <= ?)
                )
        """
        conflicts = db_manager.execute_query(
            conflict_query,
            (room_type_id, start_date, start_date, end_date, end_date, 
             start_date, end_date)
        )
        
        if conflicts:
            conflict_info = dict(conflicts[0])
            return False, f"Date range conflicts with existing rule '{conflict_info['season_name']}' ({conflict_info['start_date']} to {conflict_info['end_date']})", None
        
        # Insert new rule
        query = """
            INSERT INTO seasonal_pricing 
            (room_type_id, season_name, start_date, end_date, 
             price_multiplier, fixed_price)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        try:
            pricing_id = db_manager.execute_insert(
                query,
                (room_type_id, season_name, start_date, end_date,
                 price_multiplier, fixed_price)
            )
            
            # Record audit log
            if user_id:
                PricingService._log_audit(
                    user_id,
                    'CREATE',
                    'seasonal_pricing',
                    pricing_id,
                    None,
                    f"Added seasonal pricing '{season_name}' for room type {room_type_id}"
                )
            
            return True, "Seasonal pricing rule added successfully", pricing_id
            
        except Exception as e:
            return False, f"Addition failed: {str(e)}", None
    
    @staticmethod
    def update_seasonal_pricing(pricing_id: int, season_name: str = None,
                              start_date: str = None, end_date: str = None,
                              price_multiplier: float = None,
                              fixed_price: float = None,
                              user_id: int = None) -> tuple:
        """
        Update seasonal pricing rule
        
        Args:
            pricing_id: Pricing rule ID
            season_name: Season name
            start_date: Start date
            end_date: End date
            price_multiplier: Price multiplier
            fixed_price: Fixed price
            user_id: Operating user ID
            
        Returns:
            (Success status, Message)
        """
        # Get current rule
        current_query = "SELECT * FROM seasonal_pricing WHERE pricing_id = ?"
        current = db_manager.execute_query(current_query, (pricing_id,))
        
        if not current:
            return False, "Pricing rule does not exist"
        
        current_rule = dict(current[0])
        
        # Build update fields
        updates = []
        params = []
        
        if season_name:
            updates.append("season_name = ?")
            params.append(season_name)
        
        if start_date:
            updates.append("start_date = ?")
            params.append(start_date)
        
        if end_date:
            updates.append("end_date = ?")
            params.append(end_date)
        
        if price_multiplier is not None:
            updates.append("price_multiplier = ?")
            params.append(price_multiplier)
        
        if fixed_price is not None:
            updates.append("fixed_price = ?")
            params.append(fixed_price)
        
        if not updates:
            return False, "No content to update"
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(pricing_id)
        
        # Execute update
        query = f"UPDATE seasonal_pricing SET {', '.join(updates)} WHERE pricing_id = ?"
        
        try:
            db_manager.execute_update(query, tuple(params))
            
            # Record audit log
            if user_id:
                PricingService._log_audit(
                    user_id,
                    'UPDATE',
                    'seasonal_pricing',
                    pricing_id,
                    str(current_rule),
                    f"Updated seasonal pricing rule {pricing_id}"
                )
            
            return True, "Pricing rule updated successfully"
            
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    @staticmethod
    def delete_seasonal_pricing(pricing_id: int, user_id: int = None) -> tuple:
        """
        Delete seasonal pricing rule (soft delete)
        
        Args:
            pricing_id: Pricing rule ID
            user_id: Operating user ID
            
        Returns:
            (Success status, Message)
        """
        query = "UPDATE seasonal_pricing SET is_active = 0 WHERE pricing_id = ?"
        
        try:
            rowcount = db_manager.execute_update(query, (pricing_id,))
            
            if rowcount == 0:
                return False, "Pricing rule does not exist"
            
            # Record audit log
            if user_id:
                PricingService._log_audit(
                    user_id,
                    'DELETE',
                    'seasonal_pricing',
                    pricing_id,
                    None,
                    f"Deleted seasonal pricing rule {pricing_id}"
                )
            
            return True, "Pricing rule deleted successfully"
            
        except Exception as e:
            return False, f"Deletion failed: {str(e)}"
    
    @staticmethod
    def list_seasonal_pricing(room_type_id: int = None, 
                            active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List seasonal pricing rules
        
        Args:
            room_type_id: Room type ID (None for all room types)
            active_only: Whether to show only active rules
            
        Returns:
            List of pricing rules
        """
        query = """
            SELECT sp.*, rt.type_name
            FROM seasonal_pricing sp
            JOIN room_types rt ON sp.room_type_id = rt.room_type_id
            WHERE 1=1
        """
        params = []
        
        if room_type_id:
            query += " AND sp.room_type_id = ?"
            params.append(room_type_id)
        
        if active_only:
            query += " AND sp.is_active = 1"
        
        query += " ORDER BY sp.start_date, sp.room_type_id"
        
        result = db_manager.execute_query(query, tuple(params) if params else None)
        return db_manager.rows_to_dict_list(result)
    
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
