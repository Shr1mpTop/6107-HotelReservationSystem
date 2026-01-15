"""
定价服务模块
处理房间定价计算，包括基础价格和季节性定价
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from database.db_manager import db_manager


class PricingService:
    """定价服务类"""
    
    @staticmethod
    def get_room_base_price(room_type_id: int) -> Optional[float]:
        """
        获取房型基础价格
        
        Args:
            room_type_id: 房型ID
            
        Returns:
            基础价格
        """
        query = "SELECT base_price FROM room_types WHERE room_type_id = ?"
        result = db_manager.execute_query(query, (room_type_id,))
        
        if result:
            return float(result[0]['base_price'])
        return None
    
    @staticmethod
    def get_seasonal_pricing(room_type_id: int, date: str) -> Optional[Dict[str, Any]]:
        """
        获取特定日期的季节性定价规则
        
        Args:
            room_type_id: 房型ID
            date: 日期（YYYY-MM-DD格式）
            
        Returns:
            季节性定价规则信息
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
        计算特定日期的房间价格
        
        Args:
            room_type_id: 房型ID
            date: 日期（YYYY-MM-DD格式）
            
        Returns:
            当日价格
        """
        # 获取基础价格
        base_price = PricingService.get_room_base_price(room_type_id)
        if base_price is None:
            return 0.0
        
        # 检查是否有季节性定价
        seasonal = PricingService.get_seasonal_pricing(room_type_id, date)
        
        if seasonal:
            # 如果有固定价格，使用固定价格
            if seasonal['fixed_price']:
                return float(seasonal['fixed_price'])
            # 否则使用价格乘数
            elif seasonal['price_multiplier']:
                return base_price * float(seasonal['price_multiplier'])
        
        # 返回基础价格
        return base_price
    
    @staticmethod
    def calculate_total_price(room_type_id: int, check_in_date: str, 
                            check_out_date: str) -> Dict[str, Any]:
        """
        计算总价格（包括每日明细）
        
        Args:
            room_type_id: 房型ID
            check_in_date: 入住日期（YYYY-MM-DD）
            check_out_date: 退房日期（YYYY-MM-DD）
            
        Returns:
            包含总价和每日明细的字典
        """
        try:
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d')
        except ValueError:
            return {'total': 0.0, 'nights': 0, 'daily_prices': []}
        
        if check_out <= check_in:
            return {'total': 0.0, 'nights': 0, 'daily_prices': []}
        
        # 计算每日价格
        total_price = 0.0
        daily_prices = []
        current_date = check_in
        
        while current_date < check_out:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_price = PricingService.calculate_daily_price(room_type_id, date_str)
            
            # 获取季节性定价信息（用于显示）
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
        添加季节性定价规则
        
        Args:
            room_type_id: 房型ID
            season_name: 季节名称
            start_date: 开始日期
            end_date: 结束日期
            price_multiplier: 价格乘数
            fixed_price: 固定价格
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息, 定价ID)
        """
        # 验证日期
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end <= start:
                return False, "结束日期必须晚于开始日期", None
        except ValueError:
            return False, "日期格式无效，请使用YYYY-MM-DD格式", None
        
        # 验证价格设置
        if price_multiplier is None and fixed_price is None:
            return False, "必须设置价格乘数或固定价格", None
        
        # 检查日期冲突
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
            return False, f"日期范围与现有规则 '{conflict_info['season_name']}' ({conflict_info['start_date']} 至 {conflict_info['end_date']}) 冲突", None
        
        # 插入新规则
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
            
            # 记录审计日志
            if user_id:
                PricingService._log_audit(
                    user_id,
                    'CREATE',
                    'seasonal_pricing',
                    pricing_id,
                    None,
                    f"Added seasonal pricing '{season_name}' for room type {room_type_id}"
                )
            
            return True, "季节性定价规则添加成功", pricing_id
            
        except Exception as e:
            return False, f"添加失败: {str(e)}", None
    
    @staticmethod
    def update_seasonal_pricing(pricing_id: int, season_name: str = None,
                              start_date: str = None, end_date: str = None,
                              price_multiplier: float = None,
                              fixed_price: float = None,
                              user_id: int = None) -> tuple:
        """
        更新季节性定价规则
        
        Args:
            pricing_id: 定价规则ID
            season_name: 季节名称
            start_date: 开始日期
            end_date: 结束日期
            price_multiplier: 价格乘数
            fixed_price: 固定价格
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息)
        """
        # 获取当前规则
        current_query = "SELECT * FROM seasonal_pricing WHERE pricing_id = ?"
        current = db_manager.execute_query(current_query, (pricing_id,))
        
        if not current:
            return False, "定价规则不存在"
        
        current_rule = dict(current[0])
        
        # 构建更新字段
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
            return False, "没有需要更新的内容"
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(pricing_id)
        
        # 执行更新
        query = f"UPDATE seasonal_pricing SET {', '.join(updates)} WHERE pricing_id = ?"
        
        try:
            db_manager.execute_update(query, tuple(params))
            
            # 记录审计日志
            if user_id:
                PricingService._log_audit(
                    user_id,
                    'UPDATE',
                    'seasonal_pricing',
                    pricing_id,
                    str(current_rule),
                    f"Updated seasonal pricing rule {pricing_id}"
                )
            
            return True, "定价规则更新成功"
            
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    @staticmethod
    def delete_seasonal_pricing(pricing_id: int, user_id: int = None) -> tuple:
        """
        删除季节性定价规则（软删除）
        
        Args:
            pricing_id: 定价规则ID
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息)
        """
        query = "UPDATE seasonal_pricing SET is_active = 0 WHERE pricing_id = ?"
        
        try:
            rowcount = db_manager.execute_update(query, (pricing_id,))
            
            if rowcount == 0:
                return False, "定价规则不存在"
            
            # 记录审计日志
            if user_id:
                PricingService._log_audit(
                    user_id,
                    'DELETE',
                    'seasonal_pricing',
                    pricing_id,
                    None,
                    f"Deleted seasonal pricing rule {pricing_id}"
                )
            
            return True, "定价规则删除成功"
            
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    @staticmethod
    def list_seasonal_pricing(room_type_id: int = None, 
                            active_only: bool = True) -> List[Dict[str, Any]]:
        """
        列出季节性定价规则
        
        Args:
            room_type_id: 房型ID（None表示所有房型）
            active_only: 是否只显示活动规则
            
        Returns:
            定价规则列表
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
