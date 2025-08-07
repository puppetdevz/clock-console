"""
Script to test the FastAPI server endpoints
Run the server first with: uvicorn main:app --reload
Then run this script to test the endpoints
"""

import httpx
import asyncio
import json


async def test_endpoints():
    """Test the /today and /date-info endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Test /today endpoint
        print("Testing GET /today...")
        try:
            response = await client.get(f"{base_url}/today")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # Validate response structure
                assert "date" in data, "Missing 'date' field"
                assert "day_type" in data, "Missing 'day_type' field"
                assert data["day_type"] in ["workday", "weekend", "legal_holiday"], f"Invalid day_type: {data['day_type']}"
                print("  ✓ /today endpoint validated successfully")
            else:
                print(f"  ✗ Unexpected status code: {response.status_code}")
                print(f"  Response: {response.text}")
        except httpx.ConnectError:
            print("  ✗ Could not connect to server. Make sure it's running with: uvicorn main:app --reload")
            return
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # Test /date-info endpoint (alias)
        print("Testing GET /date-info (alias)...")
        try:
            response = await client.get(f"{base_url}/date-info")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                print("  ✓ /date-info endpoint (alias) working correctly")
            else:
                print(f"  ✗ Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # Test root endpoint
        print("Testing GET / (root)...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
            print("  ✓ Root endpoint working")
        except Exception as e:
            print(f"  ✗ Error: {e}")


if __name__ == "__main__":
    print("FastAPI Endpoint Tester")
    print("="*50)
    print("Note: Make sure the server is running with:")
    print("  uvicorn main:app --reload")
    print("="*50 + "\n")
    
    asyncio.run(test_endpoints())
    
    print("\n✅ Testing completed!")
