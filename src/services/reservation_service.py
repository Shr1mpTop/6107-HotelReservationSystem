"""
预订服务模块
处理预订的创建、修改、取消和查询
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from database.db_manager import db_manager
from services.pricing_service import PricingService
from services.room_service import RoomService
from services.email_service import EmailService


class ReservationService:
    """预订服务类"""
    
    # 预订状态常量
    STATUS_CONFIRMED = 'Confirmed'
    STATUS_CHECKED_IN = 'CheckedIn'
    STATUS_CHECKED_OUT = 'CheckedOut'
    STATUS_CANCELLED = 'Cancelled'
    
    @staticmethod
    def create_reservation(guest_info: Dict[str, Any], room_id: int,
                          check_in_date: str, check_out_date: str,
                          num_guests: int, special_requests: str,
                          user_id: int) -> Tuple[bool, str, Optional[int]]:
        """
        创建新预订
        
        Args:
            guest_info: 客人信息字典 {first_name, last_name, email, phone, id_number, address}
            room_id: 房间ID
            check_in_date: 入住日期（YYYY-MM-DD）
            check_out_date: 退房日期（YYYY-MM-DD）
            num_guests: 客人数量
            special_requests: 特殊要求
            user_id: 创建预订的用户ID
            
        Returns:
            (是否成功, 消息, 预订ID)
        """
        # 1. 验证日期
        try:
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d')
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if check_in < today:
                return False, "入住日期不能早于今天", None
            
            if check_out <= check_in:
                return False, "退房日期必须晚于入住日期", None
            
        except ValueError:
            return False, "日期格式无效，请使用YYYY-MM-DD格式", None
        
        # 2. 验证房间
        room = RoomService.get_room_by_id(room_id)
        if not room:
            return False, "房间不存在", None
        
        if room['status'] != RoomService.STATUS_CLEAN:
            return False, f"房间当前状态为 {room['status']}，不可预订", None
        
        # 3. 验证客人数量
        if num_guests > room['max_occupancy']:
            return False, f"客人数量超过房间最大容纳量（{room['max_occupancy']}人）", None
        
        if num_guests < 1:
            return False, "客人数量必须至少为1人", None
        
        # 4. 检查超售防护 - 确保房间在指定日期范围内可用
        conflict_check = """
            SELECT reservation_id 
            FROM reservations
            WHERE room_id = ? 
                AND status IN ('Confirmed', 'CheckedIn')
                AND (
                    (check_in_date < ? AND check_out_date > ?)
                    OR (check_in_date >= ? AND check_in_date < ?)
                )
            LIMIT 1
        """
        conflicts = db_manager.execute_query(
            conflict_check,
            (room_id, check_out_date, check_in_date, check_in_date, check_out_date)
        )
        
        if conflicts:
            return False, f"房间 {room['room_number']} 在此日期范围内已被预订", None
        
        # 5. 计算总价
        pricing_info = PricingService.calculate_total_price(
            room['room_type_id'],
            check_in_date,
            check_out_date
        )
        total_price = pricing_info['total']
        
        # 6. 创建或获取客人记录
        guest_id = ReservationService._get_or_create_guest(guest_info)
        if not guest_id:
            return False, "无法创建客人记录", None
        
        # 7. 创建预订
        reservation_query = """
            INSERT INTO reservations 
            (guest_id, room_id, check_in_date, check_out_date, num_guests, 
             total_price, status, special_requests, created_by)
            VALUES (?, ?, ?, ?, ?, ?, 'Confirmed', ?, ?)
        """
        
        try:
            reservation_id = db_manager.execute_insert(
                reservation_query,
                (guest_id, room_id, check_in_date, check_out_date, 
                 num_guests, total_price, special_requests, user_id)
            )
            
            # 8. 记录审计日志
            ReservationService._log_audit(
                user_id,
                'CREATE',
                'reservations',
                reservation_id,
                None,
                f"Created reservation {reservation_id} for room {room['room_number']}"
            )
            
            # 9. 发送确认邮件
            reservation_details = ReservationService.get_reservation_by_id(reservation_id)
            if reservation_details:
                EmailService.send_reservation_confirmation(reservation_details)
            
            return True, f"预订创建成功！预订号: {reservation_id}", reservation_id
            
        except Exception as e:
            return False, f"创建预订失败: {str(e)}", None
    
    @staticmethod
    def _get_or_create_guest(guest_info: Dict[str, Any]) -> Optional[int]:
        """
        获取或创建客人记录
        
        Args:
            guest_info: 客人信息
            
        Returns:
            客人ID
        """
        # 先尝试通过手机号查找现有客人
        phone = guest_info.get('phone')
        if phone:
            query = "SELECT guest_id FROM guests WHERE phone = ?"
            result = db_manager.execute_query(query, (phone,))
            if result:
                # 更新客人信息
                guest_id = result[0]['guest_id']
                update_query = """
                    UPDATE guests 
                    SET first_name = ?, last_name = ?, email = ?, 
                        id_number = ?, address = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE guest_id = ?
                """
                db_manager.execute_update(
                    update_query,
                    (guest_info.get('first_name'), guest_info.get('last_name'),
                     guest_info.get('email'), guest_info.get('id_number'),
                     guest_info.get('address'), guest_id)
                )
                return guest_id
        
        # 创建新客人记录
        insert_query = """
            INSERT INTO guests 
            (first_name, last_name, email, phone, id_number, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            guest_id = db_manager.execute_insert(
                insert_query,
                (guest_info.get('first_name'), guest_info.get('last_name'),
                 guest_info.get('email'), phone,
                 guest_info.get('id_number'), guest_info.get('address'))
            )
            return guest_id
        except Exception as e:
            print(f"创建客人记录失败: {e}")
            return None
    
    @staticmethod
    def get_reservation_by_id(reservation_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取预订详情
        
        Args:
            reservation_id: 预订ID
            
        Returns:
            预订详情字典
        """
        query = """
            SELECT 
                r.*,
                g.first_name, g.last_name, g.email, g.phone, g.id_number, g.address,
                rm.room_number, rm.floor,
                rt.type_name as room_type, rt.description as room_description,
                u.username as created_by_username, u.full_name as created_by_name
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            JOIN room_types rt ON rm.room_type_id = rt.room_type_id
            JOIN users u ON r.created_by = u.user_id
            WHERE r.reservation_id = ?
        """
        result = db_manager.execute_query(query, (reservation_id,))
        
        if result:
            reservation = dict(result[0])
            # 添加客人全名
            reservation['guest_name'] = f"{reservation['first_name']} {reservation['last_name']}"
            return reservation
        return None
    
    @staticmethod
    def search_reservations(guest_name: str = None, phone: str = None,
                           reservation_id: int = None, room_number: str = None,
                           status: str = None, check_in_date: str = None) -> List[Dict[str, Any]]:
        """
        搜索预订
        
        Args:
            guest_name: 客人姓名（模糊匹配）
            phone: 手机号（精确匹配）
            reservation_id: 预订ID
            room_number: 房间号
            status: 预订状态
            check_in_date: 入住日期
            
        Returns:
            预订列表
        """
        query = """
            SELECT 
                r.reservation_id, r.check_in_date, r.check_out_date, 
                r.num_guests, r.total_price, r.status,
                g.first_name, g.last_name, g.phone,
                rm.room_number,
                rt.type_name as room_type
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            JOIN room_types rt ON rm.room_type_id = rt.room_type_id
            WHERE 1=1
        """
        params = []
        
        if reservation_id:
            query += " AND r.reservation_id = ?"
            params.append(reservation_id)
        
        if guest_name:
            query += " AND (g.first_name LIKE ? OR g.last_name LIKE ?)"
            params.extend([f"%{guest_name}%", f"%{guest_name}%"])
        
        if phone:
            query += " AND g.phone = ?"
            params.append(phone)
        
        if room_number:
            query += " AND rm.room_number = ?"
            params.append(room_number)
        
        if status:
            query += " AND r.status = ?"
            params.append(status)
        
        if check_in_date:
            query += " AND r.check_in_date = ?"
            params.append(check_in_date)
        
        query += " ORDER BY r.created_at DESC LIMIT 50"
        
        result = db_manager.execute_query(query, tuple(params) if params else None)
        reservations = db_manager.rows_to_dict_list(result)
        
        # 添加客人全名
        for reservation in reservations:
            reservation['guest_name'] = f"{reservation['first_name']} {reservation['last_name']}"
        
        return reservations
    
    @staticmethod
    def modify_reservation(reservation_id: int, new_check_in: str = None,
                          new_check_out: str = None, new_room_id: int = None,
                          new_num_guests: int = None, new_special_requests: str = None,
                          user_id: int = None) -> Tuple[bool, str]:
        """
        修改预订
        
        Args:
            reservation_id: 预订ID
            new_check_in: 新入住日期
            new_check_out: 新退房日期
            new_room_id: 新房间ID
            new_num_guests: 新客人数量
            new_special_requests: 新特殊要求
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息)
        """
        # 获取当前预订
        current = ReservationService.get_reservation_by_id(reservation_id)
        if not current:
            return False, "预订不存在"
        
        if current['status'] not in [ReservationService.STATUS_CONFIRMED]:
            return False, f"预订状态为 {current['status']}，无法修改"
        
        # 检查是否已入住
        check_in = datetime.strptime(current['check_in_date'], '%Y-%m-%d')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if check_in <= today and not new_check_in:
            return False, "预订已到入住日期，无法修改"
        
        changes = []
        updates = []
        params = []
        
        # 处理日期修改
        final_check_in = new_check_in or current['check_in_date']
        final_check_out = new_check_out or current['check_out_date']
        final_room_id = new_room_id or current['room_id']
        
        # 验证新日期
        if new_check_in or new_check_out:
            try:
                check_in_dt = datetime.strptime(final_check_in, '%Y-%m-%d')
                check_out_dt = datetime.strptime(final_check_out, '%Y-%m-%d')
                
                if check_in_dt < today:
                    return False, "入住日期不能早于今天"
                
                if check_out_dt <= check_in_dt:
                    return False, "退房日期必须晚于入住日期"
                    
            except ValueError:
                return False, "日期格式无效"
        
        # 检查房间冲突（如果修改了日期或房间）
        if new_check_in or new_check_out or new_room_id:
            conflict_check = """
                SELECT reservation_id 
                FROM reservations
                WHERE room_id = ? 
                    AND reservation_id != ?
                    AND status IN ('Confirmed', 'CheckedIn')
                    AND (
                        (check_in_date < ? AND check_out_date > ?)
                        OR (check_in_date >= ? AND check_in_date < ?)
                    )
                LIMIT 1
            """
            conflicts = db_manager.execute_query(
                conflict_check,
                (final_room_id, reservation_id, final_check_out, 
                 final_check_in, final_check_in, final_check_out)
            )
            
            if conflicts:
                return False, "所选房间在此日期范围内已被预订"
        
        # 构建更新
        if new_check_in:
            updates.append("check_in_date = ?")
            params.append(new_check_in)
            changes.append(f"入住日期: {current['check_in_date']} → {new_check_in}")
        
        if new_check_out:
            updates.append("check_out_date = ?")
            params.append(new_check_out)
            changes.append(f"退房日期: {current['check_out_date']} → {new_check_out}")
        
        if new_room_id:
            room = RoomService.get_room_by_id(new_room_id)
            if not room:
                return False, "新房间不存在"
            updates.append("room_id = ?")
            params.append(new_room_id)
            changes.append(f"房间: {current['room_number']} → {room['room_number']}")
        
        if new_num_guests:
            room = RoomService.get_room_by_id(final_room_id)
            if new_num_guests > room['max_occupancy']:
                return False, f"客人数量超过房间最大容纳量（{room['max_occupancy']}人）"
            updates.append("num_guests = ?")
            params.append(new_num_guests)
            changes.append(f"客人数量: {current['num_guests']} → {new_num_guests}")
        
        if new_special_requests is not None:
            updates.append("special_requests = ?")
            params.append(new_special_requests)
            changes.append("特殊要求已更新")
        
        if not updates:
            return False, "没有需要修改的内容"
        
        # 重新计算价格（如果日期或房间改变）
        if new_check_in or new_check_out or new_room_id:
            room = RoomService.get_room_by_id(final_room_id)
            pricing_info = PricingService.calculate_total_price(
                room['room_type_id'],
                final_check_in,
                final_check_out
            )
            new_total = pricing_info['total']
            
            updates.append("total_price = ?")
            params.append(new_total)
            changes.append(f"总价: ¥{current['total_price']:.2f} → ¥{new_total:.2f}")
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(reservation_id)
        
        # 执行更新
        query = f"UPDATE reservations SET {', '.join(updates)} WHERE reservation_id = ?"
        
        try:
            db_manager.execute_update(query, tuple(params))
            
            # 记录审计日志
            if user_id:
                ReservationService._log_audit(
                    user_id,
                    'MODIFY',
                    'reservations',
                    reservation_id,
                    str(current),
                    f"Modified reservation {reservation_id}: {'; '.join(changes)}"
                )
            
            # 发送修改通知邮件
            updated_reservation = ReservationService.get_reservation_by_id(reservation_id)
            if updated_reservation:
                EmailService.send_modification_notice(
                    updated_reservation,
                    "\n".join(changes)
                )
            
            return True, f"预订修改成功。\n修改内容:\n" + "\n".join(changes)
            
        except Exception as e:
            return False, f"修改失败: {str(e)}"
    
    @staticmethod
    def cancel_reservation(reservation_id: int, user_id: int = None) -> Tuple[bool, str]:
        """
        取消预订
        
        Args:
            reservation_id: 预订ID
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息)
        """
        # 获取预订
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            return False, "预订不存在"
        
        if reservation['status'] == ReservationService.STATUS_CANCELLED:
            return False, "预订已被取消"
        
        if reservation['status'] == ReservationService.STATUS_CHECKED_OUT:
            return False, "已退房的预订无法取消"
        
        # 如果已入住，需要先退房
        if reservation['status'] == ReservationService.STATUS_CHECKED_IN:
            return False, "已入住的预订需要先办理退房"
        
        # 取消预订
        query = """
            UPDATE reservations 
            SET status = 'Cancelled', updated_at = CURRENT_TIMESTAMP
            WHERE reservation_id = ?
        """
        
        try:
            db_manager.execute_update(query, (reservation_id,))
            
            # 记录审计日志
            if user_id:
                ReservationService._log_audit(
                    user_id,
                    'CANCEL',
                    'reservations',
                    reservation_id,
                    f"Status: {reservation['status']}",
                    f"Cancelled reservation {reservation_id}"
                )
            
            # 发送取消通知邮件
            EmailService.send_cancellation_notice(reservation)
            
            return True, "预订已取消"
            
        except Exception as e:
            return False, f"取消失败: {str(e)}"
    
    @staticmethod
    def check_in(reservation_id: int, user_id: int = None) -> Tuple[bool, str]:
        """
        办理入住
        
        Args:
            reservation_id: 预订ID
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息)
        """
        # 获取预订
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            return False, "预订不存在"
        
        if reservation['status'] != ReservationService.STATUS_CONFIRMED:
            return False, f"预订状态为 {reservation['status']}，无法办理入住"
        
        # 检查入住日期
        check_in_date = datetime.strptime(reservation['check_in_date'], '%Y-%m-%d')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 允许提前一天入住
        if check_in_date > today + timedelta(days=1):
            return False, f"入住日期为 {reservation['check_in_date']}，现在还不能办理入住"
        
        try:
            # 更新预订状态
            query = """
                UPDATE reservations 
                SET status = 'CheckedIn', updated_at = CURRENT_TIMESTAMP
                WHERE reservation_id = ?
            """
            db_manager.execute_update(query, (reservation_id,))
            
            # 更新房间状态为已占用
            RoomService.update_room_status(
                reservation['room_id'],
                RoomService.STATUS_OCCUPIED,
                user_id
            )
            
            # 记录审计日志
            if user_id:
                ReservationService._log_audit(
                    user_id,
                    'CHECK_IN',
                    'reservations',
                    reservation_id,
                    f"Status: {reservation['status']}",
                    f"Checked in reservation {reservation_id}, room {reservation['room_number']}"
                )
            
            return True, f"入住办理成功！房间号: {reservation['room_number']}"
            
        except Exception as e:
            return False, f"入住办理失败: {str(e)}"
    
    @staticmethod
    def check_out(reservation_id: int, payment_method: str, 
                 payment_amount: float, user_id: int = None) -> Tuple[bool, str]:
        """
        办理退房
        
        Args:
            reservation_id: 预订ID
            payment_method: 支付方式
            payment_amount: 支付金额
            user_id: 操作用户ID
            
        Returns:
            (是否成功, 消息)
        """
        # 获取预订
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            return False, "预订不存在"
        
        if reservation['status'] != ReservationService.STATUS_CHECKED_IN:
            return False, f"预订状态为 {reservation['status']}，无法办理退房"
        
        # 验证支付方式
        valid_methods = ['Cash', 'CreditCard', 'DebitCard', 'OnlineTransfer']
        if payment_method not in valid_methods:
            return False, f"无效的支付方式。有效选项: {', '.join(valid_methods)}"
        
        try:
            # 更新预订状态
            query = """
                UPDATE reservations 
                SET status = 'CheckedOut', updated_at = CURRENT_TIMESTAMP
                WHERE reservation_id = ?
            """
            db_manager.execute_update(query, (reservation_id,))
            
            # 记录支付
            payment_query = """
                INSERT INTO payments 
                (reservation_id, amount, payment_method, payment_status, processed_by)
                VALUES (?, ?, ?, 'Paid', ?)
            """
            payment_id = db_manager.execute_insert(
                payment_query,
                (reservation_id, payment_amount, payment_method, user_id or 1)
            )
            
            # 更新房间状态为脏污
            RoomService.update_room_status(
                reservation['room_id'],
                RoomService.STATUS_DIRTY,
                user_id
            )
            
            # 记录审计日志
            if user_id:
                ReservationService._log_audit(
                    user_id,
                    'CHECK_OUT',
                    'reservations',
                    reservation_id,
                    f"Status: {reservation['status']}",
                    f"Checked out reservation {reservation_id}, payment: {payment_method} ¥{payment_amount}"
                )
            
            return True, f"退房办理成功！支付金额: ¥{payment_amount:.2f}"
            
        except Exception as e:
            return False, f"退房办理失败: {str(e)}"
    
    @staticmethod
    def get_upcoming_checkins(days: int = 1) -> List[Dict[str, Any]]:
        """
        获取即将入住的预订列表
        
        Args:
            days: 未来天数
            
        Returns:
            预订列表
        """
        today = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                r.reservation_id, r.check_in_date, r.check_out_date,
                g.first_name, g.last_name, g.phone,
                rm.room_number,
                rt.type_name as room_type
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            JOIN room_types rt ON rm.room_type_id = rt.room_type_id
            WHERE r.status = 'Confirmed'
                AND r.check_in_date >= ?
                AND r.check_in_date <= ?
            ORDER BY r.check_in_date, rm.room_number
        """
        
        result = db_manager.execute_query(query, (today, end_date))
        reservations = db_manager.rows_to_dict_list(result)
        
        for reservation in reservations:
            reservation['guest_name'] = f"{reservation['first_name']} {reservation['last_name']}"
        
        return reservations
    
    @staticmethod
    def get_current_checkins() -> List[Dict[str, Any]]:
        """
        获取当前入住的预订列表
        
        Returns:
            预订列表
        """
        query = """
            SELECT 
                r.reservation_id, r.check_in_date, r.check_out_date,
                g.first_name, g.last_name, g.phone,
                rm.room_number,
                rt.type_name as room_type
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            JOIN room_types rt ON rm.room_type_id = rt.room_type_id
            WHERE r.status = 'CheckedIn'
            ORDER BY rm.room_number
        """
        
        result = db_manager.execute_query(query)
        reservations = db_manager.rows_to_dict_list(result)
        
        for reservation in reservations:
            reservation['guest_name'] = f"{reservation['first_name']} {reservation['last_name']}"
        
        return reservations
    
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
