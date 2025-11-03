# Testing VacationMCP on Render

This guide explains how to test your deployed VacationMCP service on Render.

## Prerequisites

1. **Get your Render URL**: After deployment, Render will provide you with a URL like:
   - `https://vacation-mcp.onrender.com` (or similar)
   - You can find this in your Render dashboard under the service details

2. **Set your API Key**: Make sure you've configured the `API_KEY` environment variable in your Render service settings. You'll need this value to authenticate requests.

## Testing Steps

### 1. Health Check (No Authentication Required)

Test that the service is running:

**PowerShell:**
```powershell
$renderUrl = "https://vacation-mcp.onrender.com"
Invoke-RestMethod -Uri "$renderUrl/health" -Method GET
```

**curl:**
```bash
curl https://vacation-mcp.onrender.com/health
```

**Expected Response:**
```json
{"status": "ok"}
```

### 2. Get Vacation Balance

Check available vacation hours for an employee. The service comes with demo data:
- `alice` has 80 hours
- `bob` has 16 hours

**PowerShell:**
```powershell
$renderUrl = "https://vacation-mcp.onrender.com"
$apiKey = "YOUR_API_KEY_HERE"
$headers = @{
    "Authorization" = "Bearer $apiKey"
    "X-Employee-Id" = "alice"
}
Invoke-RestMethod -Uri "$renderUrl/balance" -Method GET -Headers $headers
```

**curl:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     -H "X-Employee-Id: alice" \
     https://vacation-mcp.onrender.com/balance
```

**Expected Response:**
```json
{"hoursAvailable": 80}
```

### 3. Create a Vacation Request

Submit a new vacation request. Dates should be in ISO format (YYYY-MM-DD).

**PowerShell:**
```powershell
$renderUrl = "https://vacation-mcp.onrender.com"
$apiKey = "YOUR_API_KEY_HERE"
$headers = @{
    "Authorization" = "Bearer $apiKey"
    "Content-Type" = "application/json"
}
$body = @{
    employeeId = "alice"
    startDate = "2024-12-20"
    endDate = "2024-12-22"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$renderUrl/vacation-requests" -Method POST -Headers $headers -Body $body
```

**curl:**
```bash
curl -X POST https://vacation-mcp.onrender.com/vacation-requests \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "employeeId": "alice",
    "startDate": "2024-12-20",
    "endDate": "2024-12-22"
  }'
```

**Expected Response:**
```json
{
  "id": "some-uuid",
  "status": "Approved",
  "reason": null
}
```

### 4. List Vacation Requests

Get all vacation requests for an employee.

**PowerShell:**
```powershell
$renderUrl = "https://vacation-mcp.onrender.com"
$apiKey = "YOUR_API_KEY_HERE"
$headers = @{
    "Authorization" = "Bearer $apiKey"
    "X-Employee-Id" = "alice"
}
Invoke-RestMethod -Uri "$renderUrl/vacation-requests" -Method GET -Headers $headers
```

**curl:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY_HERE" \
     -H "X-Employee-Id: alice" \
     https://vacation-mcp.onrender.com/vacation-requests
```

**Expected Response:**
```json
[
  {
    "id": "some-uuid",
    "employeeId": "alice",
    "startDate": "2024-12-20",
    "endDate": "2024-12-22",
    "totalDays": 3,
    "totalHours": 24,
    "status": "Approved",
    "reason": null
  }
]
```

## Complete Test Script (PowerShell)

Save this as `test-render.ps1` and customize the variables:

```powershell
# Configuration
$renderUrl = "https://vacation-mcp.onrender.com"
$apiKey = "YOUR_API_KEY_HERE"
$employeeId = "alice"

# Test 1: Health Check
Write-Host "`n=== Testing Health Check ===" -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "$renderUrl/health" -Method GET
    Write-Host "✓ Health check passed: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
}

# Test 2: Get Balance
Write-Host "`n=== Testing Get Balance ===" -ForegroundColor Green
try {
    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "X-Employee-Id" = $employeeId
    }
    $response = Invoke-RestMethod -Uri "$renderUrl/balance" -Method GET -Headers $headers
    Write-Host "✓ Balance retrieved: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "✗ Get balance failed: $_" -ForegroundColor Red
}

# Test 3: Create Vacation Request
Write-Host "`n=== Testing Create Vacation Request ===" -ForegroundColor Green
try {
    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "Content-Type" = "application/json"
    }
    $body = @{
        employeeId = $employeeId
        startDate = "2024-12-20"
        endDate = "2024-12-22"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$renderUrl/vacation-requests" -Method POST -Headers $headers -Body $body
    Write-Host "✓ Vacation request created: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "✗ Create vacation request failed: $_" -ForegroundColor Red
}

# Test 4: List Vacation Requests
Write-Host "`n=== Testing List Vacation Requests ===" -ForegroundColor Green
try {
    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "X-Employee-Id" = $employeeId
    }
    $response = Invoke-RestMethod -Uri "$renderUrl/vacation-requests" -Method GET -Headers $headers
    Write-Host "✓ Vacation requests retrieved: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Green
} catch {
    Write-Host "✗ List vacation requests failed: $_" -ForegroundColor Red
}

Write-Host "`n=== Testing Complete ===" -ForegroundColor Cyan
```

## Testing with Python Requests

If you prefer Python:

```python
import requests

RENDER_URL = "https://vacation-mcp.onrender.com"
API_KEY = "YOUR_API_KEY_HERE"
EMPLOYEE_ID = "alice"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Health check
print("=== Health Check ===")
response = requests.get(f"{RENDER_URL}/health")
print(response.json())

# Get balance
print("\n=== Get Balance ===")
response = requests.get(
    f"{RENDER_URL}/balance",
    headers={**headers, "X-Employee-Id": EMPLOYEE_ID}
)
print(response.json())

# Create vacation request
print("\n=== Create Vacation Request ===")
response = requests.post(
    f"{RENDER_URL}/vacation-requests",
    headers=headers,
    json={
        "employeeId": EMPLOYEE_ID,
        "startDate": "2024-12-20",
        "endDate": "2024-12-22"
    }
)
print(response.json())

# List vacation requests
print("\n=== List Vacation Requests ===")
response = requests.get(
    f"{RENDER_URL}/vacation-requests",
    headers={**headers, "X-Employee-Id": EMPLOYEE_ID}
)
print(response.json())
```

## Common Issues

1. **401 Unauthorized**: Make sure your `API_KEY` environment variable is set correctly in Render and matches the value you're sending in the `Authorization: Bearer <API_KEY>` header.

2. **400 Bad Request**: 
   - Ensure dates are in ISO format (YYYY-MM-DD)
   - Check that required headers (`X-Employee-Id`) are present

3. **401 Unauthorized**: 
   - Ensure you're using `Authorization: Bearer <API_KEY>` header format
   - Verify the API key matches your Render environment variable

4. **429 Too Many Requests**: The service has rate limiting (60 requests per 60 seconds per API key). Wait a minute and try again.

4. **Service not responding**: Check the Render dashboard for service status and logs.

## Accessing FastAPI Docs

FastAPI automatically generates interactive API documentation. Once deployed, you can access:
- Swagger UI: `https://vacation-mcp.onrender.com/docs`
- ReDoc: `https://vacation-mcp.onrender.com/redoc`

Note: These endpoints may require authentication depending on your setup.

