"""
报表服务模块
处理入住率、收入等报表的生成和导出
"""

import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from database.db_manager import db_manager


class ReportService:
    """报表服务类"""
    
    @staticmethod
    def generate_occupancy_report(start_date: str, end_date: str) -> Dict[str, Any]:
        """
        生成入住率报表
        
        Args:
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            
        Returns:
            报表数据字典
        """
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end_dt <= start_dt:
                return {'error': '结束日期必须晚于开始日期'}
        except ValueError:
            return {'error': '日期格式无效'}
        
        # 获取总房间数
        total_rooms_query = "SELECT COUNT(*) as total FROM rooms WHERE is_active = 1"
        total_rooms_result = db_manager.execute_query(total_rooms_query)
        total_rooms = total_rooms_result[0]['total'] if total_rooms_result else 0
        
        if total_rooms == 0:
            return {'error': '没有可用的房间数据'}
        
        # 计算每日入住情况
        daily_data = []
        current_date = start_dt
        
        while current_date <= end_dt:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 查询当日已占用房间数
            occupied_query = """
                SELECT COUNT(DISTINCT room_id) as occupied
                FROM reservations
                WHERE status IN ('Confirmed', 'CheckedIn')
                    AND check_in_date <= ?
                    AND check_out_date > ?
            """
            occupied_result = db_manager.execute_query(occupied_query, (date_str, date_str))
            occupied = occupied_result[0]['occupied'] if occupied_result else 0
            
            occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0
            
            daily_data.append({
                'date': date_str,
                'total_rooms': total_rooms,
                'occupied_rooms': occupied,
                'available_rooms': total_rooms - occupied,
                'occupancy_rate': round(occupancy_rate, 2)
            })
            
            current_date += timedelta(days=1)
        
        # 计算平均入住率
        total_occupied = sum(d['occupied_rooms'] for d in daily_data)
        total_room_days = total_rooms * len(daily_data)
        average_occupancy = (total_occupied / total_room_days * 100) if total_room_days > 0 else 0
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_rooms': total_rooms,
            'days': len(daily_data),
            'average_occupancy_rate': round(average_occupancy, 2),
            'daily_data': daily_data
        }
    
    @staticmethod
    def generate_revenue_report(start_date: str, end_date: str) -> Dict[str, Any]:
        """
        生成收入报表
        
        Args:
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
            
        Returns:
            报表数据字典
        """
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end_dt <= start_dt:
                return {'error': '结束日期必须晚于开始日期'}
        except ValueError:
            return {'error': '日期格式无效'}
        
        # 查询总收入（已完成的预订）
        total_revenue_query = """
            SELECT 
                COUNT(*) as total_reservations,
                SUM(total_price) as total_revenue
            FROM reservations
            WHERE status IN ('CheckedOut')
                AND check_out_date >= ?
                AND check_out_date <= ?
        """
        revenue_result = db_manager.execute_query(
            total_revenue_query,
            (start_date, end_date)
        )
        
        total_reservations = revenue_result[0]['total_reservations'] if revenue_result else 0
        total_revenue = float(revenue_result[0]['total_revenue'] or 0) if revenue_result else 0.0
        
        # 按房型统计收入
        by_room_type_query = """
            SELECT 
                rt.type_name,
                COUNT(*) as reservations_count,
                SUM(r.total_price) as revenue
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.room_id
            JOIN room_types rt ON rm.room_type_id = rt.room_type_id
            WHERE r.status IN ('CheckedOut')
                AND r.check_out_date >= ?
                AND r.check_out_date <= ?
            GROUP BY rt.room_type_id, rt.type_name
            ORDER BY revenue DESC
        """
        by_room_type = db_manager.execute_query(
            by_room_type_query,
            (start_date, end_date)
        )
        room_type_data = [
            {
                'room_type': row['type_name'],
                'reservations': row['reservations_count'],
                'revenue': float(row['revenue'])
            }
            for row in by_room_type
        ]
        
        # 按支付方式统计
        by_payment_method_query = """
            SELECT 
                payment_method,
                COUNT(*) as payment_count,
                SUM(amount) as total_amount
            FROM payments
            WHERE payment_status = 'Paid'
                AND payment_date >= ?
                AND payment_date <= ?
            GROUP BY payment_method
            ORDER BY total_amount DESC
        """
        by_payment = db_manager.execute_query(
            by_payment_method_query,
            (start_date, end_date)
        )
        payment_data = [
            {
                'payment_method': row['payment_method'],
                'count': row['payment_count'],
                'amount': float(row['total_amount'])
            }
            for row in by_payment
        ]
        
        # 计算平均每预订收入
        avg_revenue = (total_revenue / total_reservations) if total_reservations > 0 else 0
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_reservations': total_reservations,
            'total_revenue': round(total_revenue, 2),
            'average_revenue_per_reservation': round(avg_revenue, 2),
            'by_room_type': room_type_data,
            'by_payment_method': payment_data
        }
    
    @staticmethod
    def export_to_csv(data: Dict[str, Any], filename: str, 
                     report_type: str) -> Tuple[bool, str]:
        """
        导出报表到CSV文件
        
        Args:
            data: 报表数据
            filename: 文件名
            report_type: 报表类型 ('occupancy' 或 'revenue')
            
        Returns:
            (是否成功, 消息或文件路径)
        """
        try:
            if report_type == 'occupancy':
                return ReportService._export_occupancy_csv(data, filename)
            elif report_type == 'revenue':
                return ReportService._export_revenue_csv(data, filename)
            else:
                return False, "不支持的报表类型"
        except Exception as e:
            return False, f"导出失败: {str(e)}"
    
    @staticmethod
    def _export_occupancy_csv(data: Dict[str, Any], filename: str) -> Tuple[bool, str]:
        """导出入住率报表为CSV"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入标题
            writer.writerow(['入住率报表'])
            writer.writerow([])
            writer.writerow(['报表期间', f"{data['start_date']} 至 {data['end_date']}"])
            writer.writerow(['总房间数', data['total_rooms']])
            writer.writerow(['报表天数', data['days']])
            writer.writerow(['平均入住率', f"{data['average_occupancy_rate']}%"])
            writer.writerow([])
            
            # 写入每日数据表头
            writer.writerow(['日期', '总房间数', '已占用', '可用', '入住率(%)'])
            
            # 写入每日数据
            for day in data['daily_data']:
                writer.writerow([
                    day['date'],
                    day['total_rooms'],
                    day['occupied_rooms'],
                    day['available_rooms'],
                    day['occupancy_rate']
                ])
        
        return True, filename
    
    @staticmethod
    def _export_revenue_csv(data: Dict[str, Any], filename: str) -> Tuple[bool, str]:
        """导出收入报表为CSV"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入标题
            writer.writerow(['收入报表'])
            writer.writerow([])
            writer.writerow(['报表期间', f"{data['start_date']} 至 {data['end_date']}"])
            writer.writerow(['总预订数', data['total_reservations']])
            writer.writerow(['总收入', f"¥{data['total_revenue']:.2f}"])
            writer.writerow(['平均每预订收入', f"¥{data['average_revenue_per_reservation']:.2f}"])
            writer.writerow([])
            
            # 按房型统计
            writer.writerow(['按房型统计'])
            writer.writerow(['房型', '预订数', '收入'])
            for item in data['by_room_type']:
                writer.writerow([
                    item['room_type'],
                    item['reservations'],
                    f"¥{item['revenue']:.2f}"
                ])
            writer.writerow([])
            
            # 按支付方式统计
            writer.writerow(['按支付方式统计'])
            writer.writerow(['支付方式', '交易数', '金额'])
            for item in data['by_payment_method']:
                writer.writerow([
                    item['payment_method'],
                    item['count'],
                    f"¥{item['amount']:.2f}"
                ])
        
        return True, filename
    
    @staticmethod
    def get_audit_logs(user_id: int = None, operation_type: str = None,
                      table_name: str = None, record_id: int = None,
                      start_date: str = None, end_date: str = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询审计日志
        
        Args:
            user_id: 用户ID
            operation_type: 操作类型
            table_name: 表名
            record_id: 记录ID
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回记录数限制
            
        Returns:
            审计日志列表
        """
        query = """
            SELECT 
                al.*,
                u.username, u.full_name
            FROM audit_logs al
            JOIN users u ON al.user_id = u.user_id
            WHERE 1=1
        """
        params = []
        
        if user_id:
            query += " AND al.user_id = ?"
            params.append(user_id)
        
        if operation_type:
            query += " AND al.operation_type = ?"
            params.append(operation_type)
        
        if table_name:
            query += " AND al.table_name = ?"
            params.append(table_name)
        
        if record_id:
            query += " AND al.record_id = ?"
            params.append(record_id)
        
        if start_date:
            query += " AND DATE(al.timestamp) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(al.timestamp) <= ?"
            params.append(end_date)
        
        query += f" ORDER BY al.timestamp DESC LIMIT {limit}"
        
        result = db_manager.execute_query(query, tuple(params) if params else None)
        return db_manager.rows_to_dict_list(result)
    
    @staticmethod
    def backup_database(backup_name: str, user_id: int) -> Tuple[bool, str]:
        """
        执行数据库备份
        
        Args:
            backup_name: 备份文件名（不含路径和扩展名）
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息或备份文件路径)
        """
        import os
        from datetime import datetime
        
        try:
            # 创建备份目录
            backup_dir = 'backups'
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_name}_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_file)
            
            # 执行备份
            db_manager.backup_database(backup_path)
            
            # 获取备份文件大小
            backup_size = os.path.getsize(backup_path)
            
            # 记录备份信息
            record_query = """
                INSERT INTO backup_records 
                (backup_file, backup_size, backup_type, status, created_by)
                VALUES (?, ?, 'Manual', 'Completed', ?)
            """
            backup_id = db_manager.execute_insert(
                record_query,
                (backup_path, backup_size, user_id)
            )
            
            # 记录审计日志
            audit_query = """
                INSERT INTO audit_logs 
                (user_id, operation_type, table_name, record_id, description)
                VALUES (?, 'BACKUP', 'backup_records', ?, ?)
            """
            db_manager.execute_insert(
                audit_query,
                (user_id, backup_id, f"Created database backup: {backup_file}")
            )
            
            return True, backup_path
            
        except Exception as e:
            # 记录失败状态
            try:
                record_query = """
                    INSERT INTO backup_records 
                    (backup_file, backup_type, status, created_by, notes)
                    VALUES (?, 'Manual', 'Failed', ?, ?)
                """
                db_manager.execute_insert(
                    record_query,
                    (backup_name, user_id, str(e))
                )
            except:
                pass
            
            return False, f"备份失败: {str(e)}"
    
    @staticmethod
    def list_backups() -> List[Dict[str, Any]]:
        """
        列出所有备份记录
        
        Returns:
            备份记录列表
        """
        query = """
            SELECT 
                br.*,
                u.username, u.full_name
            FROM backup_records br
            JOIN users u ON br.created_by = u.user_id
            ORDER BY br.created_at DESC
        """
        result = db_manager.execute_query(query)
        return db_manager.rows_to_dict_list(result)
