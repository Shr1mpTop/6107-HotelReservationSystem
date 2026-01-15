"""
邮件服务模块（模拟实现）
用于发送预订确认、取消等通知邮件
"""

from datetime import datetime
from typing import Dict, Any
from database.db_manager import db_manager


class EmailService:
    """邮件服务类（模拟实现）"""
    
    @staticmethod
    def send_reservation_confirmation(reservation: Dict[str, Any]) -> bool:
        """
        发送预订确认邮件
        
        Args:
            reservation: 预订信息
            
        Returns:
            是否发送成功
        """
        subject = f"预订确认 - 预订号 {reservation['reservation_id']}"
        
        body = f"""
尊敬的 {reservation['guest_name']}，

感谢您选择我们的酒店！您的预订已确认。

预订详情：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
预订号：{reservation['reservation_id']}
房间号：{reservation['room_number']}
房型：{reservation['room_type']}
入住日期：{reservation['check_in_date']}
退房日期：{reservation['check_out_date']}
客人数量：{reservation['num_guests']}
总价：¥{reservation['total_price']:.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

特殊要求：{reservation.get('special_requests', '无')}

我们期待您的到来！

如有任何疑问，请联系我们：
电话：1234567890
邮箱：info@hotel.com

此致
酒店管理团队
        """
        
        return EmailService._send_email(
            reservation_id=reservation['reservation_id'],
            recipient_email=reservation.get('guest_email', 'guest@example.com'),
            subject=subject,
            body=body,
            notification_type='Confirmation'
        )
    
    @staticmethod
    def send_cancellation_notice(reservation: Dict[str, Any]) -> bool:
        """
        发送预订取消通知
        
        Args:
            reservation: 预订信息
            
        Returns:
            是否发送成功
        """
        subject = f"预订取消确认 - 预订号 {reservation['reservation_id']}"
        
        body = f"""
尊敬的 {reservation['guest_name']}，

您的预订已被取消。

预订详情：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
预订号：{reservation['reservation_id']}
房间号：{reservation['room_number']}
房型：{reservation['room_type']}
原入住日期：{reservation['check_in_date']}
原退房日期：{reservation['check_out_date']}
取消时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

如果您有任何疑问，请随时联系我们。

此致
酒店管理团队
        """
        
        return EmailService._send_email(
            reservation_id=reservation['reservation_id'],
            recipient_email=reservation.get('guest_email', 'guest@example.com'),
            subject=subject,
            body=body,
            notification_type='Cancellation'
        )
    
    @staticmethod
    def send_modification_notice(reservation: Dict[str, Any], changes: str) -> bool:
        """
        发送预订修改通知
        
        Args:
            reservation: 预订信息
            changes: 修改内容描述
            
        Returns:
            是否发送成功
        """
        subject = f"预订修改确认 - 预订号 {reservation['reservation_id']}"
        
        body = f"""
尊敬的 {reservation['guest_name']}，

您的预订信息已更新。

预订详情：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
预订号：{reservation['reservation_id']}
房间号：{reservation['room_number']}
房型：{reservation['room_type']}
入住日期：{reservation['check_in_date']}
退房日期：{reservation['check_out_date']}
客人数量：{reservation['num_guests']}
总价：¥{reservation['total_price']:.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

修改内容：
{changes}

修改时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

如有任何疑问，请联系我们。

此致
酒店管理团队
        """
        
        return EmailService._send_email(
            reservation_id=reservation['reservation_id'],
            recipient_email=reservation.get('guest_email', 'guest@example.com'),
            subject=subject,
            body=body,
            notification_type='Modification'
        )
    
    @staticmethod
    def _send_email(reservation_id: int, recipient_email: str, 
                   subject: str, body: str, notification_type: str) -> bool:
        """
        发送邮件（模拟实现）
        
        Args:
            reservation_id: 预订ID
            recipient_email: 收件人邮箱
            subject: 邮件主题
            body: 邮件正文
            notification_type: 通知类型
            
        Returns:
            是否发送成功
        """
        try:
            # 模拟邮件发送 - 实际应用中这里会调用真实的邮件服务API
            print(f"\n{'='*60}")
            print(f"[模拟邮件服务] 正在发送邮件...")
            print(f"{'='*60}")
            print(f"收件人: {recipient_email}")
            print(f"主题: {subject}")
            print(f"{'='*60}")
            print(body)
            print(f"{'='*60}\n")
            
            # 记录到数据库
            query = """
                INSERT INTO email_notifications 
                (reservation_id, recipient_email, subject, body, notification_type, status)
                VALUES (?, ?, ?, ?, ?, 'Sent')
            """
            db_manager.execute_insert(
                query,
                (reservation_id, recipient_email, subject, body, notification_type)
            )
            
            return True
            
        except Exception as e:
            print(f"邮件发送失败: {e}")
            
            # 记录失败状态
            try:
                query = """
                    INSERT INTO email_notifications 
                    (reservation_id, recipient_email, subject, body, notification_type, status)
                    VALUES (?, ?, ?, ?, ?, 'Failed')
                """
                db_manager.execute_insert(
                    query,
                    (reservation_id, recipient_email, subject, body, notification_type)
                )
            except:
                pass
            
            return False
    
    @staticmethod
    def get_notification_history(reservation_id: int) -> list:
        """
        获取预订的邮件通知历史
        
        Args:
            reservation_id: 预订ID
            
        Returns:
            通知历史列表
        """
        query = """
            SELECT notification_id, recipient_email, subject, notification_type, 
                   status, sent_at
            FROM email_notifications
            WHERE reservation_id = ?
            ORDER BY sent_at DESC
        """
        result = db_manager.execute_query(query, (reservation_id,))
        return db_manager.rows_to_dict_list(result)
