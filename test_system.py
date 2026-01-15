"""
系统测试脚本
用于验证系统各模块是否正常工作
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.db_manager import db_manager
from services.auth_service import AuthService
from services.room_service import RoomService
from services.pricing_service import PricingService
from services.reservation_service import ReservationService


def test_database():
    """测试数据库连接"""
    print("测试数据库连接...")
    try:
        # 检查表是否存在
        tables = ['users', 'rooms', 'room_types', 'reservations', 'guests']
        for table in tables:
            assert db_manager.table_exists(table), f"表 {table} 不存在"
        print("✓ 数据库连接正常")
        return True
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        return False


def test_authentication():
    """测试认证系统"""
    print("\n测试认证系统...")
    try:
        # 测试登录
        result = AuthService.login('admin', 'admin123')
        assert result is not None, "登录失败"
        
        session_token = result['session_token']
        assert session_token is not None, "会话令牌为空"
        
        # 测试会话验证
        session = AuthService.validate_session(session_token)
        assert session is not None, "会话验证失败"
        assert session['username'] == 'admin', "用户名不匹配"
        
        # 测试权限检查
        assert AuthService.is_admin(session_token), "管理员权限检查失败"
        
        # 测试登出
        assert AuthService.logout(session_token), "登出失败"
        
        print("✓ 认证系统正常")
        return True
    except Exception as e:
        print(f"✗ 认证测试失败: {e}")
        return False


def test_room_service():
    """测试房间服务"""
    print("\n测试房间服务...")
    try:
        # 测试获取房型
        room_types = RoomService.get_room_types()
        assert len(room_types) > 0, "没有房型数据"
        
        # 测试获取所有房间
        rooms = RoomService.list_all_rooms()
        assert len(rooms) > 0, "没有房间数据"
        
        # 测试查询可用房间
        available = RoomService.get_available_rooms('2026-02-01', '2026-02-05')
        assert isinstance(available, list), "可用房间查询失败"
        
        # 测试房间统计
        stats = RoomService.get_room_statistics()
        assert 'total_rooms' in stats, "房间统计失败"
        
        print(f"✓ 房间服务正常 (共{stats['total_rooms']}个房间)")
        return True
    except Exception as e:
        print(f"✗ 房间服务测试失败: {e}")
        return False


def test_pricing_service():
    """测试定价服务"""
    print("\n测试定价服务...")
    try:
        # 测试获取基础价格
        price = PricingService.get_room_base_price(1)
        assert price is not None and price > 0, "基础价格获取失败"
        
        # 测试价格计算
        pricing_info = PricingService.calculate_total_price(
            1, '2026-02-01', '2026-02-05'
        )
        assert 'total' in pricing_info, "价格计算失败"
        assert pricing_info['total'] > 0, "总价为0"
        assert pricing_info['nights'] == 4, "天数计算错误"
        
        # 测试季节性定价列表
        seasonal = PricingService.list_seasonal_pricing()
        assert isinstance(seasonal, list), "季节性定价查询失败"
        
        print(f"✓ 定价服务正常 (4晚总价: ¥{pricing_info['total']:.2f})")
        return True
    except Exception as e:
        print(f"✗ 定价服务测试失败: {e}")
        return False


def test_reservation_service():
    """测试预订服务"""
    print("\n测试预订服务...")
    try:
        # 登录获取用户ID
        login_result = AuthService.login('admin', 'admin123')
        user_id = login_result['user']['user_id']
        
        # 测试创建预订
        guest_info = {
            'first_name': '测试',
            'last_name': '用户',
            'phone': '13800138000',
            'email': 'test@example.com'
        }
        
        success, message, reservation_id = ReservationService.create_reservation(
            guest_info, 1, '2026-03-01', '2026-03-05', 1, '测试预订', user_id
        )
        
        if not success:
            # 可能是房间冲突，尝试其他房间
            available = RoomService.get_available_rooms('2026-03-01', '2026-03-05')
            if available:
                success, message, reservation_id = ReservationService.create_reservation(
                    guest_info, available[0]['room_id'], 
                    '2026-03-01', '2026-03-05', 1, '测试预订', user_id
                )
        
        assert success, f"创建预订失败: {message}"
        assert reservation_id is not None, "预订ID为空"
        
        # 测试查询预订
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        assert reservation is not None, "查询预订失败"
        assert reservation['reservation_id'] == reservation_id, "预订ID不匹配"
        
        # 测试取消预订
        success, message = ReservationService.cancel_reservation(reservation_id, user_id)
        assert success, f"取消预订失败: {message}"
        
        # 登出
        AuthService.logout(login_result['session_token'])
        
        # 注意：不删除测试数据，保留作为示例
        
        print(f"✓ 预订服务正常 (测试预订ID: {reservation_id})")
        return True
    except Exception as e:
        print(f"✗ 预订服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("酒店预订管理系统 - 系统测试")
    print("="*60)
    
    results = []
    
    # 运行各模块测试
    results.append(("数据库", test_database()))
    results.append(("认证系统", test_authentication()))
    results.append(("房间服务", test_room_service()))
    results.append(("定价服务", test_pricing_service()))
    results.append(("预订服务", test_reservation_service()))
    
    # 输出测试结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for module, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{module:<15}: {status}")
    
    # 统计
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "="*60)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("✓ 所有测试通过！系统运行正常。")
        print("="*60)
        return True
    else:
        print("✗ 部分测试失败，请检查错误信息。")
        print("="*60)
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
