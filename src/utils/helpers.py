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
    Get all dates within a date range
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        List of dates
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
    Format price
    
    Args:
        amount: Amount
        
    Returns:
        Formatted string
    """
    return f"¥{amount:,.2f}"


def truncate_string(text: str, length: int = 50, suffix: str = '...') -> str:
    """
    Truncate string
    
    Args:
        text: Text
        length: Maximum length
        suffix: Suffix
        
    Returns:
        Truncated string
    """
    if not text:
        return ""
    
    if len(text) <= length:
        return text
    
    return text[:length - len(suffix)] + suffix


def dict_diff(old_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> Dict[str, tuple]:
    """
    Compare differences between two dictionaries
    
    Args:
        old_dict: Old dictionary
        new_dict: New dictionary
        
    Returns:
        Difference dictionary {key: (old_value, new_value)}
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
    Get current timestamp string
    
    Returns:
        Timestamp string (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def is_past_date(date_str: str) -> bool:
    """
    Check if date is in the past
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        
    Returns:
        Whether date is in the past
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return date < today
    except ValueError:
        return False


def is_future_date(date_str: str) -> bool:
    """
    Check if date is in the future
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        
    Returns:
        Whether date is in the future
    """
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return date > today
    except ValueError:
        return False
