"""
显示工具模块
提供CLI界面的格式化输出功能
"""

from typing import List, Dict, Any
from tabulate import tabulate
from colorama import Fore, Style, init

# 初始化colorama（Windows支持）
init(autoreset=True)


class Display:
    """CLI显示工具类"""
    
    @staticmethod
    def print_header(text: str):
        """打印标题"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{text:^70}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_subheader(text: str):
        """打印子标题"""
        print(f"\n{Fore.YELLOW}{'-'*70}")
        print(f"{text}")
        print(f"{'-'*70}{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_success(message: str):
        """打印成功消息"""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_error(message: str):
        """打印错误消息"""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_info(message: str):
        """打印信息消息"""
        print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_warning(message: str):
        """打印警告消息"""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_table(data: List[Dict[str, Any]], headers: List[str] = None,
                   title: str = None, tablefmt: str = 'grid'):
        """
        打印表格
        
        Args:
            data: 数据列表
            headers: 表头列表（如果为None，使用字典的键）
            title: 表格标题
            tablefmt: 表格格式
        """
        if not data:
            Display.print_warning("没有数据可显示")
            return
        
        if title:
            Display.print_subheader(title)
        
        # 如果没有指定headers，使用第一行数据的键
        if headers is None and data:
            headers = list(data[0].keys())
        
        # 提取表格数据
        table_data = []
        for row in data:
            if isinstance(row, dict):
                table_data.append([row.get(h, '') for h in headers])
            else:
                table_data.append(row)
        
        print(tabulate(table_data, headers=headers, tablefmt=tablefmt))
        print()
    
    @staticmethod
    def print_detail(data: Dict[str, Any], title: str = None):
        """
        打印详细信息（键值对形式）
        
        Args:
            data: 数据字典
            title: 标题
        """
        if title:
            Display.print_subheader(title)
        
        max_key_length = max(len(str(k)) for k in data.keys()) if data else 0
        
        for key, value in data.items():
            key_str = str(key).replace('_', ' ').title()
            print(f"{Fore.CYAN}{key_str:<{max_key_length + 2}}{Style.RESET_ALL}: {value}")
        print()
    
    @staticmethod
    def print_menu(title: str, options: List[str], show_back: bool = True):
        """
        打印菜单
        
        Args:
            title: 菜单标题
            options: 选项列表
            show_back: 是否显示返回选项
        """
        Display.print_header(title)
        
        for i, option in enumerate(options, 1):
            print(f"{Fore.CYAN}[{i}]{Style.RESET_ALL} {option}")
        
        if show_back:
            print(f"{Fore.CYAN}[0]{Style.RESET_ALL} 返回上级菜单")
        else:
            print(f"{Fore.CYAN}[0]{Style.RESET_ALL} 退出系统")
        
        print()
    
    @staticmethod
    def get_input(prompt: str, input_type: type = str, 
                 default: Any = None, allow_empty: bool = False):
        """
        获取用户输入
        
        Args:
            prompt: 提示信息
            input_type: 输入类型（str, int, float等）
            default: 默认值
            allow_empty: 是否允许空输入
            
        Returns:
            用户输入的值
        """
        while True:
            try:
                default_text = f" (默认: {default})" if default is not None else ""
                user_input = input(f"{Fore.GREEN}>{Style.RESET_ALL} {prompt}{default_text}: ").strip()
                
                # 如果有默认值且用户输入为空，返回默认值
                if not user_input and default is not None:
                    return default
                
                # 如果允许空输入且用户输入为空
                if not user_input and allow_empty:
                    return None if input_type == str else user_input
                
                # 如果不允许空输入且用户输入为空
                if not user_input:
                    Display.print_error("输入不能为空，请重新输入")
                    continue
                
                # 类型转换
                if input_type == bool:
                    return user_input.lower() in ['y', 'yes', '是', 'true', '1']
                elif input_type == str:
                    return user_input
                else:
                    return input_type(user_input)
                    
            except ValueError:
                Display.print_error(f"输入格式错误，请输入{input_type.__name__}类型的值")
            except KeyboardInterrupt:
                print()
                Display.print_warning("操作已取消")
                return None
    
    @staticmethod
    def get_choice(max_choice: int, min_choice: int = 0) -> int:
        """
        获取菜单选择
        
        Args:
            max_choice: 最大选项数
            min_choice: 最小选项数（通常为0，表示返回）
            
        Returns:
            用户选择的选项号
        """
        while True:
            try:
                choice = int(input(f"{Fore.GREEN}>{Style.RESET_ALL} 请选择 ({min_choice}-{max_choice}): "))
                if min_choice <= choice <= max_choice:
                    return choice
                else:
                    Display.print_error(f"请输入 {min_choice} 到 {max_choice} 之间的数字")
            except ValueError:
                Display.print_error("请输入有效的数字")
            except KeyboardInterrupt:
                print()
                return 0  # 返回上级
    
    @staticmethod
    def confirm(message: str, default: bool = False) -> bool:
        """
        确认对话框
        
        Args:
            message: 确认消息
            default: 默认值
            
        Returns:
            用户确认结果
        """
        default_text = "(Y/n)" if default else "(y/N)"
        user_input = input(f"{Fore.YELLOW}?{Style.RESET_ALL} {message} {default_text}: ").strip().lower()
        
        if not user_input:
            return default
        
        return user_input in ['y', 'yes', '是']
    
    @staticmethod
    def pause():
        """暂停，等待用户按键继续"""
        input(f"\n{Fore.CYAN}按回车键继续...{Style.RESET_ALL}")
    
    @staticmethod
    def clear_screen():
        """清屏"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_separator(char: str = '-', length: int = 70):
        """打印分隔线"""
        print(char * length)
    
    @staticmethod
    def print_logo():
        """打印系统Logo"""
        logo = f"""{Fore.CYAN}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           酒店预订管理系统 (HRMS) - CLI 版本                     ║
║           Hotel Reservation Management System                     ║
║                                                                   ║
║                          Version 1.0                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
        print(logo)
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """格式化货币"""
        return f"¥{amount:,.2f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """格式化百分比"""
        return f"{value:.2f}%"
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """格式化日期显示"""
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y年%m月%d日')
        except:
            return date_str
    
    @staticmethod
    def format_datetime(datetime_str: str) -> str:
        """格式化日期时间显示"""
        try:
            from datetime import datetime
            # 尝试多种格式
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                try:
                    dt_obj = datetime.strptime(datetime_str, fmt)
                    return dt_obj.strftime('%Y年%m月%d日 %H:%M:%S')
                except:
                    continue
            return datetime_str
        except:
            return datetime_str
    
    @staticmethod
    def print_box(content: str, width: int = 70):
        """打印带边框的内容"""
        lines = content.split('\n')
        print(f"{Fore.CYAN}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
        for line in lines:
            padding = width - len(line) - 4
            print(f"{Fore.CYAN}│{Style.RESET_ALL} {line}{' ' * padding} {Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}└{'─' * (width - 2)}┘{Style.RESET_ALL}")
