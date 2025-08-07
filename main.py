from typing import Union, Optional
from datetime import date
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from holiday_api import (
    fetch_holiday_info,
    HolidayAPIConnectionError,
    HolidayAPITimeoutError,
    HolidayAPINotFoundError,
    HolidayAPIServerError,
    HolidayAPIInvalidResponseError,
    HolidayAPIRateLimitError,
    HolidayAPIError
)

app = FastAPI()

# Pydantic model for DateInfo response
class DateInfo(BaseModel):
    date: str
    day_type: str  # 'workday', 'legal_holiday', or 'weekend'
    holiday_name: Optional[str] = None


@app.get("/today", response_model=DateInfo)
async def get_today_info():
    """
    Get holiday information for today's date.
    Returns date, day_type (workday/legal_holiday/weekend), and optional holiday_name.
    
    The API type codes are mapped as follows:
    - API type 0 (workday) or 3 (compensatory workday) -> 'workday'
    - API type 1 (weekend) -> 'weekend'
    - API type 2 (legal holiday) -> 'legal_holiday'
    """
    try:
        # Get today's date in YYYY-MM-DD format
        today = date.today().strftime("%Y-%m-%d")
        
        # Fetch holiday information from the API
        holiday_info = await fetch_holiday_info(today)
        
        # Parse and validate the response
        try:
            # Validate that we have the required fields
            if not isinstance(holiday_info, dict):
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected API response format: Response is not a dictionary"
                )
            
            # Map the API's day_type_code to our day_type
            # According to the API:
            # 0 = Regular workday, 1 = Weekend, 2 = Legal holiday, 3 = Compensatory workday
            if 'day_type_code' not in holiday_info:
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected API response format: Missing 'day_type_code' field"
                )
            
            day_type_code = holiday_info['day_type_code']
            
            # Validate day_type_code is an integer
            if not isinstance(day_type_code, int):
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected API response format: 'day_type_code' is not an integer (got {type(day_type_code).__name__})"
                )
            
            # Map to our day_type
            if day_type_code == 0 or day_type_code == 3:
                # Regular workday or compensatory workday
                day_type = "workday"
            elif day_type_code == 1:
                # Weekend
                day_type = "weekend"
            elif day_type_code == 2:
                # Legal holiday
                day_type = "legal_holiday"
            else:
                # Unknown code, log warning but don't fail
                day_type = "workday"
                # Could add logging here if needed
            
            # Get holiday name if it's a legal holiday
            holiday_name = holiday_info.get('holiday_name') if day_type == "legal_holiday" else None
            
            return DateInfo(
                date=today,
                day_type=day_type,
                holiday_name=holiday_name
            )
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except (KeyError, ValueError, TypeError) as e:
            # Handle parsing errors
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected API response format: Error parsing response - {str(e)}"
            )
        
    except HTTPException:
        # Re-raise HTTPExceptions that we've already handled
        raise
    
    except Exception as e:
        # Handle network-related errors (502 Bad Gateway)
        if isinstance(e, (HolidayAPIConnectionError, HolidayAPITimeoutError, HolidayAPIServerError)):
            raise HTTPException(
                status_code=502,
                detail="Upstream holiday API unavailable"
            )
        
        # Handle rate limiting
        elif isinstance(e, HolidayAPIRateLimitError):
            raise HTTPException(
                status_code=503,
                detail="Holiday API rate limit exceeded. Please try again later."
            )
        
        # Handle not found errors
        elif isinstance(e, HolidayAPINotFoundError):
            raise HTTPException(
                status_code=404,
                detail=f"Date information not found: {str(e)}"
            )
        
        # Handle invalid response format
        elif isinstance(e, HolidayAPIInvalidResponseError):
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected API response format: {str(e)}"
            )
        
        # Handle any other Holiday API errors
        elif isinstance(e, HolidayAPIError):
            raise HTTPException(
                status_code=500,
                detail=f"Holiday API error: {str(e)}"
            )
        
        # Handle any other unexpected errors
        else:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred: {str(e)}"
            )


@app.get("/date-info", response_model=DateInfo)
async def get_date_info_alias():
    """
    Alias for /today endpoint.
    Get holiday information for today's date.
    """
    return await get_today_info()
