# Holiday API Utility Module

## Overview

The `holiday_api.py` module provides a clean, async interface for fetching Chinese holiday information from the Timor Tech API. It handles all error scenarios gracefully and converts third-party HTTP status codes into meaningful Python exceptions, keeping route handlers clean and maintainable.

## Features

- **Async Support**: Built with `httpx` for async/await compatibility
- **Comprehensive Error Handling**: Catches and converts all API errors into specific exception types
- **Clean Data Format**: Returns normalized, easy-to-use dictionary structure
- **Type Safety**: Uses Enums for day types and proper type hints
- **Timeout Protection**: Built-in timeout handling (10 seconds default)
- **Cloudflare Bypass**: Includes browser-like headers to avoid protection mechanisms

## Installation

Ensure you have the required dependency:

```bash
pip install httpx
```

## Usage

### Basic Usage

```python
from holiday_api import fetch_holiday_info

# In an async context (e.g., FastAPI route)
async def get_holiday(date: str):
    try:
        info = await fetch_holiday_info(date)
        return info
    except HolidayAPITimeoutError:
        # Handle timeout
        pass
    except HolidayAPINotFoundError:
        # Handle not found
        pass
    # ... handle other exceptions
```

### Response Format

The function returns a dictionary with the following structure:

```python
{
    'date': '2024-01-01',              # The requested date
    'day_type': 'LEGAL_HOLIDAY',       # WORKDAY, WEEKEND, LEGAL_HOLIDAY, or COMPENSATORY_WORKDAY
    'day_type_code': 2,                # 0, 1, 2, or 3
    'day_name': '元旦',                # Chinese day name
    'weekday': 1,                      # 1=Monday to 7=Sunday
    'is_working_day': False,           # True if it's a working day
    'is_rest_day': True,               # True if it's a rest day
    'is_holiday': True,                # True if it's a legal holiday
    'holiday_name': '元旦',            # Name of the holiday if applicable
    'wage_multiplier': 3,              # Wage multiplier (1 or 3)
    'target_holiday': None             # Target holiday for compensatory workdays
}
```

## Exception Hierarchy

The module defines a clear exception hierarchy for different error scenarios:

```
HolidayAPIError (base exception)
├── HolidayAPIConnectionError      # Connection failures
├── HolidayAPITimeoutError         # Request timeouts
├── HolidayAPINotFoundError        # 404 - Date not found
├── HolidayAPIServerError          # 5xx server errors
├── HolidayAPIRateLimitError       # 429 - Rate limit exceeded
└── HolidayAPIInvalidResponseError # Invalid/unexpected response
```

## FastAPI Integration Example

```python
from fastapi import FastAPI, HTTPException
from holiday_api import (
    fetch_holiday_info,
    HolidayAPITimeoutError,
    HolidayAPINotFoundError,
    HolidayAPIServerError,
    HolidayAPIError
)

app = FastAPI()

@app.get("/holiday/{date}")
async def get_holiday(date: str):
    try:
        # Clean call - no need to handle HTTP status codes
        return await fetch_holiday_info(date)
        
    except HolidayAPINotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
    except HolidayAPITimeoutError as e:
        raise HTTPException(status_code=504, detail=f"Gateway timeout: {str(e)}")
        
    except HolidayAPIServerError as e:
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")
        
    except HolidayAPIError as e:
        raise HTTPException(status_code=500, detail=f"Holiday API error: {str(e)}")
```

## Day Type Classification

The module uses an Enum for day types:

- `WORKDAY` (0): Regular working day
- `WEEKEND` (1): Weekend (Saturday/Sunday)
- `LEGAL_HOLIDAY` (2): Legal holiday
- `COMPENSATORY_WORKDAY` (3): Compensatory workday (weekend turned into workday)

## Testing

Run the module directly to test with sample dates:

```bash
python holiday_api.py
```

This will test various date types including holidays, weekends, workdays, and invalid dates.

## Benefits

1. **Clean Route Handlers**: No need to handle raw HTTP responses or status codes in your application logic
2. **Predictable Errors**: All errors are converted to specific exception types
3. **Consistent Data Format**: Always returns the same structure regardless of the API response variations
4. **Async-First**: Designed for modern async Python applications
5. **Robust Error Handling**: Handles timeouts, connection errors, and unexpected responses gracefully

## API Endpoint

The module connects to:
- Base URL: `https://timor.tech/api/holiday/info/{date}`
- Format: `YYYY-MM-DD`
- No authentication required

## Notes

- The API returns Chinese holiday information primarily for mainland China
- Compensatory workdays are weekend days that become workdays to compensate for extended holiday periods
- Legal holidays typically have 3x wage multiplier, while compensatory workdays have 1x
- The module includes browser-like headers to avoid potential Cloudflare protection
