"""
Report Service Module
Handles generation and export of occupancy, revenue and other reports
"""

import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from database.db_manager import db_manager


class ReportService:
    """Report Service Class"""
    
    @staticmethod
    def generate_occupancy_report(start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate occupancy report
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Report data dictionary
        """
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end_dt <= start_dt:
                return {'error': 'End date must be later than start date'}
        except ValueError:
            return {'error': 'Invalid date format'}
        
        # Get total room count
        total_rooms_query = "SELECT COUNT(*) as total FROM rooms WHERE is_active = 1"
        total_rooms_result = db_manager.execute_query(total_rooms_query)
        total_rooms = total_rooms_result[0]['total'] if total_rooms_result else 0
        
        if total_rooms == 0:
            return {'error': 'No available room data'}
        
        # Calculate daily occupancy
        daily_data = []
        current_date = start_dt
        
        while current_date <= end_dt:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Query occupied rooms for the day
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
        
        # Calculate average occupancy rate
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
        Generate revenue report
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Report data dictionary
        """
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if end_dt <= start_dt:
                return {'error': 'End date must be later than start date'}
        except ValueError:
            return {'error': 'Invalid date format'}
        
        # Query total revenue (completed reservations)
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
        
        # Revenue by room type
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
        
        # Revenue by payment method
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
        
        # Calculate average revenue per reservation
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
        Export report to CSV file
        
        Args:
            data: Report data
            filename: Filename
            report_type: Report type ('occupancy' or 'revenue')
            
        Returns:
            (Success status, Message or file path)
        """
        try:
            if report_type == 'occupancy':
                return ReportService._export_occupancy_csv(data, filename)
            elif report_type == 'revenue':
                return ReportService._export_revenue_csv(data, filename)
            else:
                return False, "Unsupported report type"
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    @staticmethod
    def _export_occupancy_csv(data: Dict[str, Any], filename: str) -> Tuple[bool, str]:
        """Export occupancy report as CSV"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # Write title
            writer.writerow(['Occupancy Report'])
            writer.writerow([])
            writer.writerow(['Report Period', f"{data['start_date']} to {data['end_date']}"])
            writer.writerow(['Total Rooms', data['total_rooms']])
            writer.writerow(['Report Days', data['days']])
            writer.writerow(['Average Occupancy Rate', f"{data['average_occupancy_rate']}%"])
            writer.writerow([])
            
            # Write daily data headers
            writer.writerow(['Date', 'Total Rooms', 'Occupied', 'Available', 'Occupancy Rate (%)'])
            
            # Write daily data
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
        """Export revenue report as CSV"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # Write title
            writer.writerow(['Revenue Report'])
            writer.writerow([])
            writer.writerow(['Report Period', f"{data['start_date']} to {data['end_date']}"])
            writer.writerow(['Total Reservations', data['total_reservations']])
            writer.writerow(['Total Revenue', f"¥{data['total_revenue']:.2f}"])
            writer.writerow(['Average Revenue per Reservation', f"¥{data['average_revenue_per_reservation']:.2f}"])
            writer.writerow([])
            
            # By room type
            writer.writerow(['By Room Type'])
            writer.writerow(['Room Type', 'Reservations', 'Revenue'])
            for item in data['by_room_type']:
                writer.writerow([
                    item['room_type'],
                    item['reservations'],
                    f"¥{item['revenue']:.2f}"
                ])
            writer.writerow([])
            
            # By payment method
            writer.writerow(['By Payment Method'])
            writer.writerow(['Payment Method', 'Transactions', 'Amount'])
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
        Query audit logs
        
        Args:
            user_id: User ID
            operation_type: Operation type
            table_name: Table name
            record_id: Record ID
            start_date: Start date
            end_date: End date
            limit: Record limit
            
        Returns:
            Audit log list
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
        Execute database backup
        
        Args:
            backup_name: Backup filename (without path and extension)
            user_id: Operating user ID
            
        Returns:
            (Success status, Message or backup file path)
        """
        import os
        from datetime import datetime
        
        try:
            # Create backup directory
            backup_dir = 'backups'
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_name}_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_file)
            
            # Execute backup
            db_manager.backup_database(backup_path)
            
            # Get backup file size
            backup_size = os.path.getsize(backup_path)
            
            # Record backup information
            record_query = """
                INSERT INTO backup_records 
                (backup_file, backup_size, backup_type, status, created_by)
                VALUES (?, ?, 'Manual', 'Completed', ?)
            """
            backup_id = db_manager.execute_insert(
                record_query,
                (backup_path, backup_size, user_id)
            )
            
            # Record audit log
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
            # Record failure status
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
            
            return False, f"Backup failed: {str(e)}"
    
    @staticmethod
    def list_backups() -> List[Dict[str, Any]]:
        """
        List all backup records
        
        Returns:
            Backup record list
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
