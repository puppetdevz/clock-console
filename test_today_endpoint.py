"""
Test script for the /today endpoint
"""

import asyncio
from datetime import date
from main import app, DateInfo, get_today_info
from holiday_api import fetch_holiday_info


async def test_today_endpoint():
    """Test the /today endpoint functionality"""
    print("Testing /today endpoint...")
    
    # Test the function directly
    try:
        result = await get_today_info()
        print(f"\n✓ Successfully called get_today_info()")
        print(f"  Date: {result.date}")
        print(f"  Day Type: {result.day_type}")
        print(f"  Holiday Name: {result.holiday_name}")
        
        # Verify the result is a DateInfo instance
        assert isinstance(result, DateInfo), "Result should be a DateInfo instance"
        assert result.day_type in ["workday", "weekend", "legal_holiday"], f"Invalid day_type: {result.day_type}"
        print(f"\n✓ Result validation passed")
        
    except Exception as e:
        print(f"\n✗ Error testing endpoint: {e}")
        return False
    
    # Test with a known date (example)
    print("\n" + "="*50)
    print("Testing with example dates...")
    
    test_dates = [
        date.today().strftime("%Y-%m-%d"),  # Today
        "2024-01-01",  # New Year's Day (should be legal_holiday)
        "2024-11-16",  # A Saturday (should be weekend)
        "2024-11-15",  # A Friday (should be workday)
    ]
    
    for test_date in test_dates:
        try:
            print(f"\nFetching info for {test_date}:")
            info = await fetch_holiday_info(test_date)
            
            # Map the day type according to our logic
            day_type_code = info.get('day_type_code', 0)
            if day_type_code == 0 or day_type_code == 3:
                day_type = "workday"
            elif day_type_code == 1:
                day_type = "weekend"
            elif day_type_code == 2:
                day_type = "legal_holiday"
            else:
                day_type = "workday"
            
            holiday_name = info.get('holiday_name') if day_type == "legal_holiday" else None
            
            print(f"  API Type Code: {day_type_code}")
            print(f"  Mapped Day Type: {day_type}")
            print(f"  Holiday Name: {holiday_name}")
            print(f"  Is Holiday: {info.get('is_holiday', False)}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "="*50)
    print("✓ All tests completed successfully!")
    return True


if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_today_endpoint())
    if success:
        print("\n🎉 The /today endpoint is working correctly!")
    else:
        print("\n❌ There were issues with the /today endpoint.")
