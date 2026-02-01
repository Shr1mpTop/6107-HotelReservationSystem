"""
Test pricing API endpoint
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.pricing_service import PricingService
from datetime import datetime, timedelta

# Test the calculate_price method
room_type_id = 1  # Standard Single Room
check_in = datetime.now().strftime('%Y-%m-%d')
check_out = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')

print(f"Testing price calculation for:")
print(f"Room Type ID: {room_type_id}")
print(f"Check-in: {check_in}")
print(f"Check-out: {check_out}")
print()

# Test calculate_total_price
result = PricingService.calculate_total_price(room_type_id, check_in, check_out)
print(f"calculate_total_price result: {result}")
print()

# Test calculate_price
price = PricingService.calculate_price(room_type_id, check_in, check_out)
print(f"calculate_price result: {price}")
print(f"Type: {type(price)}")
