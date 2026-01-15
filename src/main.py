"""
酒店预订管理系统 - 主程序入口
Hotel Reservation Management System - Main Entry Point
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.menu import HRMSMenu
from ui.display import Display


def main():
    """主程序入口"""
    try:
        # 创建并启动菜单系统
        menu = HRMSMenu()
        menu.start()
        
    except KeyboardInterrupt:
        print("\n")
        Display.print_warning("系统被用户中断")
    except Exception as e:
        Display.print_error(f"系统错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n感谢使用酒店预订管理系统!")
        print("再见!\n")


if __name__ == '__main__':
    main()
