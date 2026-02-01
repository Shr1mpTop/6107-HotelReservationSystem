"""
Main Menu Module
Handles CLI interface menu navigation and user interaction
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.display import Display
from services.auth_service import AuthService
from services.reservation_service import ReservationService
from services.room_service import RoomService
from services.pricing_service import PricingService
from services.report_service import ReportService


class HRMSMenu:
    """Hotel Reservation Management System Menu Class"""
    
    def __init__(self):
        self.current_user = None
        self.session_token = None
        self.running = True
    
    def start(self):
        """Start system"""
        Display.clear_screen()
        Display.print_logo()
        
        # Login
        if not self.login():
            return
        
        # Main menu loop
        while self.running:
            self.show_main_menu()
    
    def login(self) -> bool:
        """User login"""
        Display.print_header("User Login")
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            username = Display.get_input("Username")
            if username is None:  # User cancelled
                return False
            
            password = Display.get_input("Password")
            if password is None:  # User cancelled
                return False
            
            # Try login
            result = AuthService.login(username, password)
            
            if result:
                self.session_token = result['session_token']
                self.current_user = result['user']
                
                Display.print_success(f"Welcome, {self.current_user['full_name']}!")
                Display.print_info(f"Role: {self._get_role_name(self.current_user['role'])}")
                Display.pause()
                return True
            else:
                attempts += 1
                remaining = max_attempts - attempts
                if remaining > 0:
                    Display.print_error(f"Invalid username or password, {remaining} attempts remaining")
                else:
                    Display.print_error("Too many failed login attempts, system exit")
                    return False
        
        return False
    
    def logout(self):
        """User logout"""
        if self.session_token:
            AuthService.logout(self.session_token)
            Display.print_success("Successfully logged out of the system")
        self.running = False
    
    def show_main_menu(self):
        """Show main menu"""
        Display.clear_screen()
        
        # Check if session is valid
        if not AuthService.validate_session(self.session_token):
            Display.print_warning("Session has expired, please login again")
            self.running = False
            return
        
        role = self.current_user['role']
        
        # Show different menus based on role
        if role == 'admin':
            self._show_admin_menu()
        elif role == 'front_desk':
            self._show_front_desk_menu()
        elif role == 'housekeeping':
            self._show_housekeeping_menu()
    
    def _show_admin_menu(self):
        """Admin menu"""
        options = [
            "Reservation Management",
            "Operation Management",
            "Room Management",
            "Pricing Configuration",
            "Report Management",
            "System Management",
            "Logout"
        ]
        
        Display.print_menu("Admin Main Menu", options, show_back=False)
        choice = Display.get_choice(len(options))
        
        if choice == 1:
            self.reservation_menu()
        elif choice == 2:
            self.operation_menu()
        elif choice == 3:
            self.room_management_menu()
        elif choice == 4:
            self.pricing_menu()
        elif choice == 5:
            self.report_menu()
        elif choice == 6:
            self.system_menu()
        elif choice == 7 or choice == 0:
            self.logout()
    
    def _show_front_desk_menu(self):
        """Front desk staff menu"""
        options = [
            "Reservation Management",
            "Operation Management",
            "View Room Status",
            "Logout"
        ]
        
        Display.print_menu("Front Desk Staff Main Menu", options, show_back=False)
        choice = Display.get_choice(len(options))
        
        if choice == 1:
            self.reservation_menu()
        elif choice == 2:
            self.operation_menu()
        elif choice == 3:
            self.view_rooms()
        elif choice == 4 or choice == 0:
            self.logout()
    
    def _show_housekeeping_menu(self):
        """Housekeeping staff menu"""
        options = [
            "View Room Status",
            "Update Room Status",
            "Logout"
        ]
        
        Display.print_menu("Housekeeping Staff Main Menu", options, show_back=False)
        choice = Display.get_choice(len(options))
        
        if choice == 1:
            self.view_rooms()
        elif choice == 2:
            self.update_room_status()
        elif choice == 3 or choice == 0:
            self.logout()
    
    # ==================== Reservation Management Menu ====================
    
    def reservation_menu(self):
        """Reservation management menu"""
        while True:
            Display.clear_screen()
            options = [
                "Search Available Rooms",
                "Create New Reservation",
                "Search Reservations",
                "Modify Reservation",
                "Cancel Reservation",
                "View Today's Check-ins",
                "View Current Guests"
            ]
            
            Display.print_menu("Reservation Management", options)
            choice = Display.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                self.search_available_rooms()
            elif choice == 2:
                self.create_reservation()
            elif choice == 3:
                self.search_reservations()
            elif choice == 4:
                self.modify_reservation()
            elif choice == 5:
                self.cancel_reservation()
            elif choice == 6:
                self.view_upcoming_checkins()
            elif choice == 7:
                self.view_current_checkins()
    
    def search_available_rooms(self):
        """Search available rooms"""
        Display.clear_screen()
        Display.print_header("Search Available Rooms")
        
        # Get date range
        check_in = Display.get_input("Check-in date (YYYY-MM-DD)")
        if not check_in:
            return
        
        check_out = Display.get_input("Check-out date (YYYY-MM-DD)")
        if not check_out:
            return
        
        # Get room type (optional)
        room_types = RoomService.get_room_types()
        if room_types:
            Display.print_table(
                [{'ID': rt['room_type_id'], 'Room Type': rt['type_name'], 
                  'Base Price': Display.format_currency(rt['base_price']),
                  'Max Occupancy': rt['max_occupancy']} for rt in room_types],
                title="Available Room Types"
            )
        
        room_type_id = Display.get_input("Room type ID (leave empty for all)", int, allow_empty=True)
        
        # Search available rooms
        available_rooms = RoomService.get_available_rooms(
            check_in, check_out, room_type_id
        )
        
        if not available_rooms:
            Display.print_warning("No available rooms found")
        else:
            # Calculate price and display
            rooms_with_price = []
            for room in available_rooms:
                pricing_info = PricingService.calculate_total_price(
                    room['room_type_id'],
                    check_in,
                    check_out
                )
                
                rooms_with_price.append({
                    'Room Number': room['room_number'],
                    'Room Type': room['type_name'],
                    'Floor': room['floor'],
                    'Max Occupancy': room['max_occupancy'],
                    'Total Price': Display.format_currency(pricing_info['total']),
                    'Nights': pricing_info['nights']
                })
            
            Display.print_table(rooms_with_price, title=f"Available Rooms ({check_in} to {check_out})")
        
        Display.pause()
    
    def create_reservation(self):
        """Create new reservation"""
        Display.clear_screen()
        Display.print_header("Create New Reservation")
        
        # 1. Get check-in information
        check_in = Display.get_input("Check-in date (YYYY-MM-DD)")
        if not check_in:
            return
        
        check_out = Display.get_input("Check-out date (YYYY-MM-DD)")
        if not check_out:
            return
        
        # 2. Display available rooms
        available_rooms = RoomService.get_available_rooms(check_in, check_out)
        
        if not available_rooms:
            Display.print_error("No available rooms for selected dates")
            Display.pause()
            return
        
        rooms_display = []
        for room in available_rooms:
            pricing_info = PricingService.calculate_total_price(
                room['room_type_id'],
                check_in,
                check_out
            )
            rooms_display.append({
                'ID': room['room_id'],
                'Room Number': room['room_number'],
                'Room Type': room['type_name'],
                'Floor': room['floor'],
                'Max Occupancy': room['max_occupancy'],
                'Total Price': Display.format_currency(pricing_info['total'])
            })
        
        Display.print_table(rooms_display, title="Available Rooms")
        
        # 3. Select room
        room_id = Display.get_input("Select room ID", int)
        if not room_id:
            return
        
        # Validate room ID
        selected_room = next((r for r in available_rooms if r['room_id'] == room_id), None)
        if not selected_room:
            Display.print_error("Invalid room ID")
            Display.pause()
            return
        
        # 4. Get guest information
        Display.print_subheader("Guest Information")
        
        guest_info = {
            'first_name': Display.get_input("First name"),
            'last_name': Display.get_input("Last name"),
            'phone': Display.get_input("Phone number"),
            'email': Display.get_input("Email", allow_empty=True),
            'id_number': Display.get_input("ID number", allow_empty=True),
            'address': Display.get_input("Address", allow_empty=True)
        }
        
        if not all([guest_info['first_name'], guest_info['last_name'], guest_info['phone']]):
            Display.print_error("Required information is incomplete")
            Display.pause()
            return
        
        # 5. Other information
        num_guests = Display.get_input("Number of guests", int, default=1)
        if num_guests > selected_room['max_occupancy']:
            Display.print_error(f"Number of guests exceeds room capacity ({selected_room['max_occupancy']} people)")
            Display.pause()
            return
        
        special_requests = Display.get_input("Special requests", allow_empty=True) or ""
        
        # 6. Confirm reservation
        pricing_info = PricingService.calculate_total_price(
            selected_room['room_type_id'],
            check_in,
            check_out
        )
        
        Display.print_subheader("Reservation Confirmation")
        Display.print_detail({
            'Room Number': selected_room['room_number'],
            'Room Type': selected_room['type_name'],
            'Check-in Date': check_in,
            'Check-out Date': check_out,
            'Nights': pricing_info['nights'],
            'Guest': f"{guest_info['last_name']}{guest_info['first_name']}",
            'Number of Guests': num_guests,
            'Total Price': Display.format_currency(pricing_info['total'])
        })
        
        if not Display.confirm("Confirm creating reservation?"):
            Display.print_info("Cancelled")
            Display.pause()
            return
        
        # 7. Create reservation
        success, message, reservation_id = ReservationService.create_reservation(
            guest_info, room_id, check_in, check_out,
            num_guests, special_requests,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    def search_reservations(self):
        """Search reservations"""
        Display.clear_screen()
        Display.print_header("Search Reservations")
        
        Display.print_info("Enter search criteria (leave empty to skip):")
        
        reservation_id = Display.get_input("Reservation ID", int, allow_empty=True)
        guest_name = Display.get_input("Guest name", allow_empty=True)
        phone = Display.get_input("Phone number", allow_empty=True)
        room_number = Display.get_input("Room number", allow_empty=True)
        
        # Search
        reservations = ReservationService.search_reservations(
            guest_name=guest_name,
            phone=phone,
            reservation_id=reservation_id,
            room_number=room_number
        )
        
        if not reservations:
            Display.print_warning("No matching reservations found")
        else:
            display_data = []
            for res in reservations:
                display_data.append({
                    'ID': res['reservation_id'],
                    'Guest': res['guest_name'],
                    'Phone': res['phone'],
                    'Room': res['room_number'],
                    'Room Type': res['room_type'],
                    'Check-in': res['check_in_date'],
                    'Check-out': res['check_out_date'],
                    'Status': res['status'],
                    'Total Price': Display.format_currency(res['total_price'])
                })
            
            Display.print_table(display_data, title="Reservation List")
            
            # Ask if want to view details
            if Display.confirm("View details of a specific reservation?"):
                res_id = Display.get_input("Enter reservation ID", int)
                if res_id:
                    self.view_reservation_detail(res_id)
        
        Display.pause()
    
    def view_reservation_detail(self, reservation_id: int):
        """View reservation details"""
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        
        if not reservation:
            Display.print_error("Reservation does not exist")
            return
        
        Display.print_subheader(f"Reservation Details - {reservation_id}")
        Display.print_detail({
            'Reservation ID': reservation['reservation_id'],
            'Status': reservation['status'],
            'Guest Name': reservation['guest_name'],
            'Phone': reservation['phone'],
            'Email': reservation.get('email', 'N/A'),
            'Room Number': reservation['room_number'],
            'Room Type': reservation['room_type'],
            'Floor': reservation['floor'],
            'Check-in Date': reservation['check_in_date'],
            'Check-out Date': reservation['check_out_date'],
            'Number of Guests': reservation['num_guests'],
            'Total Price': Display.format_currency(reservation['total_price']),
            'Special Requests': reservation.get('special_requests') or 'None',
            'Created At': Display.format_datetime(reservation['created_at']),
            'Created By': reservation['created_by_name']
        })
    
    def modify_reservation(self):
        """Modify reservation"""
        Display.clear_screen()
        Display.print_header("Modify Reservation")
        
        reservation_id = Display.get_input("Reservation ID", int)
        if not reservation_id:
            return
        
        # Get reservation details
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            Display.print_error("Reservation does not exist")
            Display.pause()
            return
        
        # Display current information
        Display.print_subheader("Current Reservation Information")
        Display.print_detail({
            'Reservation ID': reservation['reservation_id'],
            'Status': reservation['status'],
            'Guest': reservation['guest_name'],
            'Room': f"{reservation['room_number']} ({reservation['room_type']})",
            'Check-in Date': reservation['check_in_date'],
            'Check-out Date': reservation['check_out_date'],
            'Number of Guests': reservation['num_guests']
        })
        
        if reservation['status'] != 'Confirmed':
            Display.print_error(f"Reservation status is {reservation['status']}, cannot modify")
            Display.pause()
            return
        
        # Get modification content
        Display.print_info("Enter content to modify (leave empty to keep unchanged):")
        
        new_check_in = Display.get_input(f"New check-in date (current: {reservation['check_in_date']})", allow_empty=True)
        new_check_out = Display.get_input(f"New check-out date (current: {reservation['check_out_date']})", allow_empty=True)
        new_num_guests = Display.get_input(f"New number of guests (current: {reservation['num_guests']})", int, allow_empty=True)
        new_special_requests = Display.get_input("New special requests", allow_empty=True)
        
        if not any([new_check_in, new_check_out, new_num_guests, new_special_requests]):
            Display.print_info("No content was modified")
            Display.pause()
            return
        
        if not Display.confirm("Confirm modifying reservation?"):
            Display.print_info("Cancelled")
            Display.pause()
            return
        
        # Execute modification
        success, message = ReservationService.modify_reservation(
            reservation_id,
            new_check_in=new_check_in or None,
            new_check_out=new_check_out or None,
            new_num_guests=new_num_guests,
            new_special_requests=new_special_requests if new_special_requests else None,
            user_id=self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    def cancel_reservation(self):
        """Cancel reservation"""
        Display.clear_screen()
        Display.print_header("Cancel Reservation")
        
        reservation_id = Display.get_input("Reservation ID", int)
        if not reservation_id:
            return
        
        # Get reservation details
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            Display.print_error("Reservation does not exist")
            Display.pause()
            return
        
        # Display reservation information
        Display.print_detail({
            'Reservation ID': reservation['reservation_id'],
            'Guest': reservation['guest_name'],
            'Room': reservation['room_number'],
            'Check-in Date': reservation['check_in_date'],
            'Check-out Date': reservation['check_out_date'],
            'Status': reservation['status']
        })
        
        if not Display.confirm("Confirm canceling this reservation?"):
            Display.print_info("Operation cancelled")
            Display.pause()
            return
        
        # Execute cancellation
        success, message = ReservationService.cancel_reservation(
            reservation_id,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    def view_upcoming_checkins(self):
        """View today's check-ins"""
        Display.clear_screen()
        
        reservations = ReservationService.get_upcoming_checkins(days=1)
        
        if not reservations:
            Display.print_warning("No expected check-ins today")
        else:
            display_data = [{
                'Reservation ID': res['reservation_id'],
                'Guest': res['guest_name'],
                'Phone': res['phone'],
                'Room': res['room_number'],
                'Room Type': res['room_type'],
                'Check-in Date': res['check_in_date'],
                'Check-out Date': res['check_out_date']
            } for res in reservations]
            
            Display.print_table(display_data, title="Today's Expected Check-ins")
        
        Display.pause()
    
    def view_current_checkins(self):
        """View current check-ins"""
        Display.clear_screen()
        
        reservations = ReservationService.get_current_checkins()
        
        if not reservations:
            Display.print_warning("No current guests checked in")
        else:
            display_data = [{
                'Reservation ID': res['reservation_id'],
                'Guest': res['guest_name'],
                'Phone': res['phone'],
                'Room': res['room_number'],
                'Room Type': res['room_type'],
                'Check-in Date': res['check_in_date'],
                'Check-out Date': res['check_out_date']
            } for res in reservations]
            
            Display.print_table(display_data, title="Current Checked-in Guests")
        
        Display.pause()
    
    # ==================== Operation Management Menu ====================
    
    def operation_menu(self):
        """Operation management menu"""
        while True:
            Display.clear_screen()
            options = [
                "Check-in Guest",
                "Check-out Guest",
                "View Today's Check-ins",
                "View Current Check-ins"
            ]
            
            Display.print_menu("Operation Management", options)
            choice = Display.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                self.check_in()
            elif choice == 2:
                self.check_out()
            elif choice == 3:
                self.view_upcoming_checkins()
            elif choice == 4:
                self.view_current_checkins()
    
    def check_in(self):
        """Check-in guest"""
        Display.clear_screen()
        Display.print_header("Check-in Guest")
        
        reservation_id = Display.get_input("Reservation ID", int)
        if not reservation_id:
            return
        
        # Get reservation details
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            Display.print_error("Reservation does not exist")
            Display.pause()
            return
        
        # Display reservation information
        Display.print_detail({
            'Reservation ID': reservation['reservation_id'],
            'Guest': reservation['guest_name'],
            'Phone': reservation['phone'],
            'Room': reservation['room_number'],
            'Check-in Date': reservation['check_in_date'],
            'Check-out Date': reservation['check_out_date'],
            'Status': reservation['status']
        })
        
        if not Display.confirm("Confirm check-in?"):
            Display.print_info("Cancelled")
            Display.pause()
            return
        
        # Execute check-in
        success, message = ReservationService.check_in(
            reservation_id,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    def check_out(self):
        """Check-out guest"""
        Display.clear_screen()
        Display.print_header("Check-out Guest")
        
        reservation_id = Display.get_input("Reservation ID", int)
        if not reservation_id:
            return
        
        # Get reservation details
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            Display.print_error("Reservation does not exist")
            Display.pause()
            return
        
        # Display reservation information
        Display.print_detail({
            'Reservation ID': reservation['reservation_id'],
            'Guest': reservation['guest_name'],
            'Room': reservation['room_number'],
            'Check-in Date': reservation['check_in_date'],
            'Check-out Date': reservation['check_out_date'],
            'Amount Due': Display.format_currency(reservation['total_price']),
            'Status': reservation['status']
        })
        
        if reservation['status'] != 'CheckedIn':
            Display.print_error(f"Reservation status is {reservation['status']}, cannot check out")
            Display.pause()
            return
        
        # Get payment information
        Display.print_subheader("Payment Information")
        Display.print_info("Payment methods: 1-Cash, 2-Credit Card, 3-Debit Card, 4-Online Transfer")
        
        payment_method_map = {
            1: 'Cash',
            2: 'CreditCard',
            3: 'DebitCard',
            4: 'OnlineTransfer'
        }
        
        method_choice = Display.get_input("Select payment method", int)
        if method_choice not in payment_method_map:
            Display.print_error("Invalid payment method")
            Display.pause()
            return
        
        payment_method = payment_method_map[method_choice]
        payment_amount = Display.get_input(
            "Payment amount", 
            float, 
            default=float(reservation['total_price'])
        )
        
        if not Display.confirm(f"Confirm receiving {Display.format_currency(payment_amount)}?"):
            Display.print_info("Cancelled")
            Display.pause()
            return
        
        # Execute check-out
        success, message = ReservationService.check_out(
            reservation_id,
            payment_method,
            payment_amount,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    # ==================== Room Management Menu ====================
    
    def view_rooms(self):
        """View room status"""
        Display.clear_screen()
        Display.print_header("Room Status")
        
        # Get statistics
        stats = RoomService.get_room_statistics()
        Display.print_info(
            f"Total Rooms: {stats.get('total_rooms', 0)} | "
            f"Clean: {stats.get('clean_rooms', 0)} | "
            f"Dirty: {stats.get('dirty_rooms', 0)} | "
            f"Occupied: {stats.get('occupied_rooms', 0)} | "
            f"Maintenance: {stats.get('maintenance_rooms', 0)}"
        )
        
        # Get all rooms
        rooms = RoomService.list_all_rooms()
        
        display_data = [{
            'Room Number': room['room_number'],
            'Room Type': room['type_name'],
            'Floor': room['floor'],
            'Status': room['status'],
            'Max Occupancy': room['max_occupancy'],
            'Base Price': Display.format_currency(room['base_price'])
        } for room in rooms]
        
        Display.print_table(display_data, title="Room List")
        Display.pause()
    
    def room_management_menu(self):
        """Room management menu (Admin)"""
        while True:
            Display.clear_screen()
            options = [
                "View All Rooms",
                "Update Room Status",
                "Add Room",
                "Room Type Management"
            ]
            
            Display.print_menu("Room Management", options)
            choice = Display.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                self.view_rooms()
            elif choice == 2:
                self.update_room_status()
            elif choice == 3:
                self.add_room()
            elif choice == 4:
                self.room_type_menu()
    
    def update_room_status(self):
        """Update room status"""
        Display.clear_screen()
        Display.print_header("Update Room Status")
        
        room_number = Display.get_input("Room number")
        if not room_number:
            return
        
        # Get room information
        room = RoomService.get_room_by_number(room_number)
        if not room:
            Display.print_error("Room does not exist")
            Display.pause()
            return
        
        Display.print_info(f"Current status: {room['status']}")
        Display.print_info("Status options: 1-Clean, 2-Dirty, 3-Occupied, 4-Maintenance")
        
        status_map = {
            1: 'Clean',
            2: 'Dirty',
            3: 'Occupied',
            4: 'Maintenance'
        }
        
        status_choice = Display.get_input("Select new status", int)
        if status_choice not in status_map:
            Display.print_error("Invalid status selection")
            Display.pause()
            return
        
        new_status = status_map[status_choice]
        
        if not Display.confirm(f"Confirm changing room {room_number} status to {new_status}?"):
            Display.print_info("Cancelled")
            Display.pause()
            return
        
        # Update status
        success, message = RoomService.update_room_status(
            room['room_id'],
            new_status,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    def add_room(self):
        """Add room"""
        Display.clear_screen()
        Display.print_header("Add Room")
        
        # Display room type list
        room_types = RoomService.get_room_types()
        Display.print_table(
            [{'ID': rt['room_type_id'], 'Room Type': rt['type_name'], 
              'Price': Display.format_currency(rt['base_price'])} 
             for rt in room_types],
            title="Available Room Types"
        )
        
        room_number = Display.get_input("Room number")
        room_type_id = Display.get_input("Room type ID", int)
        floor = Display.get_input("Floor", int)
        
        if not all([room_number, room_type_id, floor]):
            Display.print_error("Information incomplete")
            Display.pause()
            return
        
        # Add room
        success, message, room_id = RoomService.add_room(
            room_number,
            room_type_id,
            floor,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    def room_type_menu(self):
        """Room type management menu"""
        while True:
            Display.clear_screen()
            options = [
                "View All Room Types",
                "Add Room Type",
                "Update Room Type"
            ]
            
            Display.print_menu("Room Type Management", options)
            choice = Display.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                self.view_room_types()
            elif choice == 2:
                self.add_room_type()
            elif choice == 3:
                self.update_room_type()
    
    def view_room_types(self):
        """View all room types"""
        Display.clear_screen()
        
        room_types = RoomService.get_room_types()
        
        display_data = [{
            'ID': rt['room_type_id'],
            'Room Type Name': rt['type_name'],
            'Base Price': Display.format_currency(rt['base_price']),
            'Max Occupancy': rt['max_occupancy'],
            'Description': rt['description'][:30] + '...' if len(rt['description']) > 30 else rt['description']
        } for rt in room_types]
        
        Display.print_table(display_data, title="Room Type List")
        Display.pause()
    
    def add_room_type(self):
        """Add room type"""
        Display.clear_screen()
        Display.print_header("Add Room Type")
        
        type_name = Display.get_input("Room type name")
        description = Display.get_input("Description")
        base_price = Display.get_input("Base price", float)
        max_occupancy = Display.get_input("Maximum occupancy", int)
        amenities = Display.get_input("Amenities (comma separated)")
        
        if not all([type_name, description, base_price, max_occupancy, amenities]):
            Display.print_error("Information incomplete")
            Display.pause()
            return
        
        # Add room type
        success, message, room_type_id = RoomService.add_room_type(
            type_name, description, base_price,
            max_occupancy, amenities,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    def update_room_type(self):
        """Update room type"""
        Display.clear_screen()
        Display.print_header("Update Room Type")
        
        # Display room type list
        self.view_room_types()
        
        room_type_id = Display.get_input("Room type ID", int)
        if not room_type_id:
            return
        
        # Get current room type
        room_type = RoomService.get_room_type_by_id(room_type_id)
        if not room_type:
            Display.print_error("Room type does not exist")
            Display.pause()
            return
        
        Display.print_info("Enter new values (leave empty to keep unchanged):")
        
        new_name = Display.get_input(f"Room type name (current: {room_type['type_name']})", allow_empty=True)
        new_desc = Display.get_input(f"Description (current: {room_type['description'][:30]}...)", allow_empty=True)
        new_price = Display.get_input(f"Base price (current: {room_type['base_price']})", float, allow_empty=True)
        new_occupancy = Display.get_input(f"Max occupancy (current: {room_type['max_occupancy']})", int, allow_empty=True)
        new_amenities = Display.get_input(f"Amenities", allow_empty=True)
        
        # Update room type
        success, message = RoomService.update_room_type(
            room_type_id,
            type_name=new_name or None,
            description=new_desc or None,
            base_price=new_price,
            max_occupancy=new_occupancy,
            amenities=new_amenities or None,
            user_id=self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    # ==================== Pricing Management Menu ====================
    
    def pricing_menu(self):
        """Pricing management menu"""
        while True:
            Display.clear_screen()
            options = [
                "View Seasonal Pricing",
                "Add Seasonal Pricing",
                "Delete Seasonal Pricing"
            ]
            
            Display.print_menu("Pricing Configuration", options)
            choice = Display.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                self.view_seasonal_pricing()
            elif choice == 2:
                self.add_seasonal_pricing()
            elif choice == 3:
                self.delete_seasonal_pricing()
    
    def view_seasonal_pricing(self):
        """View seasonal pricing"""
        Display.clear_screen()
        
        pricing_rules = PricingService.list_seasonal_pricing()
        
        if not pricing_rules:
            Display.print_warning("No seasonal pricing rules")
        else:
            display_data = [{
                'ID': pr['pricing_id'],
                'Room Type': pr['type_name'],
                'Season': pr['season_name'],
                'Start Date': pr['start_date'],
                'End Date': pr['end_date'],
                'Price Multiplier': pr['price_multiplier'] or '-',
                'Fixed Price': Display.format_currency(pr['fixed_price']) if pr['fixed_price'] else '-'
            } for pr in pricing_rules]
            
            Display.print_table(display_data, title="Seasonal Pricing Rules")
        
        Display.pause()
    
    def add_seasonal_pricing(self):
        """Add seasonal pricing"""
        Display.clear_screen()
        Display.print_header("Add Seasonal Pricing")
        
        # Display room type list
        room_types = RoomService.get_room_types()
        Display.print_table(
            [{'ID': rt['room_type_id'], 'Room Type': rt['type_name'], 
              'Base Price': Display.format_currency(rt['base_price'])} 
             for rt in room_types],
            title="Room Type List"
        )
        
        room_type_id = Display.get_input("Room type ID", int)
        season_name = Display.get_input("Season name")
        start_date = Display.get_input("Start date (YYYY-MM-DD)")
        end_date = Display.get_input("End date (YYYY-MM-DD)")
        
        Display.print_info("Pricing method: 1-Price multiplier, 2-Fixed price")
        pricing_type = Display.get_input("Select pricing method", int)
        
        price_multiplier = None
        fixed_price = None
        
        if pricing_type == 1:
            price_multiplier = Display.get_input("Price multiplier (e.g.: 1.5 means 150%)", float)
        elif pricing_type == 2:
            fixed_price = Display.get_input("Fixed price", float)
        else:
            Display.print_error("Invalid pricing method")
            Display.pause()
            return
        
        # Add pricing rule
        success, message, pricing_id = PricingService.add_seasonal_pricing(
            room_type_id, season_name, start_date, end_date,
            price_multiplier, fixed_price,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    def delete_seasonal_pricing(self):
        """Delete seasonal pricing"""
        Display.clear_screen()
        Display.print_header("Delete Seasonal Pricing")
        
        # Display existing pricing rules
        self.view_seasonal_pricing()
        
        pricing_id = Display.get_input("Pricing rule ID", int)
        if not pricing_id:
            return
        
        if not Display.confirm("Confirm deleting this pricing rule?"):
            Display.print_info("Cancelled")
            Display.pause()
            return
        
        # Delete pricing rule
        success, message = PricingService.delete_seasonal_pricing(
            pricing_id,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    # ==================== Report Management Menu ====================
    
    def report_menu(self):
        """Report management menu"""
        while True:
            Display.clear_screen()
            options = [
                "Occupancy Report",
                "Revenue Report",
                "Audit Log Query",
                "Database Backup"
            ]
            
            Display.print_menu("Report Management", options)
            choice = Display.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                self.occupancy_report()
            elif choice == 2:
                self.revenue_report()
            elif choice == 3:
                self.view_audit_logs()
            elif choice == 4:
                self.backup_database()
    
    def occupancy_report(self):
        """Occupancy report"""
        Display.clear_screen()
        Display.print_header("Occupancy Report")
        
        start_date = Display.get_input("Start date (YYYY-MM-DD)")
        end_date = Display.get_input("End date (YYYY-MM-DD)")
        
        if not start_date or not end_date:
            return
        
        # Generate report
        report = ReportService.generate_occupancy_report(start_date, end_date)
        
        if 'error' in report:
            Display.print_error(report['error'])
            Display.pause()
            return
        
        # Display summary
        Display.print_subheader("Report Summary")
        Display.print_detail({
            'Report Period': f"{report['start_date']} to {report['end_date']}",
            'Total Rooms': report['total_rooms'],
            'Report Days': report['days'],
            'Average Occupancy Rate': Display.format_percentage(report['average_occupancy_rate'])
        })
        
        # Display daily data (first 10 days)
        if report['daily_data']:
            display_data = [{
                'Date': day['date'],
                'Total Rooms': day['total_rooms'],
                'Occupied': day['occupied_rooms'],
                'Available': day['available_rooms'],
                'Occupancy Rate': Display.format_percentage(day['occupancy_rate'])
            } for day in report['daily_data'][:10]]
            
            Display.print_table(display_data, title="Daily Occupancy (First 10 Days)")
        
        # Ask if export
        if Display.confirm("Export to CSV file?"):
            filename = f"occupancy_report_{start_date}_{end_date}.csv"
            success, result = ReportService.export_to_csv(report, filename, 'occupancy')
            
            if success:
                Display.print_success(f"Report exported: {result}")
            else:
                Display.print_error(result)
        
        Display.pause()
    
    def revenue_report(self):
        """Revenue report"""
        Display.clear_screen()
        Display.print_header("Revenue Report")
        
        start_date = Display.get_input("Start date (YYYY-MM-DD)")
        end_date = Display.get_input("End date (YYYY-MM-DD)")
        
        if not start_date or not end_date:
            return
        
        # Generate report
        report = ReportService.generate_revenue_report(start_date, end_date)
        
        if 'error' in report:
            Display.print_error(report['error'])
            Display.pause()
            return
        
        # Display summary
        Display.print_subheader("Revenue Summary")
        Display.print_detail({
            'Report Period': f"{report['start_date']} to {report['end_date']}",
            'Total Reservations': report['total_reservations'],
            'Total Revenue': Display.format_currency(report['total_revenue']),
            'Average Revenue per Reservation': Display.format_currency(report['average_revenue_per_reservation'])
        })
        
        # Statistics by room type
        if report['by_room_type']:
            Display.print_table(
                [{
                    'Room Type': item['room_type'],
                    'Reservations': item['reservations'],
                    'Revenue': Display.format_currency(item['revenue'])
                } for item in report['by_room_type']],
                title="Statistics by Room Type"
            )
        
        # Statistics by payment method
        if report['by_payment_method']:
            Display.print_table(
                [{
                    'Payment Method': item['payment_method'],
                    'Transactions': item['count'],
                    'Amount': Display.format_currency(item['amount'])
                } for item in report['by_payment_method']],
                title="Statistics by Payment Method"
            )
        
        # Ask if export
        if Display.confirm("Export to CSV file?"):
            filename = f"revenue_report_{start_date}_{end_date}.csv"
            success, result = ReportService.export_to_csv(report, filename, 'revenue')
            
            if success:
                Display.print_success(f"Report exported: {result}")
            else:
                Display.print_error(result)
        
        Display.pause()
    
    def view_audit_logs(self):
        """View audit logs"""
        Display.clear_screen()
        Display.print_header("Audit Log Query")
        
        Display.print_info("Enter search criteria (leave empty to skip):")
        
        operation_type = Display.get_input("Operation type (CREATE/UPDATE/DELETE etc.)", allow_empty=True)
        table_name = Display.get_input("Table name", allow_empty=True)
        start_date = Display.get_input("Start date (YYYY-MM-DD)", allow_empty=True)
        end_date = Display.get_input("End date (YYYY-MM-DD)", allow_empty=True)
        
        # Query logs
        logs = ReportService.get_audit_logs(
            operation_type=operation_type or None,
            table_name=table_name or None,
            start_date=start_date or None,
            end_date=end_date or None,
            limit=50
        )
        
        if not logs:
            Display.print_warning("No matching logs found")
        else:
            display_data = [{
                'Time': Display.format_datetime(log['timestamp']),
                'User': log['username'],
                'Operation': log['operation_type'],
                'Table': log['table_name'] or '-',
                'Record ID': log['record_id'] or '-',
                'Description': (log['description'][:40] + '...') if log['description'] and len(log['description']) > 40 else log['description']
            } for log in logs]
            
            Display.print_table(display_data, title=f"Audit Logs (Latest {len(logs)} entries)")
        
        Display.pause()
    
    def backup_database(self):
        """Database backup"""
        Display.clear_screen()
        Display.print_header("Database Backup")
        
        backup_name = Display.get_input("Backup filename", default="hrms_backup")
        
        if not Display.confirm("Confirm database backup?"):
            Display.print_info("Cancelled")
            Display.pause()
            return
        
        Display.print_info("Backing up database...")
        
        success, result = ReportService.backup_database(
            backup_name,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(f"Database backup successful: {result}")
        else:
            Display.print_error(result)
        
        Display.pause()
    
    # ==================== System Management Menu ====================
    
    def system_menu(self):
        """System management menu"""
        while True:
            Display.clear_screen()
            options = [
                "Change Password",
                "View Backup History",
                "System Statistics"
            ]
            
            Display.print_menu("System Management", options)
            choice = Display.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                self.change_password()
            elif choice == 2:
                self.view_backup_history()
            elif choice == 3:
                self.system_statistics()
    
    def change_password(self):
        """Change password"""
        Display.clear_screen()
        Display.print_header("Change Password")
        
        old_password = Display.get_input("Current password")
        new_password = Display.get_input("New password")
        confirm_password = Display.get_input("Confirm new password")
        
        if not all([old_password, new_password, confirm_password]):
            Display.print_error("Information incomplete")
            Display.pause()
            return
        
        if new_password != confirm_password:
            Display.print_error("New passwords do not match")
            Display.pause()
            return
        
        # Change password
        success, message = AuthService.change_password(
            self.current_user['user_id'],
            old_password,
            new_password
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    def view_backup_history(self):
        """View backup history"""
        Display.clear_screen()
        
        backups = ReportService.list_backups()
        
        if not backups:
            Display.print_warning("No backup records")
        else:
            display_data = [{
                'ID': backup['backup_id'],
                'Filename': backup['backup_file'].split('/')[-1] if '/' in backup['backup_file'] else backup['backup_file'],
                'Size(KB)': f"{backup['backup_size'] / 1024:.2f}" if backup['backup_size'] else '-',
                'Type': backup['backup_type'],
                'Status': backup['status'],
                'Created By': backup['username'],
                'Time': Display.format_datetime(backup['created_at'])
            } for backup in backups]
            
            Display.print_table(display_data, title="Backup History")
        
        Display.pause()
    
    def system_statistics(self):
        """System statistics"""
        Display.clear_screen()
        Display.print_header("System Statistics")
        
        # Room statistics
        room_stats = RoomService.get_room_statistics()
        Display.print_subheader("Room Status Statistics")
        Display.print_detail({
            'Total Rooms': room_stats.get('total_rooms', 0),
            'Clean Available': room_stats.get('clean_rooms', 0),
            'Dirty for Cleaning': room_stats.get('dirty_rooms', 0),
            'Occupied': room_stats.get('occupied_rooms', 0),
            'Under Maintenance': room_stats.get('maintenance_rooms', 0)
        })
        
        # Today's reservation statistics
        today_checkins = ReservationService.get_upcoming_checkins(days=0)
        current_guests = ReservationService.get_current_checkins()
        
        Display.print_subheader("Reservation Statistics")
        Display.print_detail({
            'Expected Check-ins Today': len(today_checkins),
            'Current Guests': len(current_guests)
        })
        
        # Active sessions
        active_sessions = AuthService.get_active_sessions_count()
        Display.print_subheader("System Status")
        Display.print_detail({
            'Active Sessions': active_sessions
        })
        
        Display.pause()
    
    @staticmethod
    def _get_role_name(role: str) -> str:
        """Get role English name"""
        role_names = {
            'admin': 'Administrator',
            'front_desk': 'Front Desk Staff',
            'housekeeping': 'Housekeeping Staff'
        }
        return role_names.get(role, role)
