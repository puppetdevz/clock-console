"""
Utility module for fetching holiday information from Timor Tech API.
Provides async support and proper error handling with meaningful exceptions.
"""

import httpx
from typing import Dict, Any, Optional
from enum import Enum


class DayType(Enum):
    """Enumeration for day types based on Timor API response"""
    WORKDAY = 0              # 工作日 (Regular workday)
    WEEKEND = 1              # 周末 (Weekend)
    LEGAL_HOLIDAY = 2        # 法定节假日 (Legal holiday)
    COMPENSATORY_WORKDAY = 3 # 调休补班 (Compensatory workday)


class HolidayAPIError(Exception):
    """Base exception for Holiday API errors"""
    pass


class HolidayAPIConnectionError(HolidayAPIError):
    """Raised when connection to the API fails"""
    pass


class HolidayAPITimeoutError(HolidayAPIError):
    """Raised when the API request times out"""
    pass


class HolidayAPINotFoundError(HolidayAPIError):
    """Raised when the requested date/resource is not found"""
    pass


class HolidayAPIServerError(HolidayAPIError):
    """Raised when the API server returns a 5xx error"""
    pass


class HolidayAPIInvalidResponseError(HolidayAPIError):
    """Raised when the API returns an invalid or unexpected response"""
    pass


class HolidayAPIRateLimitError(HolidayAPIError):
    """Raised when rate limit is exceeded"""
    pass


async def fetch_holiday_info(date: str) -> dict:
    """
    Fetch holiday information for a specific date from Timor Tech API.
    
    Args:
        date: Date string in YYYY-MM-DD format
        
    Returns:
        Dictionary containing holiday information with the following structure:
        {
            'date': str,              # The requested date
            'day_type': str,          # WORKDAY, WEEKEND, LEGAL_HOLIDAY, or COMPENSATORY_WORKDAY
            'day_type_code': int,     # 0, 1, 2, or 3
            'day_name': str,          # Chinese day name (e.g., "周一", "元旦")
            'weekday': int,           # 1=Monday to 7=Sunday
            'is_working_day': bool,   # True if it's a working day
            'is_rest_day': bool,      # True if it's a rest day
            'is_holiday': bool,       # True if it's a legal holiday
            'holiday_name': str|None, # Name of the holiday if applicable
            'wage_multiplier': int,   # Wage multiplier (1 or 3)
            'target_holiday': str|None # Target holiday for compensatory workdays
        }
        
    Raises:
        HolidayAPITimeoutError: If the request times out
        HolidayAPIConnectionError: If connection to the API fails
        HolidayAPINotFoundError: If the date/resource is not found (404)
        HolidayAPIServerError: If the server returns a 5xx error
        HolidayAPIRateLimitError: If rate limit is exceeded (429)
        HolidayAPIInvalidResponseError: If the response is invalid or unexpected
    """
    url = f"https://timor.tech/api/holiday/info/{date}"
    
    # Browser-like headers to avoid potential Cloudflare protection
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            
            # Handle various HTTP status codes
            if response.status_code == 404:
                raise HolidayAPINotFoundError(f"Date not found: {date}")
            elif response.status_code == 429:
                raise HolidayAPIRateLimitError("API rate limit exceeded. Please try again later.")
            elif response.status_code >= 500:
                raise HolidayAPIServerError(f"API server error (status {response.status_code})")
            elif response.status_code != 200:
                raise HolidayAPIError(f"API request failed with status {response.status_code}")
            
            # Parse JSON response
            data = response.json()
            
            # Check API response code
            if data.get('code') != 0:
                error_code = data.get('code', 'unknown')
                error_msg = data.get('message', 'Unknown error')
                raise HolidayAPIInvalidResponseError(f"API returned error code {error_code}: {error_msg}")
            
            # Validate response structure
            if 'type' not in data:
                raise HolidayAPIInvalidResponseError("Missing 'type' field in API response")
            
            # Parse and transform the response
            type_info = data.get('type', {})
            holiday_info = data.get('holiday')
            
            # Extract type information
            day_type_code = type_info.get('type', 0)
            try:
                day_type = DayType(day_type_code)
            except ValueError:
                raise HolidayAPIInvalidResponseError(f"Invalid day type code: {day_type_code}")
            
            # Build clean response
            result = {
                'date': date,
                'day_type': day_type.name,
                'day_type_code': day_type.value,
                'day_name': type_info.get('name', ''),
                'weekday': type_info.get('week', 1),
                'is_working_day': day_type in [DayType.WORKDAY, DayType.COMPENSATORY_WORKDAY],
                'is_rest_day': day_type in [DayType.WEEKEND, DayType.LEGAL_HOLIDAY],
                'is_holiday': day_type == DayType.LEGAL_HOLIDAY,
                'holiday_name': None,
                'wage_multiplier': 1,
                'target_holiday': None
            }
            
            # Add holiday-specific information if available
            if holiday_info:
                result['is_holiday'] = holiday_info.get('holiday', False)
                result['holiday_name'] = holiday_info.get('name')
                result['wage_multiplier'] = holiday_info.get('wage', 1)
                result['target_holiday'] = holiday_info.get('target')
            
            return result
            
    except httpx.TimeoutException as e:
        raise HolidayAPITimeoutError(f"Request to holiday API timed out: {str(e)}")
    except httpx.HTTPError as e:
        raise HolidayAPIConnectionError(f"Failed to connect to holiday API: {str(e)}")
    except ValueError as e:
        # JSON decode error or other value errors
        raise HolidayAPIInvalidResponseError(f"Invalid response from API: {str(e)}")
    except HolidayAPIError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise HolidayAPIError(f"Unexpected error while fetching holiday info: {str(e)}")


# Optional: Synchronous wrapper for compatibility
def fetch_holiday_info_sync(date: str) -> dict:
    """
    Synchronous wrapper for fetch_holiday_info.
    
    This is provided for compatibility but async version is preferred.
    """
    import asyncio
    
    try:
        # Try to get the running loop
        loop = asyncio.get_running_loop()
        # We're already in an async context, can't use run()
        raise RuntimeError("Cannot call sync version from async context. Use await fetch_holiday_info() instead.")
    except RuntimeError:
        # No running loop, we can create one
        return asyncio.run(fetch_holiday_info(date))


# Example usage (for testing)
if __name__ == "__main__":
    import asyncio
    import json
    
    async def test():
        """Test the holiday API fetch function"""
        test_dates = [
            '2024-01-01',  # New Year's Day
            '2024-02-10',  # Chinese New Year
            '2024-09-14',  # Compensatory workday
            '2024-11-15',  # Regular Friday
            '2024-11-16',  # Regular Weekend
            '2099-99-99',  # Invalid date for error testing
        ]
        
        for date in test_dates:
            print(f"\nFetching info for {date}:")
            try:
                info = await fetch_holiday_info(date)
                print(json.dumps(info, indent=2, ensure_ascii=False))
            except HolidayAPIError as e:
                print(f"  Error: {type(e).__name__}: {e}")
            except Exception as e:
                print(f"  Unexpected error: {e}")
    
    # Run the test
    asyncio.run(test())
