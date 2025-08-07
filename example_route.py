"""
Example FastAPI application demonstrating the use of the holiday_api module.
Shows how the route handler stays clean thanks to the exception conversion.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn

from holiday_api import (
    fetch_holiday_info,
    HolidayAPITimeoutError,
    HolidayAPINotFoundError,
    HolidayAPIServerError,
    HolidayAPIRateLimitError,
    HolidayAPIInvalidResponseError,
    HolidayAPIConnectionError,
    HolidayAPIError
)

app = FastAPI(title="Holiday API Service", version="1.0.0")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Holiday Information API",
        "endpoints": {
            "/holiday/{date}": "Get holiday information for a specific date",
            "/holiday": "Get holiday information with date as query parameter"
        },
        "example": "/holiday/2024-01-01 or /holiday?date=2024-01-01"
    }


@app.get("/holiday/{date}")
async def get_holiday_by_path(date: str):
    """
    Get holiday information for a specific date.
    
    The route handler remains clean because all third-party API errors
    are converted to meaningful Python exceptions by the utility module.
    """
    try:
        # Clean call to the utility function
        holiday_info = await fetch_holiday_info(date)
        return holiday_info
        
    except HolidayAPINotFoundError as e:
        # Date not found - return 404
        raise HTTPException(status_code=404, detail=str(e))
        
    except HolidayAPITimeoutError as e:
        # Timeout - return 504 Gateway Timeout
        raise HTTPException(status_code=504, detail=f"Gateway timeout: {str(e)}")
        
    except HolidayAPIRateLimitError as e:
        # Rate limit exceeded - return 429 Too Many Requests
        raise HTTPException(status_code=429, detail=str(e))
        
    except HolidayAPIServerError as e:
        # Server error - return 502 Bad Gateway
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")
        
    except HolidayAPIConnectionError as e:
        # Connection error - return 503 Service Unavailable
        raise HTTPException(status_code=503, detail=f"Service temporarily unavailable: {str(e)}")
        
    except HolidayAPIInvalidResponseError as e:
        # Invalid response - return 502 Bad Gateway
        raise HTTPException(status_code=502, detail=f"Invalid response from external API: {str(e)}")
        
    except HolidayAPIError as e:
        # Generic API error - return 500
        raise HTTPException(status_code=500, detail=f"Holiday API error: {str(e)}")
        
    except Exception as e:
        # Unexpected error - return 500
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/holiday")
async def get_holiday_by_query(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    """
    Alternative endpoint using query parameter instead of path parameter.
    Demonstrates the same clean error handling.
    """
    try:
        holiday_info = await fetch_holiday_info(date)
        return holiday_info
        
    except HolidayAPINotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HolidayAPITimeoutError as e:
        raise HTTPException(status_code=504, detail=f"Gateway timeout: {str(e)}")
    except HolidayAPIRateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except HolidayAPIServerError as e:
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")
    except HolidayAPIConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Service temporarily unavailable: {str(e)}")
    except HolidayAPIInvalidResponseError as e:
        raise HTTPException(status_code=502, detail=f"Invalid response from external API: {str(e)}")
    except HolidayAPIError as e:
        raise HTTPException(status_code=500, detail=f"Holiday API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/holiday/batch")
async def get_holidays_batch(dates: str = Query(..., description="Comma-separated dates in YYYY-MM-DD format")):
    """
    Get holiday information for multiple dates at once.
    Example: /holiday/batch?dates=2024-01-01,2024-02-10,2024-05-01
    """
    date_list = [d.strip() for d in dates.split(",")]
    results = {}
    errors = {}
    
    for date in date_list:
        try:
            holiday_info = await fetch_holiday_info(date)
            results[date] = holiday_info
        except HolidayAPIError as e:
            # Collect errors but don't stop processing other dates
            errors[date] = {
                "error": type(e).__name__,
                "message": str(e)
            }
        except Exception as e:
            errors[date] = {
                "error": "UnexpectedError",
                "message": str(e)
            }
    
    return {
        "success": results,
        "errors": errors,
        "total": len(date_list),
        "successful": len(results),
        "failed": len(errors)
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler for better error responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "status": exc.status_code,
                "message": exc.detail,
                "path": str(request.url)
            }
        }
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "example_route:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
