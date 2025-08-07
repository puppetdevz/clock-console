# /today Endpoint Documentation

## Overview
The `/today` endpoint (with alias `/date-info`) has been successfully implemented in `main.py`. This endpoint fetches holiday information for the current date from the Timor Tech API and returns it in a structured format.

## Endpoint Details

### Primary Endpoint: `/today`
- **Method**: GET
- **Path**: `/today`
- **Response Model**: `DateInfo`
- **Description**: Returns holiday information for today's date

### Alias Endpoint: `/date-info`
- **Method**: GET  
- **Path**: `/date-info`
- **Response Model**: `DateInfo`
- **Description**: Alias for `/today` endpoint

## Response Model

### DateInfo Schema
```python
class DateInfo(BaseModel):
    date: str                          # Date in YYYY-MM-DD format
    day_type: str                      # One of: 'workday', 'legal_holiday', 'weekend'
    holiday_name: Optional[str] = None # Holiday name (only for legal holidays)
```

## Day Type Mapping

The endpoint maps the Timor Tech API response codes to our simplified day types:

| API Type Code | API Description | Our `day_type` |
|--------------|-----------------|----------------|
| 0 | Regular workday (工作日) | `workday` |
| 1 | Weekend (周末) | `weekend` |
| 2 | Legal holiday (法定节假日) | `legal_holiday` |
| 3 | Compensatory workday (调休补班) | `workday` |

## Example Responses

### Regular Workday
```json
{
  "date": "2024-11-15",
  "day_type": "workday",
  "holiday_name": null
}
```

### Weekend
```json
{
  "date": "2024-11-16",
  "day_type": "weekend",
  "holiday_name": null
}
```

### Legal Holiday
```json
{
  "date": "2024-01-01",
  "day_type": "legal_holiday",
  "holiday_name": "元旦"
}
```

## Implementation Details

1. **Imports Added**:
   - `datetime.date` for getting today's date
   - `pydantic.BaseModel` for response model
   - `holiday_api.fetch_holiday_info` helper function

2. **Async Handler**: The endpoint is implemented as an async function to handle the async API call efficiently

3. **Error Handling**: Wraps API calls in try-catch block and returns HTTP 500 with error details if the API fails

4. **Holiday Name Logic**: Only includes `holiday_name` when `day_type` is `legal_holiday`

## Testing

### Unit Test
Run the unit test to verify functionality:
```bash
python test_today_endpoint.py
```

### API Server Test
1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Test the endpoints:
```bash
python test_api_server.py
```

### Manual Testing
Access the endpoints directly:
- http://localhost:8000/today
- http://localhost:8000/date-info
- http://localhost:8000/docs (Interactive API documentation)

## Files Modified/Created

- **Modified**: `main.py` - Added DateInfo model and /today, /date-info endpoints
- **Created**: `test_today_endpoint.py` - Unit test for the endpoint
- **Created**: `test_api_server.py` - HTTP client test for the API
- **Created**: `TODAY_ENDPOINT_README.md` - This documentation

## Dependencies

The implementation uses existing dependencies:
- `fastapi` - Web framework
- `pydantic` - Data validation
- `httpx` - Async HTTP client (used by holiday_api)
- `holiday_api.py` - Existing helper module for Timor Tech API

No new dependencies were required.
