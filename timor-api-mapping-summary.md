# Timor Tech API - Key Field Mappings Summary

## API Endpoint
- **URL Format**: `https://timor.tech/api/holiday/info/{YYYY-MM-DD}`
- **No authentication required**
- **Returns JSON with holiday information for Chinese holidays**

## Critical Field Mappings

### Day Type Classification (`type.type`)
The most important field for determining the nature of a day:

| Value | Meaning | Description |
|-------|---------|-------------|
| **0** | **WORKDAY** | Regular working day (工作日) |
| **1** | **WEEKEND** | Weekend Saturday/Sunday (周末) |
| **2** | **LEGAL_HOLIDAY** | Official holiday (法定节假日) |
| **3** | **COMPENSATORY_WORKDAY** | Weekend turned into workday (调休补班) |

### Quick Logic Checks

```python
# Is it a working day?
is_working_day = response['type']['type'] in [0, 3]

# Is it a rest day?
is_rest_day = response['type']['type'] in [1, 2]

# Is it a legal holiday?
is_legal_holiday = response['type']['type'] == 2

# Get holiday name (if applicable)
holiday_name = response['holiday']['name'] if response['holiday'] else None
```

## Response Structure Examples

### Regular Workday (type = 0)
```json
{
  "type": {"type": 0, "name": "周五", "week": 5},
  "holiday": null
}
```

### Weekend (type = 1)
```json
{
  "type": {"type": 1, "name": "周六", "week": 6},
  "holiday": null
}
```

### Legal Holiday (type = 2)
```json
{
  "type": {"type": 2, "name": "国庆节", "week": 2},
  "holiday": {
    "holiday": true,
    "name": "国庆节",
    "wage": 3,
    "date": "2024-10-01"
  }
}
```

### Compensatory Workday (type = 3)
```json
{
  "type": {"type": 3, "name": "中秋节前补班", "week": 6},
  "holiday": {
    "holiday": false,
    "name": "中秋节前补班",
    "wage": 1,
    "target": "中秋节"
  }
}
```

## Implementation Notes

1. **Headers Required**: Use browser-like headers to avoid Cloudflare blocking
2. **Holiday Object**: Only present for holidays (type=2) and compensatory workdays (type=3)
3. **Wage Multiplier**: 
   - Normal days & compensatory workdays: 1x
   - Legal holidays: 3x (triple pay by Chinese labor law)
4. **Week Field**: 1=Monday through 7=Sunday

## Sample Implementation

```python
def get_day_status(date_str):
    """Get clean day status from Timor API"""
    response = requests.get(
        f'https://timor.tech/api/holiday/info/{date_str}',
        headers={'User-Agent': 'Mozilla/5.0...'}
    )
    data = response.json()
    
    day_type = data['type']['type']
    return {
        'is_working_day': day_type in [0, 3],
        'is_holiday': day_type == 2,
        'is_weekend': day_type == 1,
        'is_compensatory': day_type == 3,
        'holiday_name': data['holiday']['name'] if data['holiday'] else None,
        'day_name': data['type']['name']
    }
```

## Key Takeaways

✅ **Use `type.type` field** as the primary indicator for day classification  
✅ **Values 0 and 3** indicate working days  
✅ **Values 1 and 2** indicate rest days  
✅ **Holiday names** are in the `holiday.name` field when available  
✅ **No authentication needed** but browser headers recommended  

This API is stable, free, and provides comprehensive Chinese holiday information including compensatory workdays which are crucial for accurate scheduling in China.
