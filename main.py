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
    """Response model for date information including holiday status."""
    date: str
    day_type: str  # 'workday', 'legal_holiday', or 'weekend'
    holiday_name: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "date": "2024-01-01",
                    "day_type": "legal_holiday",
                    "holiday_name": "New Year's Day"
                },
                {
                    "date": "2024-03-15",
                    "day_type": "workday",
                    "holiday_name": None
                },
                {
                    "date": "2024-06-08",
                    "day_type": "weekend",
                    "holiday_name": None
                }
            ]
        }


@app.get(
    "/today",
    response_model=DateInfo,
    summary="Get today's date information",
    response_description="Information about today's date including holiday status",
    responses={
        200: {
            "description": "Successfully retrieved date information",
            "content": {
                "application/json": {
                    "examples": {
                        "workday": {
                            "summary": "Regular workday",
                            "value": {
                                "date": "2024-03-15",
                                "day_type": "workday",
                                "holiday_name": None
                            }
                        },
                        "holiday": {
                            "summary": "Legal holiday",
                            "value": {
                                "date": "2024-01-01",
                                "day_type": "legal_holiday",
                                "holiday_name": "New Year's Day"
                            }
                        },
                        "weekend": {
                            "summary": "Weekend day",
                            "value": {
                                "date": "2024-06-08",
                                "day_type": "weekend",
                                "holiday_name": None
                            }
                        }
                    }
                }
            }
        },
        404: {"description": "Date information not found"},
        500: {"description": "Internal server error or unexpected API response"},
        502: {"description": "Upstream holiday API unavailable"},
        503: {"description": "Holiday API rate limit exceeded"}
    }
)
async def get_today_info():
    """
    Get holiday information for today's date.
    
    This endpoint fetches information about the current date and determines whether it's
    a workday, weekend, or legal holiday. If it's a legal holiday, the holiday name
    will be included in the response.
    
    ## Day Type Mapping
    
    The external API provides day type codes that are mapped as follows:
    - **0** (workday) or **3** (compensatory workday) → `workday`
    - **1** (weekend) → `weekend`
    - **2** (legal holiday) → `legal_holiday`
    
    ## Response Fields
    
    - **date**: The current date in YYYY-MM-DD format
    - **day_type**: One of "workday", "weekend", or "legal_holiday"
    - **holiday_name**: The name of the holiday (only present for legal holidays)
    
    ## Error Handling
    
    - **404**: Date information not available
    - **500**: Internal server error or invalid API response format
    - **502**: Upstream holiday API is unreachable
    - **503**: Rate limit exceeded for the holiday API
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


@app.get(
    "/date-info",
    response_model=DateInfo,
    summary="Get today's date information (alias)",
    response_description="Information about today's date including holiday status",
    responses={
        200: {
            "description": "Successfully retrieved date information",
            "content": {
                "application/json": {
                    "example": {
                        "date": "2024-03-15",
                        "day_type": "workday",
                        "holiday_name": None
                    }
                }
            }
        },
        404: {"description": "Date information not found"},
        500: {"description": "Internal server error or unexpected API response"},
        502: {"description": "Upstream holiday API unavailable"},
        503: {"description": "Holiday API rate limit exceeded"}
    }
)
async def get_date_info_alias():
    """
    Alias endpoint for /today.
    
    This endpoint provides the same functionality as `/today` and returns
    holiday information for the current date. Use either endpoint based on
    your preference.
    
    See `/today` for detailed documentation about response fields and error handling.
    """
    return await get_today_info()
