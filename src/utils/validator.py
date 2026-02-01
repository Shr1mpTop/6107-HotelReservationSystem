"""Utility functions module - Input validation"""

import re
from datetime import datetime


def validate_date(date_str: str) -> bool:
    """
    Validate date format
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        
    Returns:
        Whether valid
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number
        
    Returns:
        Whether valid
    """
    # 简单验证：11位数字
    pattern = r'^\d{11}$'
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address
        
    Returns:
        Whether valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_id_number(id_number: str) -> bool:
    """
    Validate ID number format
    
    Args:
        id_number: ID number
        
    Returns:
        Whether valid
    """
    # 简单验证：15或18位
    pattern = r'^\d{15}$|^\d{17}[\dXx]$'
    return bool(re.match(pattern, id_number))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    return text.strip()
