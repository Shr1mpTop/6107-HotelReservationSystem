"""
主菜单模块
处理CLI界面的菜单导航和用户交互
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.display import Display
from services.auth_service import AuthService
from services.reservation_service import ReservationService
from services.room_service import RoomService
from services.pricing_service import PricingService
from services.report_service import ReportService


class HRMSMenu:
    """酒店预订管理系统菜单类"""
    
    def __init__(self):
        self.current_user = None
        self.session_token = None
        self.running = True
    
    def start(self):
        """启动系统"""
        Display.clear_screen()
        Display.print_logo()
        
        # 登录
        if not self.login():
            return
        
        # 主菜单循环
        while self.running:
            self.show_main_menu()
    
    def login(self) -> bool:
        """用户登录"""
        Display.print_header("用户登录")
        
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            username = Display.get_input("用户名")
            if username is None:  # 用户取消
                return False
            
            password = Display.get_input("密码")
            if password is None:  # 用户取消
                return False
            
            # 尝试登录
            result = AuthService.login(username, password)
            
            if result:
                self.session_token = result['session_token']
                self.current_user = result['user']
                
                Display.print_success(f"欢迎, {self.current_user['full_name']}!")
                Display.print_info(f"角色: {self._get_role_name(self.current_user['role'])}")
                Display.pause()
                return True
            else:
                attempts += 1
                remaining = max_attempts - attempts
                if remaining > 0:
                    Display.print_error(f"用户名或密码错误，还有 {remaining} 次尝试机会")
                else:
                    Display.print_error("登录失败次数过多，系统退出")
                    return False
        
        return False
    
    def logout(self):
        """用户登出"""
        if self.session_token:
            AuthService.logout(self.session_token)
            Display.print_success("已安全退出系统")
        self.running = False
    
    def show_main_menu(self):
        """显示主菜单"""
        Display.clear_screen()
        
        # 检查会话是否有效
        if not AuthService.validate_session(self.session_token):
            Display.print_warning("会话已过期，请重新登录")
            self.running = False
            return
        
        role = self.current_user['role']
        
        # 根据角色显示不同的菜单
        if role == 'admin':
            self._show_admin_menu()
        elif role == 'front_desk':
            self._show_front_desk_menu()
        elif role == 'housekeeping':
            self._show_housekeeping_menu()
    
    def _show_admin_menu(self):
        """管理员菜单"""
        options = [
            "预订管理",
            "运营管理",
            "房间管理",
            "定价配置",
            "报表管理",
            "系统管理",
            "退出登录"
        ]
        
        Display.print_menu("管理员主菜单", options, show_back=False)
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
        """前台员工菜单"""
        options = [
            "预订管理",
            "运营管理",
            "查看房间状态",
            "退出登录"
        ]
        
        Display.print_menu("前台员工主菜单", options, show_back=False)
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
        """客房员工菜单"""
        options = [
            "查看房间状态",
            "更新房间状态",
            "退出登录"
        ]
        
        Display.print_menu("客房员工主菜单", options, show_back=False)
        choice = Display.get_choice(len(options))
        
        if choice == 1:
            self.view_rooms()
        elif choice == 2:
            self.update_room_status()
        elif choice == 3 or choice == 0:
            self.logout()
    
    # ==================== 预订管理菜单 ====================
    
    def reservation_menu(self):
        """预订管理菜单"""
        while True:
            Display.clear_screen()
            options = [
                "查询可用房间",
                "创建新预订",
                "查询预订",
                "修改预订",
                "取消预订",
                "查看今日入住",
                "查看当前在住"
            ]
            
            Display.print_menu("预订管理", options)
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
        """查询可用房间"""
        Display.clear_screen()
        Display.print_header("查询可用房间")
        
        # 获取日期范围
        check_in = Display.get_input("入住日期 (YYYY-MM-DD)")
        if not check_in:
            return
        
        check_out = Display.get_input("退房日期 (YYYY-MM-DD)")
        if not check_out:
            return
        
        # 获取房型（可选）
        room_types = RoomService.get_room_types()
        if room_types:
            Display.print_table(
                [{'ID': rt['room_type_id'], '房型': rt['type_name'], 
                  '基础价格': Display.format_currency(rt['base_price']),
                  '最大入住': rt['max_occupancy']} for rt in room_types],
                title="可选房型"
            )
        
        room_type_id = Display.get_input("房型ID (留空查询所有)", int, allow_empty=True)
        
        # 查询可用房间
        available_rooms = RoomService.get_available_rooms(
            check_in, check_out, room_type_id
        )
        
        if not available_rooms:
            Display.print_warning("没有找到可用房间")
        else:
            # 计算价格并显示
            rooms_with_price = []
            for room in available_rooms:
                pricing_info = PricingService.calculate_total_price(
                    room['room_type_id'],
                    check_in,
                    check_out
                )
                
                rooms_with_price.append({
                    '房间号': room['room_number'],
                    '房型': room['type_name'],
                    '楼层': room['floor'],
                    '最大入住': room['max_occupancy'],
                    '总价': Display.format_currency(pricing_info['total']),
                    '夜数': pricing_info['nights']
                })
            
            Display.print_table(rooms_with_price, title=f"可用房间 ({check_in} 至 {check_out})")
        
        Display.pause()
    
    def create_reservation(self):
        """创建新预订"""
        Display.clear_screen()
        Display.print_header("创建新预订")
        
        # 1. 获取入住信息
        check_in = Display.get_input("入住日期 (YYYY-MM-DD)")
        if not check_in:
            return
        
        check_out = Display.get_input("退房日期 (YYYY-MM-DD)")
        if not check_out:
            return
        
        # 2. 显示可用房间
        available_rooms = RoomService.get_available_rooms(check_in, check_out)
        
        if not available_rooms:
            Display.print_error("所选日期没有可用房间")
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
                '房间号': room['room_number'],
                '房型': room['type_name'],
                '楼层': room['floor'],
                '最大入住': room['max_occupancy'],
                '总价': Display.format_currency(pricing_info['total'])
            })
        
        Display.print_table(rooms_display, title="可用房间")
        
        # 3. 选择房间
        room_id = Display.get_input("选择房间ID", int)
        if not room_id:
            return
        
        # 验证房间ID
        selected_room = next((r for r in available_rooms if r['room_id'] == room_id), None)
        if not selected_room:
            Display.print_error("无效的房间ID")
            Display.pause()
            return
        
        # 4. 获取客人信息
        Display.print_subheader("客人信息")
        
        guest_info = {
            'first_name': Display.get_input("名"),
            'last_name': Display.get_input("姓"),
            'phone': Display.get_input("手机号"),
            'email': Display.get_input("邮箱", allow_empty=True),
            'id_number': Display.get_input("身份证号", allow_empty=True),
            'address': Display.get_input("地址", allow_empty=True)
        }
        
        if not all([guest_info['first_name'], guest_info['last_name'], guest_info['phone']]):
            Display.print_error("必填信息不完整")
            Display.pause()
            return
        
        # 5. 其他信息
        num_guests = Display.get_input("客人数量", int, default=1)
        if num_guests > selected_room['max_occupancy']:
            Display.print_error(f"客人数量超过房间最大容纳量 ({selected_room['max_occupancy']}人)")
            Display.pause()
            return
        
        special_requests = Display.get_input("特殊要求", allow_empty=True) or ""
        
        # 6. 确认预订
        pricing_info = PricingService.calculate_total_price(
            selected_room['room_type_id'],
            check_in,
            check_out
        )
        
        Display.print_subheader("预订确认")
        Display.print_detail({
            '房间号': selected_room['room_number'],
            '房型': selected_room['type_name'],
            '入住日期': check_in,
            '退房日期': check_out,
            '夜数': pricing_info['nights'],
            '客人': f"{guest_info['last_name']}{guest_info['first_name']}",
            '客人数量': num_guests,
            '总价': Display.format_currency(pricing_info['total'])
        })
        
        if not Display.confirm("确认创建预订?"):
            Display.print_info("已取消")
            Display.pause()
            return
        
        # 7. 创建预订
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
        """查询预订"""
        Display.clear_screen()
        Display.print_header("查询预订")
        
        Display.print_info("请输入查询条件（留空跳过）:")
        
        reservation_id = Display.get_input("预订ID", int, allow_empty=True)
        guest_name = Display.get_input("客人姓名", allow_empty=True)
        phone = Display.get_input("手机号", allow_empty=True)
        room_number = Display.get_input("房间号", allow_empty=True)
        
        # 查询
        reservations = ReservationService.search_reservations(
            guest_name=guest_name,
            phone=phone,
            reservation_id=reservation_id,
            room_number=room_number
        )
        
        if not reservations:
            Display.print_warning("没有找到匹配的预订")
        else:
            display_data = []
            for res in reservations:
                display_data.append({
                    'ID': res['reservation_id'],
                    '客人': res['guest_name'],
                    '手机': res['phone'],
                    '房间': res['room_number'],
                    '房型': res['room_type'],
                    '入住': res['check_in_date'],
                    '退房': res['check_out_date'],
                    '状态': res['status'],
                    '总价': Display.format_currency(res['total_price'])
                })
            
            Display.print_table(display_data, title="预订列表")
            
            # 询问是否查看详情
            if Display.confirm("查看某个预订的详细信息?"):
                res_id = Display.get_input("输入预订ID", int)
                if res_id:
                    self.view_reservation_detail(res_id)
        
        Display.pause()
    
    def view_reservation_detail(self, reservation_id: int):
        """查看预订详情"""
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        
        if not reservation:
            Display.print_error("预订不存在")
            return
        
        Display.print_subheader(f"预订详情 - {reservation_id}")
        Display.print_detail({
            '预订号': reservation['reservation_id'],
            '状态': reservation['status'],
            '客人姓名': reservation['guest_name'],
            '手机号': reservation['phone'],
            '邮箱': reservation.get('email', 'N/A'),
            '房间号': reservation['room_number'],
            '房型': reservation['room_type'],
            '楼层': reservation['floor'],
            '入住日期': reservation['check_in_date'],
            '退房日期': reservation['check_out_date'],
            '客人数量': reservation['num_guests'],
            '总价': Display.format_currency(reservation['total_price']),
            '特殊要求': reservation.get('special_requests') or '无',
            '创建时间': Display.format_datetime(reservation['created_at']),
            '创建者': reservation['created_by_name']
        })
    
    def modify_reservation(self):
        """修改预订"""
        Display.clear_screen()
        Display.print_header("修改预订")
        
        reservation_id = Display.get_input("预订ID", int)
        if not reservation_id:
            return
        
        # 获取预订详情
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            Display.print_error("预订不存在")
            Display.pause()
            return
        
        # 显示当前信息
        Display.print_subheader("当前预订信息")
        Display.print_detail({
            '预订号': reservation['reservation_id'],
            '状态': reservation['status'],
            '客人': reservation['guest_name'],
            '房间': f"{reservation['room_number']} ({reservation['room_type']})",
            '入住日期': reservation['check_in_date'],
            '退房日期': reservation['check_out_date'],
            '客人数量': reservation['num_guests']
        })
        
        if reservation['status'] != 'Confirmed':
            Display.print_error(f"预订状态为 {reservation['status']}，无法修改")
            Display.pause()
            return
        
        # 获取修改内容
        Display.print_info("请输入要修改的内容（留空保持不变）:")
        
        new_check_in = Display.get_input(f"新入住日期 (当前: {reservation['check_in_date']})", allow_empty=True)
        new_check_out = Display.get_input(f"新退房日期 (当前: {reservation['check_out_date']})", allow_empty=True)
        new_num_guests = Display.get_input(f"新客人数量 (当前: {reservation['num_guests']})", int, allow_empty=True)
        new_special_requests = Display.get_input("新特殊要求", allow_empty=True)
        
        if not any([new_check_in, new_check_out, new_num_guests, new_special_requests]):
            Display.print_info("没有修改任何内容")
            Display.pause()
            return
        
        if not Display.confirm("确认修改预订?"):
            Display.print_info("已取消")
            Display.pause()
            return
        
        # 执行修改
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
        """取消预订"""
        Display.clear_screen()
        Display.print_header("取消预订")
        
        reservation_id = Display.get_input("预订ID", int)
        if not reservation_id:
            return
        
        # 获取预订详情
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            Display.print_error("预订不存在")
            Display.pause()
            return
        
        # 显示预订信息
        Display.print_detail({
            '预订号': reservation['reservation_id'],
            '客人': reservation['guest_name'],
            '房间': reservation['room_number'],
            '入住日期': reservation['check_in_date'],
            '退房日期': reservation['check_out_date'],
            '状态': reservation['status']
        })
        
        if not Display.confirm("确认取消此预订?"):
            Display.print_info("已取消操作")
            Display.pause()
            return
        
        # 执行取消
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
        """查看今日入住"""
        Display.clear_screen()
        
        reservations = ReservationService.get_upcoming_checkins(days=1)
        
        if not reservations:
            Display.print_warning("今日没有预计入住")
        else:
            display_data = [{
                '预订ID': res['reservation_id'],
                '客人': res['guest_name'],
                '手机': res['phone'],
                '房间': res['room_number'],
                '房型': res['room_type'],
                '入住日期': res['check_in_date'],
                '退房日期': res['check_out_date']
            } for res in reservations]
            
            Display.print_table(display_data, title="今日预计入住")
        
        Display.pause()
    
    def view_current_checkins(self):
        """查看当前在住"""
        Display.clear_screen()
        
        reservations = ReservationService.get_current_checkins()
        
        if not reservations:
            Display.print_warning("当前没有在住客人")
        else:
            display_data = [{
                '预订ID': res['reservation_id'],
                '客人': res['guest_name'],
                '手机': res['phone'],
                '房间': res['room_number'],
                '房型': res['room_type'],
                '入住日期': res['check_in_date'],
                '退房日期': res['check_out_date']
            } for res in reservations]
            
            Display.print_table(display_data, title="当前在住客人")
        
        Display.pause()
    
    # ==================== 运营管理菜单 ====================
    
    def operation_menu(self):
        """运营管理菜单"""
        while True:
            Display.clear_screen()
            options = [
                "办理入住",
                "办理退房",
                "查看今日入住",
                "查看当前在住"
            ]
            
            Display.print_menu("运营管理", options)
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
        """办理入住"""
        Display.clear_screen()
        Display.print_header("办理入住")
        
        reservation_id = Display.get_input("预订ID", int)
        if not reservation_id:
            return
        
        # 获取预订详情
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            Display.print_error("预订不存在")
            Display.pause()
            return
        
        # 显示预订信息
        Display.print_detail({
            '预订号': reservation['reservation_id'],
            '客人': reservation['guest_name'],
            '手机': reservation['phone'],
            '房间': reservation['room_number'],
            '入住日期': reservation['check_in_date'],
            '退房日期': reservation['check_out_date'],
            '状态': reservation['status']
        })
        
        if not Display.confirm("确认办理入住?"):
            Display.print_info("已取消")
            Display.pause()
            return
        
        # 执行入住
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
        """办理退房"""
        Display.clear_screen()
        Display.print_header("办理退房")
        
        reservation_id = Display.get_input("预订ID", int)
        if not reservation_id:
            return
        
        # 获取预订详情
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            Display.print_error("预订不存在")
            Display.pause()
            return
        
        # 显示预订信息
        Display.print_detail({
            '预订号': reservation['reservation_id'],
            '客人': reservation['guest_name'],
            '房间': reservation['room_number'],
            '入住日期': reservation['check_in_date'],
            '退房日期': reservation['check_out_date'],
            '应付金额': Display.format_currency(reservation['total_price']),
            '状态': reservation['status']
        })
        
        if reservation['status'] != 'CheckedIn':
            Display.print_error(f"预订状态为 {reservation['status']}，无法办理退房")
            Display.pause()
            return
        
        # 获取支付信息
        Display.print_subheader("支付信息")
        Display.print_info("支付方式: 1-现金, 2-信用卡, 3-借记卡, 4-在线转账")
        
        payment_method_map = {
            1: 'Cash',
            2: 'CreditCard',
            3: 'DebitCard',
            4: 'OnlineTransfer'
        }
        
        method_choice = Display.get_input("选择支付方式", int)
        if method_choice not in payment_method_map:
            Display.print_error("无效的支付方式")
            Display.pause()
            return
        
        payment_method = payment_method_map[method_choice]
        payment_amount = Display.get_input(
            "支付金额", 
            float, 
            default=float(reservation['total_price'])
        )
        
        if not Display.confirm(f"确认收款 {Display.format_currency(payment_amount)}?"):
            Display.print_info("已取消")
            Display.pause()
            return
        
        # 执行退房
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
    
    # ==================== 房间管理菜单 ====================
    
    def view_rooms(self):
        """查看房间状态"""
        Display.clear_screen()
        Display.print_header("房间状态")
        
        # 获取统计信息
        stats = RoomService.get_room_statistics()
        Display.print_info(
            f"总房间数: {stats.get('total_rooms', 0)} | "
            f"清洁: {stats.get('clean_rooms', 0)} | "
            f"脏污: {stats.get('dirty_rooms', 0)} | "
            f"已占用: {stats.get('occupied_rooms', 0)} | "
            f"维护中: {stats.get('maintenance_rooms', 0)}"
        )
        
        # 获取所有房间
        rooms = RoomService.list_all_rooms()
        
        display_data = [{
            '房间号': room['room_number'],
            '房型': room['type_name'],
            '楼层': room['floor'],
            '状态': room['status'],
            '最大入住': room['max_occupancy'],
            '基础价格': Display.format_currency(room['base_price'])
        } for room in rooms]
        
        Display.print_table(display_data, title="房间列表")
        Display.pause()
    
    def room_management_menu(self):
        """房间管理菜单（管理员）"""
        while True:
            Display.clear_screen()
            options = [
                "查看所有房间",
                "更新房间状态",
                "添加房间",
                "房型管理"
            ]
            
            Display.print_menu("房间管理", options)
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
        """更新房间状态"""
        Display.clear_screen()
        Display.print_header("更新房间状态")
        
        room_number = Display.get_input("房间号")
        if not room_number:
            return
        
        # 获取房间信息
        room = RoomService.get_room_by_number(room_number)
        if not room:
            Display.print_error("房间不存在")
            Display.pause()
            return
        
        Display.print_info(f"当前状态: {room['status']}")
        Display.print_info("状态选项: 1-Clean, 2-Dirty, 3-Occupied, 4-Maintenance")
        
        status_map = {
            1: 'Clean',
            2: 'Dirty',
            3: 'Occupied',
            4: 'Maintenance'
        }
        
        status_choice = Display.get_input("选择新状态", int)
        if status_choice not in status_map:
            Display.print_error("无效的状态选择")
            Display.pause()
            return
        
        new_status = status_map[status_choice]
        
        if not Display.confirm(f"确认将房间 {room_number} 状态改为 {new_status}?"):
            Display.print_info("已取消")
            Display.pause()
            return
        
        # 更新状态
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
        """添加房间"""
        Display.clear_screen()
        Display.print_header("添加房间")
        
        # 显示房型列表
        room_types = RoomService.get_room_types()
        Display.print_table(
            [{'ID': rt['room_type_id'], '房型': rt['type_name'], 
              '价格': Display.format_currency(rt['base_price'])} 
             for rt in room_types],
            title="可用房型"
        )
        
        room_number = Display.get_input("房间号")
        room_type_id = Display.get_input("房型ID", int)
        floor = Display.get_input("楼层", int)
        
        if not all([room_number, room_type_id, floor]):
            Display.print_error("信息不完整")
            Display.pause()
            return
        
        # 添加房间
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
        """房型管理菜单"""
        while True:
            Display.clear_screen()
            options = [
                "查看所有房型",
                "添加房型",
                "修改房型"
            ]
            
            Display.print_menu("房型管理", options)
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
        """查看所有房型"""
        Display.clear_screen()
        
        room_types = RoomService.get_room_types()
        
        display_data = [{
            'ID': rt['room_type_id'],
            '房型名称': rt['type_name'],
            '基础价格': Display.format_currency(rt['base_price']),
            '最大入住': rt['max_occupancy'],
            '描述': rt['description'][:30] + '...' if len(rt['description']) > 30 else rt['description']
        } for rt in room_types]
        
        Display.print_table(display_data, title="房型列表")
        Display.pause()
    
    def add_room_type(self):
        """添加房型"""
        Display.clear_screen()
        Display.print_header("添加房型")
        
        type_name = Display.get_input("房型名称")
        description = Display.get_input("描述")
        base_price = Display.get_input("基础价格", float)
        max_occupancy = Display.get_input("最大入住人数", int)
        amenities = Display.get_input("设施（用逗号分隔）")
        
        if not all([type_name, description, base_price, max_occupancy, amenities]):
            Display.print_error("信息不完整")
            Display.pause()
            return
        
        # 添加房型
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
        """修改房型"""
        Display.clear_screen()
        Display.print_header("修改房型")
        
        # 显示房型列表
        self.view_room_types()
        
        room_type_id = Display.get_input("房型ID", int)
        if not room_type_id:
            return
        
        # 获取当前房型
        room_type = RoomService.get_room_type_by_id(room_type_id)
        if not room_type:
            Display.print_error("房型不存在")
            Display.pause()
            return
        
        Display.print_info("请输入新值（留空保持不变）:")
        
        new_name = Display.get_input(f"房型名称 (当前: {room_type['type_name']})", allow_empty=True)
        new_desc = Display.get_input(f"描述 (当前: {room_type['description'][:30]}...)", allow_empty=True)
        new_price = Display.get_input(f"基础价格 (当前: {room_type['base_price']})", float, allow_empty=True)
        new_occupancy = Display.get_input(f"最大入住 (当前: {room_type['max_occupancy']})", int, allow_empty=True)
        new_amenities = Display.get_input(f"设施", allow_empty=True)
        
        # 更新房型
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
    
    # ==================== 定价管理菜单 ====================
    
    def pricing_menu(self):
        """定价管理菜单"""
        while True:
            Display.clear_screen()
            options = [
                "查看季节性定价",
                "添加季节性定价",
                "删除季节性定价"
            ]
            
            Display.print_menu("定价配置", options)
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
        """查看季节性定价"""
        Display.clear_screen()
        
        pricing_rules = PricingService.list_seasonal_pricing()
        
        if not pricing_rules:
            Display.print_warning("没有季节性定价规则")
        else:
            display_data = [{
                'ID': pr['pricing_id'],
                '房型': pr['type_name'],
                '季节': pr['season_name'],
                '开始日期': pr['start_date'],
                '结束日期': pr['end_date'],
                '价格乘数': pr['price_multiplier'] or '-',
                '固定价格': Display.format_currency(pr['fixed_price']) if pr['fixed_price'] else '-'
            } for pr in pricing_rules]
            
            Display.print_table(display_data, title="季节性定价规则")
        
        Display.pause()
    
    def add_seasonal_pricing(self):
        """添加季节性定价"""
        Display.clear_screen()
        Display.print_header("添加季节性定价")
        
        # 显示房型列表
        room_types = RoomService.get_room_types()
        Display.print_table(
            [{'ID': rt['room_type_id'], '房型': rt['type_name'], 
              '基础价格': Display.format_currency(rt['base_price'])} 
             for rt in room_types],
            title="房型列表"
        )
        
        room_type_id = Display.get_input("房型ID", int)
        season_name = Display.get_input("季节名称")
        start_date = Display.get_input("开始日期 (YYYY-MM-DD)")
        end_date = Display.get_input("结束日期 (YYYY-MM-DD)")
        
        Display.print_info("定价方式: 1-价格乘数, 2-固定价格")
        pricing_type = Display.get_input("选择定价方式", int)
        
        price_multiplier = None
        fixed_price = None
        
        if pricing_type == 1:
            price_multiplier = Display.get_input("价格乘数 (例如: 1.5表示150%)", float)
        elif pricing_type == 2:
            fixed_price = Display.get_input("固定价格", float)
        else:
            Display.print_error("无效的定价方式")
            Display.pause()
            return
        
        # 添加定价规则
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
        """删除季节性定价"""
        Display.clear_screen()
        Display.print_header("删除季节性定价")
        
        # 显示现有定价规则
        self.view_seasonal_pricing()
        
        pricing_id = Display.get_input("定价规则ID", int)
        if not pricing_id:
            return
        
        if not Display.confirm("确认删除此定价规则?"):
            Display.print_info("已取消")
            Display.pause()
            return
        
        # 删除定价规则
        success, message = PricingService.delete_seasonal_pricing(
            pricing_id,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(message)
        else:
            Display.print_error(message)
        
        Display.pause()
    
    # ==================== 报表管理菜单 ====================
    
    def report_menu(self):
        """报表管理菜单"""
        while True:
            Display.clear_screen()
            options = [
                "入住率报表",
                "收入报表",
                "审计日志查询",
                "数据库备份"
            ]
            
            Display.print_menu("报表管理", options)
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
        """入住率报表"""
        Display.clear_screen()
        Display.print_header("入住率报表")
        
        start_date = Display.get_input("开始日期 (YYYY-MM-DD)")
        end_date = Display.get_input("结束日期 (YYYY-MM-DD)")
        
        if not start_date or not end_date:
            return
        
        # 生成报表
        report = ReportService.generate_occupancy_report(start_date, end_date)
        
        if 'error' in report:
            Display.print_error(report['error'])
            Display.pause()
            return
        
        # 显示摘要
        Display.print_subheader("报表摘要")
        Display.print_detail({
            '报表期间': f"{report['start_date']} 至 {report['end_date']}",
            '总房间数': report['total_rooms'],
            '报表天数': report['days'],
            '平均入住率': Display.format_percentage(report['average_occupancy_rate'])
        })
        
        # 显示每日数据（前10天）
        if report['daily_data']:
            display_data = [{
                '日期': day['date'],
                '总房间': day['total_rooms'],
                '已占用': day['occupied_rooms'],
                '可用': day['available_rooms'],
                '入住率': Display.format_percentage(day['occupancy_rate'])
            } for day in report['daily_data'][:10]]
            
            Display.print_table(display_data, title="每日入住情况（前10天）")
        
        # 询问是否导出
        if Display.confirm("是否导出为CSV文件?"):
            filename = f"occupancy_report_{start_date}_{end_date}.csv"
            success, result = ReportService.export_to_csv(report, filename, 'occupancy')
            
            if success:
                Display.print_success(f"报表已导出: {result}")
            else:
                Display.print_error(result)
        
        Display.pause()
    
    def revenue_report(self):
        """收入报表"""
        Display.clear_screen()
        Display.print_header("收入报表")
        
        start_date = Display.get_input("开始日期 (YYYY-MM-DD)")
        end_date = Display.get_input("结束日期 (YYYY-MM-DD)")
        
        if not start_date or not end_date:
            return
        
        # 生成报表
        report = ReportService.generate_revenue_report(start_date, end_date)
        
        if 'error' in report:
            Display.print_error(report['error'])
            Display.pause()
            return
        
        # 显示摘要
        Display.print_subheader("收入摘要")
        Display.print_detail({
            '报表期间': f"{report['start_date']} 至 {report['end_date']}",
            '总预订数': report['total_reservations'],
            '总收入': Display.format_currency(report['total_revenue']),
            '平均每预订收入': Display.format_currency(report['average_revenue_per_reservation'])
        })
        
        # 按房型统计
        if report['by_room_type']:
            Display.print_table(
                [{
                    '房型': item['room_type'],
                    '预订数': item['reservations'],
                    '收入': Display.format_currency(item['revenue'])
                } for item in report['by_room_type']],
                title="按房型统计"
            )
        
        # 按支付方式统计
        if report['by_payment_method']:
            Display.print_table(
                [{
                    '支付方式': item['payment_method'],
                    '交易数': item['count'],
                    '金额': Display.format_currency(item['amount'])
                } for item in report['by_payment_method']],
                title="按支付方式统计"
            )
        
        # 询问是否导出
        if Display.confirm("是否导出为CSV文件?"):
            filename = f"revenue_report_{start_date}_{end_date}.csv"
            success, result = ReportService.export_to_csv(report, filename, 'revenue')
            
            if success:
                Display.print_success(f"报表已导出: {result}")
            else:
                Display.print_error(result)
        
        Display.pause()
    
    def view_audit_logs(self):
        """查看审计日志"""
        Display.clear_screen()
        Display.print_header("审计日志查询")
        
        Display.print_info("请输入查询条件（留空跳过）:")
        
        operation_type = Display.get_input("操作类型 (CREATE/UPDATE/DELETE等)", allow_empty=True)
        table_name = Display.get_input("表名", allow_empty=True)
        start_date = Display.get_input("开始日期 (YYYY-MM-DD)", allow_empty=True)
        end_date = Display.get_input("结束日期 (YYYY-MM-DD)", allow_empty=True)
        
        # 查询日志
        logs = ReportService.get_audit_logs(
            operation_type=operation_type or None,
            table_name=table_name or None,
            start_date=start_date or None,
            end_date=end_date or None,
            limit=50
        )
        
        if not logs:
            Display.print_warning("没有找到匹配的日志")
        else:
            display_data = [{
                '时间': Display.format_datetime(log['timestamp']),
                '用户': log['username'],
                '操作': log['operation_type'],
                '表': log['table_name'] or '-',
                '记录ID': log['record_id'] or '-',
                '描述': (log['description'][:40] + '...') if log['description'] and len(log['description']) > 40 else log['description']
            } for log in logs]
            
            Display.print_table(display_data, title=f"审计日志（最近{len(logs)}条）")
        
        Display.pause()
    
    def backup_database(self):
        """数据库备份"""
        Display.clear_screen()
        Display.print_header("数据库备份")
        
        backup_name = Display.get_input("备份文件名", default="hrms_backup")
        
        if not Display.confirm("确认执行数据库备份?"):
            Display.print_info("已取消")
            Display.pause()
            return
        
        Display.print_info("正在备份数据库...")
        
        success, result = ReportService.backup_database(
            backup_name,
            self.current_user['user_id']
        )
        
        if success:
            Display.print_success(f"数据库备份成功: {result}")
        else:
            Display.print_error(result)
        
        Display.pause()
    
    # ==================== 系统管理菜单 ====================
    
    def system_menu(self):
        """系统管理菜单"""
        while True:
            Display.clear_screen()
            options = [
                "修改密码",
                "查看备份历史",
                "系统统计"
            ]
            
            Display.print_menu("系统管理", options)
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
        """修改密码"""
        Display.clear_screen()
        Display.print_header("修改密码")
        
        old_password = Display.get_input("当前密码")
        new_password = Display.get_input("新密码")
        confirm_password = Display.get_input("确认新密码")
        
        if not all([old_password, new_password, confirm_password]):
            Display.print_error("信息不完整")
            Display.pause()
            return
        
        if new_password != confirm_password:
            Display.print_error("两次输入的新密码不一致")
            Display.pause()
            return
        
        # 修改密码
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
        """查看备份历史"""
        Display.clear_screen()
        
        backups = ReportService.list_backups()
        
        if not backups:
            Display.print_warning("没有备份记录")
        else:
            display_data = [{
                'ID': backup['backup_id'],
                '文件名': backup['backup_file'].split('/')[-1] if '/' in backup['backup_file'] else backup['backup_file'],
                '大小(KB)': f"{backup['backup_size'] / 1024:.2f}" if backup['backup_size'] else '-',
                '类型': backup['backup_type'],
                '状态': backup['status'],
                '创建者': backup['username'],
                '时间': Display.format_datetime(backup['created_at'])
            } for backup in backups]
            
            Display.print_table(display_data, title="备份历史")
        
        Display.pause()
    
    def system_statistics(self):
        """系统统计"""
        Display.clear_screen()
        Display.print_header("系统统计")
        
        # 房间统计
        room_stats = RoomService.get_room_statistics()
        Display.print_subheader("房间状态统计")
        Display.print_detail({
            '总房间数': room_stats.get('total_rooms', 0),
            '清洁可用': room_stats.get('clean_rooms', 0),
            '脏污待清洁': room_stats.get('dirty_rooms', 0),
            '已占用': room_stats.get('occupied_rooms', 0),
            '维护中': room_stats.get('maintenance_rooms', 0)
        })
        
        # 今日预订统计
        today_checkins = ReservationService.get_upcoming_checkins(days=0)
        current_guests = ReservationService.get_current_checkins()
        
        Display.print_subheader("预订统计")
        Display.print_detail({
            '今日预计入住': len(today_checkins),
            '当前在住客人': len(current_guests)
        })
        
        # 活动会话
        active_sessions = AuthService.get_active_sessions_count()
        Display.print_subheader("系统状态")
        Display.print_detail({
            '活动会话数': active_sessions
        })
        
        Display.pause()
    
    @staticmethod
    def _get_role_name(role: str) -> str:
        """获取角色中文名"""
        role_names = {
            'admin': '管理员',
            'front_desk': '前台员工',
            'housekeeping': '客房员工'
        }
        return role_names.get(role, role)
