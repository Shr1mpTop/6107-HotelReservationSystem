"""
Email Service Module (Simulated Implementation)
Used to send reservation confirmation, cancellation and other notification emails
"""

from datetime import datetime
from typing import Dict, Any
from database.db_manager import db_manager


class EmailService:
    """Email Service Class (Simulated Implementation)"""
    
    @staticmethod
    def send_reservation_confirmation(reservation: Dict[str, Any]) -> bool:
        """
        Send reservation confirmation email
        
        Args:
            reservation: Reservation information
            
        Returns:
            Whether sending was successful
        """
        subject = f"Reservation Confirmation - Reservation #{reservation['reservation_id']}"
        
        body = f"""
Dear {reservation['guest_name']},

Thank you for choosing our hotel! Your reservation has been confirmed.

Reservation Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reservation #: {reservation['reservation_id']}
Room Number: {reservation['room_number']}
Room Type: {reservation['room_type']}
Check-in Date: {reservation['check_in_date']}
Check-out Date: {reservation['check_out_date']}
Number of Guests: {reservation['num_guests']}
Total Price: ¥{reservation['total_price']:.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Special Requests: {reservation.get('special_requests', 'None')}

We look forward to your arrival!

If you have any questions, please contact us:
Phone: 1234567890
Email: info@hotel.com

Best regards,
Hotel Management Team
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
        Send reservation cancellation notice
        
        Args:
            reservation: Reservation information
            
        Returns:
            Whether sending was successful
        """
        subject = f"Reservation Cancellation Confirmation - Reservation #{reservation['reservation_id']}"
        
        body = f"""
Dear {reservation['guest_name']},

Your reservation has been cancelled.

Reservation Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reservation #: {reservation['reservation_id']}
Room Number: {reservation['room_number']}
Room Type: {reservation['room_type']}
Original Check-in Date: {reservation['check_in_date']}
Original Check-out Date: {reservation['check_out_date']}
Cancellation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If you have any questions, please contact us.

Best regards,
Hotel Management Team
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
        Send reservation modification notice
        
        Args:
            reservation: Reservation information
            changes: Description of changes
            
        Returns:
            Whether sending was successful
        """
        subject = f"Reservation Modification Confirmation - Reservation #{reservation['reservation_id']}"
        
        body = f"""
Dear {reservation['guest_name']},

Your reservation information has been updated.

Reservation Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reservation #: {reservation['reservation_id']}
Room Number: {reservation['room_number']}
Room Type: {reservation['room_type']}
Check-in Date: {reservation['check_in_date']}
Check-out Date: {reservation['check_out_date']}
Number of Guests: {reservation['num_guests']}
Total Price: ¥{reservation['total_price']:.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Changes Made:
{changes}

Modification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you have any questions, please contact us.

Best regards,
Hotel Management Team
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
        Send email (simulated implementation)
        
        Args:
            reservation_id: Reservation ID
            recipient_email: Recipient email
            subject: Email subject
            body: Email body
            notification_type: Notification type
            
        Returns:
            Whether sending was successful
        """
        try:
            # Simulate email sending - in real application, this would call actual email service API
            print(f"\n{'='*60}")
            print(f"[Simulated Email Service] Sending email...")
            print(f"{'='*60}")
            print(f"Recipient: {recipient_email}")
            print(f"Subject: {subject}")
            print(f"{'='*60}")
            print(body)
            print(f"{'='*60}\n")
            
            # Record to database
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
            print(f"Email sending failed: {e}")
            
            # Record failure status
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
        Get email notification history for reservation
        
        Args:
            reservation_id: Reservation ID
            
        Returns:
            List of notification history
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
