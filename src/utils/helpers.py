"""Helper functions module"""

from datetime import datetime, timedelta
from typing import List, Dict, Any


def calculate_nights(check_in: str, check_out: str) -> int:
    """
    Calculate number of nights for stay
    
    Args:
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        
    Returns:
        Number of nights
    """
    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
        delta = check_out_date - check_in_date
        return delta.days
    except ValueError:
        return 0


def get_date_range(start_date: str, end_date: str) -> List[str]:
    """
    获取日期范围内的所有日期
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        
    Returns:
        日期列表
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        date_list = []
        current = start
        while current < end:
            date_list.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return date_list
    except ValueError:
        return []


def format_price(amount: float) -> str:
    """
    格式化价格
    
    Args:
        amount: 金额
        
    Returns:
        格式化后的字符串
    """
    return f"¥{amount:,.2f}"


def truncate_string(text: str, length: int = 50, suffix: str = '...') -> str:
    """
    截断字符串
    
    Args:
        text: 文本
        length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的字符串
    """
    if not text:
        return ""
    
    if len(text) <= length:
        return text
    
    return text[:length - len(suffix)] + suffix


def dict_diff(old_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> Dict[str, tuple]:
    """
    比较两个字典的差异
    
    Args:
        old_dict: 旧字典
        new_dict: 新字典
        
    Returns:
        差异字典 {key: (old_value, new_value)}
    """
    diff = {}
    
    all_keys = set(old_dict.keys()) | set(new_dict.keys())
    
    for key in all_keys:
        old_value = old_dict.get(key)
        new_value = new_dict.get(key)
        
        if old_value != new_value:
            diff[key] = (old_value, new_value)
    
    return diff


def get_current_timestamp() -> str:
    """
    获取当前时间戳字符串
    
    Returns:
        时间戳字符串 (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def is_past_date(date_str: str) -> bool:
    """
    检查日期是否已过
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        
    Returns:
        是否已过
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return date < today
    except ValueError:
        return False


def is_future_date(date_str: str) -> bool:
    """
    检查日期是否在未来
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        
    Returns:
        是否在未来
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return date > today
    except ValueError:
        return False
