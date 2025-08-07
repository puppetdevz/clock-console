# Timor Tech Chinese Holiday API Documentation

## API Endpoint
- Base URL: `https://timor.tech/api/holiday/info/{date}`
- Format: `YYYY-MM-DD` (e.g., `2024-01-01`)
- Method: GET
- No authentication required
- Returns JSON response

## Response Schema

### Root Structure
```json
{
  "code": 0,           // Status code (0 = success)
  "type": {...},       // Day type information
  "holiday": {...}     // Holiday details (null if not a holiday or compensatory day)
}
```

### Type Object Fields

The `type` object contains:
- **`type`** (integer): Day classification
  - `0` = Regular workday (工作日)
  - `1` = Weekend (周末)
  - `2` = Legal holiday (法定节假日)
  - `3` = Compensatory workday (调休补班)
  
- **`name`** (string): Day name
  - For regular days: "周一", "周二", "周三", "周四", "周五", "周六", "周日"
  - For holidays: Holiday name (e.g., "元旦", "国庆节", "劳动节")
  - For compensatory workdays: Description (e.g., "中秋节前补班")
  
- **`week`** (integer): Day of week
  - `1` = Monday
  - `2` = Tuesday
  - `3` = Wednesday
  - `4` = Thursday
  - `5` = Friday
  - `6` = Saturday
  - `7` = Sunday

### Holiday Object Fields

The `holiday` object (when not null) contains:
- **`holiday`** (boolean): 
  - `true` = It's a holiday (rest day)
  - `false` = It's a compensatory workday
  
- **`name`** (string): Holiday or event name
  
- **`wage`** (integer): Wage multiplier
  - `1` = Normal wage (compensatory workday)
  - `3` = Triple wage (legal holidays)
  
- **`date`** (string): The date in YYYY-MM-DD format
  
- **`rest`** (integer, optional): Number of rest days (appears for some holidays)
  
- **`target`** (string, optional): Target holiday for compensatory workdays
  
- **`after`** (boolean, optional): Whether this is before or after the holiday
  - `false` = Before the holiday

## Response Examples

### 1. Regular Workday
```json
{
  "code": 0,
  "type": {
    "type": 0,
    "name": "周五",
    "week": 5
  },
  "holiday": null
}
```

### 2. Weekend (Saturday/Sunday)
```json
{
  "code": 0,
  "type": {
    "type": 1,
    "name": "周六",
    "week": 6
  },
  "holiday": null
}
```

### 3. Legal Holiday
```json
{
  "code": 0,
  "type": {
    "type": 2,
    "name": "元旦",
    "week": 1
  },
  "holiday": {
    "holiday": true,
    "name": "元旦",
    "wage": 3,
    "date": "2024-01-01"
  }
}
```

### 4. Compensatory Workday
```json
{
  "code": 0,
  "type": {
    "type": 3,
    "name": "中秋节前补班",
    "week": 6
  },
  "holiday": {
    "holiday": false,
    "name": "中秋节前补班",
    "after": false,
    "wage": 1,
    "target": "中秋节",
    "date": "2024-09-14",
    "rest": 84
  }
}
```

## Mapping Guide for Applications

### Day Type Classification Logic
```python
def classify_day(response):
    if response['type']['type'] == 0:
        return 'WORKDAY'
    elif response['type']['type'] == 1:
        return 'WEEKEND'
    elif response['type']['type'] == 2:
        return 'LEGAL_HOLIDAY'
    elif response['type']['type'] == 3:
        return 'COMPENSATORY_WORKDAY'
```

### Is Working Day Logic
```python
def is_working_day(response):
    # Working days are: regular workdays (type 0) and compensatory workdays (type 3)
    return response['type']['type'] in [0, 3]
```

### Is Holiday Logic
```python
def is_holiday(response):
    # Holidays are: legal holidays (type 2)
    return response['type']['type'] == 2
```

### Holiday Name Extraction
```python
def get_holiday_name(response):
    if response['holiday'] and response['holiday']['holiday']:
        return response['holiday']['name']
    return None
```

## Important Notes

1. **Compensatory Workdays**: These are weekend days that become workdays to compensate for extended holiday periods. They have `type.type = 3` and `holiday.holiday = false`.

2. **Regular Weekends vs Holidays**: Regular weekends have `holiday = null`, while holiday weekends have `holiday` object with details.

3. **Wage Multiplier**: Legal holidays typically have `wage = 3` (triple pay), while compensatory workdays have `wage = 1` (normal pay).

4. **API Headers**: The API may require browser-like headers to avoid Cloudflare protection:
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}
```

## Usage Example in Python
```python
import requests
import json

def get_holiday_info(date):
    """
    Get holiday information for a specific date
    
    Args:
        date (str): Date in YYYY-MM-DD format
    
    Returns:
        dict: Holiday information
    """
    url = f'https://timor.tech/api/holiday/info/{date}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status {response.status_code}")

# Example usage
date_info = get_holiday_info('2024-01-01')
print(json.dumps(date_info, indent=2, ensure_ascii=False))
```
