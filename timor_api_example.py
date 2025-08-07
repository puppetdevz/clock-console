"""
Timor Tech Chinese Holiday API Example
Demonstrates clean mapping of API responses to application-friendly formats
"""

import requests
import json
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class DayType(Enum):
    """Enumeration for day types based on Timor API response"""
    WORKDAY = 0              # 工作日
    WEEKEND = 1              # 周末
    LEGAL_HOLIDAY = 2        # 法定节假日
    COMPENSATORY_WORKDAY = 3 # 调休补班


class HolidayInfo:
    """Class to represent holiday information in a clean format"""
    
    def __init__(self, date: str, api_response: Dict[str, Any]):
        self.date = date
        self.raw_response = api_response
        
        # Parse type information
        type_info = api_response.get('type', {})
        self.day_type = DayType(type_info.get('type', 0))
        self.day_name = type_info.get('name', '')
        self.weekday = type_info.get('week', 1)  # 1=Monday, 7=Sunday
        
        # Parse holiday information
        holiday_info = api_response.get('holiday')
        if holiday_info:
            self.is_holiday = holiday_info.get('holiday', False)
            self.holiday_name = holiday_info.get('name', '')
            self.wage_multiplier = holiday_info.get('wage', 1)
            self.target_holiday = holiday_info.get('target')
        else:
            self.is_holiday = False
            self.holiday_name = None
            self.wage_multiplier = 1
            self.target_holiday = None
    
    @property
    def is_working_day(self) -> bool:
        """Check if this is a working day"""
        return self.day_type in [DayType.WORKDAY, DayType.COMPENSATORY_WORKDAY]
    
    @property
    def is_rest_day(self) -> bool:
        """Check if this is a rest day (weekend or holiday)"""
        return self.day_type in [DayType.WEEKEND, DayType.LEGAL_HOLIDAY]
    
    @property
    def day_type_description(self) -> str:
        """Get human-readable day type description"""
        descriptions = {
            DayType.WORKDAY: "Regular Workday",
            DayType.WEEKEND: "Weekend",
            DayType.LEGAL_HOLIDAY: "Legal Holiday",
            DayType.COMPENSATORY_WORKDAY: "Compensatory Workday"
        }
        return descriptions.get(self.day_type, "Unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a clean dictionary format"""
        return {
            'date': self.date,
            'day_type': self.day_type.name,
            'day_type_code': self.day_type.value,
            'day_name': self.day_name,
            'weekday': self.weekday,
            'is_working_day': self.is_working_day,
            'is_rest_day': self.is_rest_day,
            'is_holiday': self.is_holiday,
            'holiday_name': self.holiday_name,
            'wage_multiplier': self.wage_multiplier,
            'target_holiday': self.target_holiday
        }
    
    def __str__(self) -> str:
        """String representation"""
        if self.is_holiday:
            return f"{self.date}: {self.holiday_name} ({self.day_type_description})"
        elif self.day_type == DayType.COMPENSATORY_WORKDAY:
            return f"{self.date}: {self.day_name} for {self.target_holiday}"
        else:
            return f"{self.date}: {self.day_name} ({self.day_type_description})"


class TimorHolidayAPI:
    """Client for Timor Tech Holiday API"""
    
    BASE_URL = "https://timor.tech/api/holiday/info"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
    
    def get_holiday_info(self, date: str) -> Optional[HolidayInfo]:
        """
        Get holiday information for a specific date
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            HolidayInfo object or None if request fails
        """
        url = f"{self.BASE_URL}/{date}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return HolidayInfo(date, data)
                else:
                    print(f"API returned error code: {data.get('code')}")
                    return None
            else:
                print(f"Request failed with status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching holiday info: {e}")
            return None
    
    def check_dates(self, dates: list) -> Dict[str, HolidayInfo]:
        """
        Check multiple dates at once
        
        Args:
            dates: List of date strings in YYYY-MM-DD format
            
        Returns:
            Dictionary mapping dates to HolidayInfo objects
        """
        results = {}
        for date in dates:
            info = self.get_holiday_info(date)
            if info:
                results[date] = info
        return results


def main():
    """Example usage of the Timor Holiday API client"""
    
    # Initialize API client
    api = TimorHolidayAPI()
    
    # Test various dates
    test_dates = [
        '2024-01-01',   # New Year's Day (元旦)
        '2024-02-10',   # Chinese New Year (春节)
        '2024-05-01',   # Labor Day (劳动节)
        '2024-09-14',   # Compensatory workday for Mid-Autumn Festival
        '2024-10-01',   # National Day (国庆节)
        '2024-11-15',   # Regular Friday
        '2024-11-16',   # Regular Saturday
        '2024-11-17',   # Regular Sunday
    ]
    
    print("=" * 70)
    print("TIMOR TECH CHINESE HOLIDAY API - EXAMPLE OUTPUT")
    print("=" * 70)
    
    for date in test_dates:
        info = api.get_holiday_info(date)
        if info:
            print(f"\n{info}")
            print(f"  Type: {info.day_type_description} (code: {info.day_type.value})")
            print(f"  Working Day: {info.is_working_day}")
            print(f"  Rest Day: {info.is_rest_day}")
            if info.holiday_name:
                print(f"  Holiday: {info.holiday_name}")
                print(f"  Wage Multiplier: {info.wage_multiplier}x")
            print("-" * 50)
    
    # Example: Get all holidays in a date range
    print("\n" + "=" * 70)
    print("CHECKING MULTIPLE DATES - FINDING HOLIDAYS")
    print("=" * 70)
    
    dates_to_check = [f"2024-10-0{i}" for i in range(1, 8)]  # Oct 1-7, 2024
    results = api.check_dates(dates_to_check)
    
    holidays = [info for info in results.values() if info.is_holiday]
    workdays = [info for info in results.values() if info.is_working_day]
    
    print(f"\nFound {len(holidays)} holidays:")
    for h in holidays:
        print(f"  - {h}")
    
    print(f"\nFound {len(workdays)} working days:")
    for w in workdays:
        print(f"  - {w}")
    
    # Export clean JSON format
    print("\n" + "=" * 70)
    print("CLEAN JSON FORMAT EXAMPLE")
    print("=" * 70)
    
    sample_info = api.get_holiday_info('2024-01-01')
    if sample_info:
        print(json.dumps(sample_info.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
