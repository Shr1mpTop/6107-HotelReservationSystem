"""工具函数模块 - 输入验证"""

import re
from datetime import datetime


def validate_date(date_str: str) -> bool:
    """
    验证日期格式
    
    Args:
        date_str: 日期字符串 (YYYY-MM-DD)
        
    Returns:
        是否有效
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_phone(phone: str) -> bool:
    """
    验证手机号格式
    
    Args:
        phone: 手机号
        
    Returns:
        是否有效
    """
    # 简单验证：11位数字
    pattern = r'^\d{11}$'
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_id_number(id_number: str) -> bool:
    """
    验证身份证号格式
    
    Args:
        id_number: 身份证号
        
    Returns:
        是否有效
    """
    # 简单验证：15或18位
    pattern = r'^\d{15}$|^\d{17}[\dXx]$'
    return bool(re.match(pattern, id_number))


def sanitize_input(text: str) -> str:
    """
    清理用户输入
    
    Args:
        text: 输入文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    return text.strip()
