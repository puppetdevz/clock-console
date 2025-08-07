"""
Test script to verify the robust error handling in the /today endpoint.
This script simulates various error scenarios to ensure proper HTTP status codes
and error messages are returned.
"""

import asyncio
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from main import app
from fastapi.testclient import TestClient
from holiday_api import (
    HolidayAPIConnectionError,
    HolidayAPITimeoutError,
    HolidayAPIServerError,
    HolidayAPIInvalidResponseError,
    HolidayAPIRateLimitError,
    HolidayAPINotFoundError,
    HolidayAPIError
)

# Create test client
client = TestClient(app)


def test_network_error_returns_502():
    """Test that network errors return 502 Bad Gateway"""
    
    # Test connection error
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = HolidayAPIConnectionError("Connection failed")
        response = client.get("/today")
        assert response.status_code == 502
        assert response.json()["detail"] == "Upstream holiday API unavailable"
    
    # Test timeout error
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = HolidayAPITimeoutError("Request timed out")
        response = client.get("/today")
        assert response.status_code == 502
        assert response.json()["detail"] == "Upstream holiday API unavailable"
    
    # Test server error
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = HolidayAPIServerError("Server error")
        response = client.get("/today")
        assert response.status_code == 502
        assert response.json()["detail"] == "Upstream holiday API unavailable"
    
    print("✓ Network error tests passed (502 Bad Gateway)")


def test_invalid_response_format_returns_500():
    """Test that invalid response formats return 500 Internal Server Error"""
    
    # Test non-dictionary response
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = "not a dictionary"
        response = client.get("/today")
        assert response.status_code == 500
        assert "Response is not a dictionary" in response.json()["detail"]
    
    # Test missing day_type_code field
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {"date": "2024-01-01"}  # Missing day_type_code
        response = client.get("/today")
        assert response.status_code == 500
        assert "Missing 'day_type_code' field" in response.json()["detail"]
    
    # Test invalid day_type_code type
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {"day_type_code": "not an int"}
        response = client.get("/today")
        assert response.status_code == 500
        assert "'day_type_code' is not an integer" in response.json()["detail"]
    
    # Test HolidayAPIInvalidResponseError
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = HolidayAPIInvalidResponseError("Invalid JSON")
        response = client.get("/today")
        assert response.status_code == 500
        assert "Unexpected API response format" in response.json()["detail"]
    
    print("✓ Invalid response format tests passed (500 Internal Server Error)")


def test_rate_limit_returns_503():
    """Test that rate limit errors return 503 Service Unavailable"""
    
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = HolidayAPIRateLimitError("Rate limit exceeded")
        response = client.get("/today")
        assert response.status_code == 503
        assert "rate limit exceeded" in response.json()["detail"].lower()
    
    print("✓ Rate limit test passed (503 Service Unavailable)")


def test_not_found_returns_404():
    """Test that not found errors return 404 Not Found"""
    
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = HolidayAPINotFoundError("Date not found")
        response = client.get("/today")
        assert response.status_code == 404
        assert "Date information not found" in response.json()["detail"]
    
    print("✓ Not found test passed (404 Not Found)")


def test_generic_holiday_api_error_returns_500():
    """Test that generic HolidayAPIError returns 500"""
    
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = HolidayAPIError("Generic API error")
        response = client.get("/today")
        assert response.status_code == 500
        assert "Holiday API error" in response.json()["detail"]
    
    print("✓ Generic Holiday API error test passed (500 Internal Server Error)")


def test_unexpected_error_returns_500():
    """Test that unexpected errors return 500"""
    
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = RuntimeError("Completely unexpected error")
        response = client.get("/today")
        assert response.status_code == 500
        assert "An unexpected error occurred" in response.json()["detail"]
    
    print("✓ Unexpected error test passed (500 Internal Server Error)")


def test_successful_response():
    """Test that a successful response works correctly"""
    
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        # Mock a valid response
        mock_fetch.return_value = {
            "day_type_code": 2,  # Legal holiday
            "holiday_name": "New Year's Day",
            "date": "2024-01-01"
        }
        response = client.get("/today")
        assert response.status_code == 200
        data = response.json()
        assert data["day_type"] == "legal_holiday"
        assert data["holiday_name"] == "New Year's Day"
    
    # Test workday
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "day_type_code": 0,  # Workday
            "date": "2024-01-02"
        }
        response = client.get("/today")
        assert response.status_code == 200
        data = response.json()
        assert data["day_type"] == "workday"
        assert data["holiday_name"] is None
    
    # Test weekend
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "day_type_code": 1,  # Weekend
            "date": "2024-01-06"
        }
        response = client.get("/today")
        assert response.status_code == 200
        data = response.json()
        assert data["day_type"] == "weekend"
        assert data["holiday_name"] is None
    
    # Test compensatory workday
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "day_type_code": 3,  # Compensatory workday
            "date": "2024-01-07"
        }
        response = client.get("/today")
        assert response.status_code == 200
        data = response.json()
        assert data["day_type"] == "workday"
    
    print("✓ Successful response tests passed")


def test_alias_endpoint():
    """Test that the /date-info alias endpoint works the same way"""
    
    with patch('main.fetch_holiday_info', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = HolidayAPIConnectionError("Connection failed")
        response = client.get("/date-info")
        assert response.status_code == 502
        assert response.json()["detail"] == "Upstream holiday API unavailable"
    
    print("✓ Alias endpoint test passed")


if __name__ == "__main__":
    print("Running error handling tests...\n")
    
    test_network_error_returns_502()
    test_invalid_response_format_returns_500()
    test_rate_limit_returns_503()
    test_not_found_returns_404()
    test_generic_holiday_api_error_returns_500()
    test_unexpected_error_returns_500()
    test_successful_response()
    test_alias_endpoint()
    
    print("\n✅ All error handling tests passed successfully!")
