"""
Display Utility Module
Provides formatted output functionality for CLI interface
"""

from typing import List, Dict, Any
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama (Windows support)
init(autoreset=True)


class Display:
    """CLI Display Utility Class"""

    @staticmethod
    def print_header(text: str):
        """Print header"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{text:^70}")
        print(f"{'='*70}{Style.RESET_ALL}\n")

    @staticmethod
    def print_subheader(text: str):
        """Print subheader"""
        print(f"\n{Fore.YELLOW}{'-'*70}")
        print(f"{text}")
        print(f"{'-'*70}{Style.RESET_ALL}\n")

    @staticmethod
    def print_success(message: str):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

    @staticmethod
    def print_error(message: str):
        """Print error message"""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

    @staticmethod
    def print_info(message: str):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

    @staticmethod
    def print_warning(message: str):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def print_table(data: List[Dict[str, Any]], headers: List[str] = None,
                   title: str = None, tablefmt: str = 'grid'):
        """
        Print table
        
        Args:
            data: Data list
            headers: Header list (if None, use dictionary keys)
            title: Table title
            tablefmt: Table format
        """
        if not data:
            Display.print_warning("No data to display")
            return
        
        if title:
            Display.print_subheader(title)
        
        # If no headers specified, use keys from first row of data
        if headers is None and data:
            headers = list(data[0].keys())
        
        # Extract table data
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
        Print detailed information (key-value pairs)
        
        Args:
            data: Data dictionary
            title: Title
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
        Print menu
        
        Args:
            title: Menu title
            options: Options list
            show_back: Whether to show back option
        """
        Display.print_header(title)
        
        for i, option in enumerate(options, 1):
            print(f"{Fore.CYAN}[{i}]{Style.RESET_ALL} {option}")
        
        if show_back:
            print(f"{Fore.CYAN}[0]{Style.RESET_ALL} Return to previous menu")
        else:
            print(f"{Fore.CYAN}[0]{Style.RESET_ALL} Exit system")
        
        print()
    
    @staticmethod
    def get_input(prompt: str, input_type: type = str, 
                 default: Any = None, allow_empty: bool = False):
        """
        Get user input
        
        Args:
            prompt: Prompt message
            input_type: Input type (str, int, float, etc.)
            default: Default value
            allow_empty: Whether to allow empty input
            
        Returns:
            User input value
        """
        while True:
            try:
                default_text = f" (default: {default})" if default is not None else ""
                user_input = input(f"{Fore.GREEN}>{Style.RESET_ALL} {prompt}{default_text}: ").strip()
                
                # If default value exists and user input is empty, return default
                if not user_input and default is not None:
                    return default
                
                # If empty input is allowed and user input is empty
                if not user_input and allow_empty:
                    return None if input_type == str else user_input
                
                # If empty input is not allowed and user input is empty
                if not user_input:
                    Display.print_error("Input cannot be empty, please try again")
                    continue
                
                # Type conversion
                if input_type == bool:
                    return user_input.lower() in ['y', 'yes', 'true', '1']
                elif input_type == str:
                    return user_input
                else:
                    return input_type(user_input)
                    
            except ValueError:
                Display.print_error(f"Input format error, please enter a value of type {input_type.__name__}")
            except KeyboardInterrupt:
                print()
                Display.print_warning("Operation cancelled")
                return None
    
    @staticmethod
    def get_choice(max_choice: int, min_choice: int = 0) -> int:
        """
        Get menu choice
        
        Args:
            max_choice: Maximum choice number
            min_choice: Minimum choice number (usually 0 for back)
            
        Returns:
            User's selected choice number
        """
        while True:
            try:
                choice = int(input(f"{Fore.GREEN}>{Style.RESET_ALL} Please select ({min_choice}-{max_choice}): "))
                if min_choice <= choice <= max_choice:
                    return choice
                else:
                    Display.print_error(f"Please enter a number between {min_choice} and {max_choice}")
            except ValueError:
                Display.print_error("Please enter a valid number")
            except KeyboardInterrupt:
                print()
                return 0  # Return to previous level
    
    @staticmethod
    def confirm(message: str, default: bool = False) -> bool:
        """
        Confirmation dialog
        
        Args:
            message: Confirmation message
            default: Default value
            
        Returns:
            User confirmation result
        """
        default_text = "(Y/n)" if default else "(y/N)"
        user_input = input(f"{Fore.YELLOW}?{Style.RESET_ALL} {message} {default_text}: ").strip().lower()
        
        if not user_input:
            return default
        
        return user_input in ['y', 'yes']
    
    @staticmethod
    def pause():
        """Pause, wait for user to press key to continue"""
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    @staticmethod
    def clear_screen():
        """Clear screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_separator(char: str = '-', length: int = 70):
        """Print separator line"""
        print(char * length)
    
    @staticmethod
    def print_logo():
        """Print system logo"""
        logo = f"""{Fore.CYAN}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           Hotel Reservation Management System (HRMS) - CLI Version                     ║
║           Hotel Reservation Management System                     ║
║                                                                   ║
║                          Version 1.0                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
        print(logo)
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format currency"""
        return f"¥{amount:,.2f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format percentage"""
        return f"{value:.2f}%"
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """Format date display"""
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%d')
        except:
            return date_str
    
    @staticmethod
    def format_datetime(datetime_str: str) -> str:
        """Format datetime display"""
        try:
            from datetime import datetime
            # Try multiple formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                try:
                    dt_obj = datetime.strptime(datetime_str, fmt)
                    return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    continue
            return datetime_str
        except:
            return datetime_str
    
    @staticmethod
    def print_box(content: str, width: int = 70):
        """Print content with border"""
        lines = content.split('\n')
        print(f"{Fore.CYAN}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
        for line in lines:
            padding = width - len(line) - 4
            print(f"{Fore.CYAN}│{Style.RESET_ALL} {line}{' ' * padding} {Fore.CYAN}│{Style.RESET_ALL}")
        print(f"{Fore.CYAN}└{'─' * (width - 2)}┘{Style.RESET_ALL}")
