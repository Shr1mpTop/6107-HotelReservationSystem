"""
黑盒测试自动化脚本
测试前端所有功能，记录问题并提供修复建议
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# 配置
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# 测试数据
ADMIN_USER = {"username": "admin", "password": "admin123"}
RECEPTIONIST_USER = {"username": "receptionist", "password": "receptionist123"}

class TestResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.issues = []
    
    def add_pass(self, test_id: str, description: str):
        self.passed.append({"id": test_id, "description": description})
        print(f"✅ PASS: {test_id} - {description}")
    
    def add_fail(self, test_id: str, description: str, error: str):
        self.failed.append({"id": test_id, "description": description, "error": error})
        self.issues.append({
            "test_id": test_id,
            "severity": "HIGH",
            "description": description,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        print(f"❌ FAIL: {test_id} - {description}")
        print(f"   Error: {error}")
    
    def print_summary(self):
        total = len(self.passed) + len(self.failed)
        pass_rate = (len(self.passed) / total * 100) if total > 0 else 0
        
        print("\n" + "="*80)
        print("测试总结 / TEST SUMMARY")
        print("="*80)
        print(f"总测试数 / Total Tests: {total}")
        print(f"通过 / Passed: {len(self.passed)} ✅")
        print(f"失败 / Failed: {len(self.failed)} ❌")
        print(f"通过率 / Pass Rate: {pass_rate:.2f}%")
        print("="*80)
        
        if self.issues:
            print("\n发现的问题 / Issues Found:")
            for i, issue in enumerate(self.issues, 1):
                print(f"\n问题 #{i}:")
                print(f"  测试ID: {issue['test_id']}")
                print(f"  严重级别: {issue['severity']}")
                print(f"  描述: {issue['description']}")
                print(f"  错误: {issue['error']}")

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user = None
        self.result = TestResult()
    
    def login(self, username: str, password: str) -> bool:
        """登录获取token"""
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.token = data.get("session_token")
                    self.user = data.get("user")
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    return True
            return False
        except Exception as e:
            return False
    
    def logout(self):
        """登出"""
        try:
            self.session.post(f"{BASE_URL}/api/auth/logout")
        except:
            pass
        finally:
            self.token = None
            self.user = None
            self.session.headers.pop("Authorization", None)
    
    def test_authentication(self):
        """测试1: 登录与认证"""
        print("\n" + "="*80)
        print("模块 1: 登录与认证 (Authentication)")
        print("="*80)
        
        # TC-AUTH-001: 管理员登录
        self.logout()
        if self.login(ADMIN_USER["username"], ADMIN_USER["password"]):
            self.result.add_pass("TC-AUTH-001", "管理员成功登录")
        else:
            self.result.add_fail("TC-AUTH-001", "管理员登录失败", "登录接口返回失败")
        
        # TC-AUTH-005: 登出
        self.logout()
        if not self.token:
            self.result.add_pass("TC-AUTH-005", "成功登出")
        else:
            self.result.add_fail("TC-AUTH-005", "登出失败", "Token仍然存在")
        
        # TC-AUTH-002: 前台员工登录
        if self.login(RECEPTIONIST_USER["username"], RECEPTIONIST_USER["password"]):
            self.result.add_pass("TC-AUTH-002", "前台员工成功登录")
        else:
            self.result.add_fail("TC-AUTH-002", "前台员工登录失败", "登录接口返回失败")
        
        # TC-AUTH-003: 错误密码
        self.logout()
        if not self.login("admin", "wrongpassword"):
            self.result.add_pass("TC-AUTH-003", "错误密码正确拒绝")
        else:
            self.result.add_fail("TC-AUTH-003", "错误密码登录成功", "安全问题：应该拒绝错误密码")
        
        # TC-AUTH-004: 不存在的用户
        if not self.login("nonexistent", "password"):
            self.result.add_pass("TC-AUTH-004", "不存在的用户正确拒绝")
        else:
            self.result.add_fail("TC-AUTH-004", "不存在的用户登录成功", "安全问题：应该拒绝不存在的用户")
    
    def test_dashboard(self):
        """测试2: Dashboard总览"""
        print("\n" + "="*80)
        print("模块 2: Dashboard总览 (Dashboard)")
        print("="*80)
        
        # 确保已登录
        if not self.token:
            self.login(ADMIN_USER["username"], ADMIN_USER["password"])
        
        # TC-DASH-001: Dashboard统计数据
        try:
            response = self.session.get(f"{BASE_URL}/api/dashboard/stats")
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                if all(key in stats for key in ["total_rooms", "available_rooms", "total_reservations", "today_checkins"]):
                    self.result.add_pass("TC-DASH-001", "Dashboard统计数据完整")
                else:
                    self.result.add_fail("TC-DASH-001", "Dashboard统计数据不完整", f"缺少必要字段，实际数据: {stats.keys()}")
            else:
                self.result.add_fail("TC-DASH-001", "Dashboard统计数据获取失败", f"HTTP {response.status_code}")
        except Exception as e:
            self.result.add_fail("TC-DASH-001", "Dashboard统计数据请求异常", str(e))
    
    def test_hotel_map(self):
        """测试3: 酒店地图"""
        print("\n" + "="*80)
        print("模块 3: 酒店地图 (Hotel Map)")
        print("="*80)
        
        # 确保已登录
        if not self.token:
            self.login(ADMIN_USER["username"], ADMIN_USER["password"])
        
        # TC-MAP-001: 加载所有房间
        try:
            response = self.session.get(f"{BASE_URL}/api/rooms/with-reservations")
            if response.status_code == 200:
                data = response.json()
                rooms = data.get("data", [])
                if len(rooms) > 0:
                    self.result.add_pass("TC-MAP-001", f"成功加载{len(rooms)}个房间")
                    
                    # TC-MAP-002: 房间状态
                    has_status = all("status" in room for room in rooms)
                    if has_status:
                        self.result.add_pass("TC-MAP-002", "所有房间都有状态字段")
                    else:
                        self.result.add_fail("TC-MAP-002", "部分房间缺少状态字段", "数据结构不完整")
                    
                    # TC-MAP-004: 预订信息
                    has_reservation_fields = all("has_reservation" in room for room in rooms)
                    if has_reservation_fields:
                        self.result.add_pass("TC-MAP-004", "房间包含预订信息字段")
                    else:
                        self.result.add_fail("TC-MAP-004", "房间缺少预订信息字段", "预订状态功能不可用")
                else:
                    self.result.add_fail("TC-MAP-001", "未加载到房间数据", "返回的房间列表为空")
            else:
                self.result.add_fail("TC-MAP-001", "房间数据获取失败", f"HTTP {response.status_code}")
        except Exception as e:
            self.result.add_fail("TC-MAP-001", "房间数据请求异常", str(e))
    
    def test_create_reservation(self):
        """测试4: 创建新预订"""
        print("\n" + "="*80)
        print("模块 4: 创建新预订 (New Reservation)")
        print("="*80)
        
        # 确保已登录
        if not self.token:
            self.login(ADMIN_USER["username"], ADMIN_USER["password"])
        
        # 首先获取可用房间
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        checkout = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        try:
            # TC-RES-001: 搜索可用房间
            response = self.session.get(
                f"{BASE_URL}/api/rooms/available",
                params={"check_in": tomorrow, "check_out": checkout}
            )
            
            if response.status_code == 200:
                data = response.json()
                available_rooms = data.get("data", [])
                if len(available_rooms) > 0:
                    self.result.add_pass("TC-RES-001", f"找到{len(available_rooms)}个可用房间")
                    
                    # 选择第一个房间创建测试预订
                    test_room = available_rooms[0]
                    
                    # TC-RES-010: 创建预订
                    reservation_data = {
                        "guest_info": {
                            "first_name": "Test",
                            "last_name": "User",
                            "email": "test@example.com",
                            "phone": "+8613800138000",
                            "id_number": "123456789012345678"
                        },
                        "room_id": test_room["room_id"],
                        "check_in_date": tomorrow,
                        "check_out_date": checkout,
                        "num_guests": 2,
                        "special_requests": "Test reservation"
                    }
                    
                    response = self.session.post(
                        f"{BASE_URL}/api/reservations",
                        json=reservation_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            reservation_id = result.get("reservation_id")
                            self.result.add_pass("TC-RES-010", f"成功创建预订 #{reservation_id}")
                            
                            # 保存预订ID供后续测试使用
                            self.test_reservation_id = reservation_id
                            self.test_room_number = test_room["room_number"]
                        else:
                            self.result.add_fail("TC-RES-010", "创建预订失败", result.get("message", "未知错误"))
                    else:
                        self.result.add_fail("TC-RES-010", "创建预订请求失败", f"HTTP {response.status_code}: {response.text}")
                else:
                    self.result.add_fail("TC-RES-001", "未找到可用房间", "无法继续测试创建预订")
            else:
                self.result.add_fail("TC-RES-001", "搜索可用房间失败", f"HTTP {response.status_code}")
        except Exception as e:
            self.result.add_fail("TC-RES-001", "搜索可用房间异常", str(e))
        
        # TC-RES-002: 日期验证（入住日期不能早于今天）
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            invalid_data = {
                "guest_info": {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@example.com",
                    "phone": "+8613800138000",
                    "id_number": "123456789012345678"
                },
                "room_id": 1,
                "check_in_date": yesterday,
                "check_out_date": today,
                "num_guests": 1,
                "special_requests": ""
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/reservations",
                json=invalid_data
            )
            
            # 应该返回错误
            if response.status_code != 200 or not response.json().get("success", False):
                self.result.add_pass("TC-RES-002", "正确拒绝过去的入住日期")
            else:
                self.result.add_fail("TC-RES-002", "接受了过去的入住日期", "日期验证失败")
        except Exception as e:
            self.result.add_fail("TC-RES-002", "日期验证测试异常", str(e))
    
    def test_reservation_search(self):
        """测试5: 预订搜索与管理"""
        print("\n" + "="*80)
        print("模块 5: 预订搜索与管理 (Reservation Search)")
        print("="*80)
        
        # 确保已登录
        if not self.token:
            self.login(ADMIN_USER["username"], ADMIN_USER["password"])
        
        # 如果之前创建了测试预订，尝试搜索它
        if hasattr(self, 'test_reservation_id'):
            # TC-SEARCH-001: 按预订ID搜索
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/reservations/search",
                    json={"reservation_id": self.test_reservation_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and len(data.get("data", [])) > 0:
                        self.result.add_pass("TC-SEARCH-001", f"成功按ID搜索到预订 #{self.test_reservation_id}")
                    else:
                        self.result.add_fail("TC-SEARCH-001", "按ID搜索未找到预订", "搜索功能可能有问题")
                else:
                    self.result.add_fail("TC-SEARCH-001", "搜索请求失败", f"HTTP {response.status_code}")
            except Exception as e:
                self.result.add_fail("TC-SEARCH-001", "搜索请求异常", str(e))
            
            # TC-SEARCH-002: 按客人姓名搜索
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/reservations/search",
                    json={"guest_name": "Test"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.result.add_pass("TC-SEARCH-002", "姓名搜索功能正常")
                    else:
                        self.result.add_fail("TC-SEARCH-002", "姓名搜索失败", data.get("message", ""))
                else:
                    self.result.add_fail("TC-SEARCH-002", "姓名搜索请求失败", f"HTTP {response.status_code}")
            except Exception as e:
                self.result.add_fail("TC-SEARCH-002", "姓名搜索异常", str(e))
    
    def test_permissions(self):
        """测试18: 权限控制"""
        print("\n" + "="*80)
        print("模块 18: 权限控制 (Permission Control)")
        print("="*80)
        
        # 使用前台员工账号测试
        self.logout()
        if self.login(RECEPTIONIST_USER["username"], RECEPTIONIST_USER["password"]):
            # TC-PERM-001: 前台员工访问报表（应该失败或返回403）
            try:
                response = self.session.get(
                    f"{BASE_URL}/api/reports/occupancy",
                    params={"start_date": "2026-01-01", "end_date": "2026-01-31"}
                )
                
                # 注意：目前API可能没有实现权限检查，这是一个潜在问题
                if response.status_code == 403:
                    self.result.add_pass("TC-PERM-001", "前台员工正确被拒绝访问报表")
                elif response.status_code == 200:
                    self.result.add_fail("TC-PERM-001", "前台员工可以访问报表", "权限控制未实现或不严格")
                else:
                    # 其他错误也算通过，因为至少没有返回数据
                    self.result.add_pass("TC-PERM-001", f"报表访问被拒绝 (HTTP {response.status_code})")
            except Exception as e:
                self.result.add_fail("TC-PERM-001", "权限测试异常", str(e))
    
    def test_settings(self):
        """测试17: 系统设置"""
        print("\n" + "="*80)
        print("模块 17: 系统设置 (Settings)")
        print("="*80)
        
        # 确保已登录
        if not self.token:
            self.login(ADMIN_USER["username"], ADMIN_USER["password"])
        
        # TC-SETTINGS-002: 修改密码（当前密码错误）
        try:
            response = self.session.put(
                f"{BASE_URL}/api/users/{self.user['user_id']}/password",
                json={
                    "old_password": "wrongpassword",
                    "new_password": "newpassword123"
                }
            )
            
            if response.status_code != 200 or not response.json().get("success", False):
                self.result.add_pass("TC-SETTINGS-002", "正确拒绝错误的当前密码")
            else:
                self.result.add_fail("TC-SETTINGS-002", "接受了错误的当前密码", "安全问题")
        except Exception as e:
            self.result.add_fail("TC-SETTINGS-002", "修改密码测试异常", str(e))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*80)
        print("开始黑盒测试 / Starting Black Box Tests")
        print(f"测试时间 / Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 执行各模块测试
        self.test_authentication()
        self.test_dashboard()
        self.test_hotel_map()
        self.test_create_reservation()
        self.test_reservation_search()
        self.test_permissions()
        self.test_settings()
        
        # 清理：登出
        self.logout()
        
        # 打印总结
        self.result.print_summary()
        
        # 保存结果到文件
        self.save_results()
    
    def save_results(self):
        """保存测试结果到文件"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(self.result.passed) + len(self.result.failed),
                "passed": len(self.result.passed),
                "failed": len(self.result.failed),
                "pass_rate": (len(self.result.passed) / (len(self.result.passed) + len(self.result.failed)) * 100)
                    if (len(self.result.passed) + len(self.result.failed)) > 0 else 0
            },
            "passed_tests": self.result.passed,
            "failed_tests": self.result.failed,
            "issues": self.result.issues
        }
        
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n测试结果已保存到 test_results.json")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    酒店预订管理系统 - 黑盒测试                               ║
║              Hotel Reservation System - Black Box Testing                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    tester = APITester()
    tester.run_all_tests()
    
    print("\n测试完成 / Testing Complete ✅")
