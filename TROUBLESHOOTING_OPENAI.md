# OpenAI Agent Builder Troubleshooting Guide

## Issue: Tools Not Discovered

If OpenAI Agent Builder isn't finding your tools, try these solutions:

---

## ✅ Solution 1: Updated Response Format (IMPORTANT)

The endpoint now returns tools in **OpenAI Function Calling format** instead of MCP format.

**Before (MCP format):**
```json
{
  "tools": [
    {
      "name": "check_vacation_balance",
      "description": "...",
      "inputSchema": {...}
    }
  ]
}
```

**After (OpenAI format):**
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "check_vacation_balance",
        "description": "...",
        "parameters": {...}
      }
    }
  ]
}
```

**Action:** Redeploy your service to Render with the updated code.

---

## Solution 2: Try Different URL Formats

OpenAI Agent Builder might expect different URL formats. Try these in order:

### Option A: Base URL with `/mcp` path
```
https://vacationmcp.onrender.com/mcp
```

### Option B: Base URL only (without `/mcp`)
```
https://vacationmcp.onrender.com
```
If using this, you may need to add a root endpoint that redirects or OpenAI might look for `/tools` directly.

### Option C: Full tools endpoint URL
```
https://vacationmcp.onrender.com/mcp/tools
```

---

## Solution 3: Verify Response Format in Postman

Test your `/mcp/tools` endpoint and verify it returns the correct format:

```powershell
$headers = @{ "X-API-Key" = "YOUR_API_KEY" }
$response = Invoke-RestMethod -Uri "https://vacationmcp.onrender.com/mcp/tools" -Headers $headers
$response | ConvertTo-Json -Depth 10
```

**Expected format:**
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "check_vacation_balance",
        "description": "Check available vacation hours...",
        "parameters": {
          "type": "object",
          "properties": {
            "employee_id": {
              "type": "string",
              "description": "Employee identifier..."
            }
          },
          "required": ["employee_id"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "request_vacation",
        ...
      }
    },
    {
      "type": "function",
      "function": {
        "name": "list_vacation_requests",
        ...
      }
    }
  ]
}
```

---

## Solution 4: Check Authentication

1. **Verify API Key:**
   - Ensure the API key in OpenAI Agent Builder matches the `API_KEY` in Render
   - Header name must be exactly `X-API-Key` (case-sensitive)

2. **Test Authentication:**
   ```powershell
   # Should return 401 without API key
   Invoke-RestMethod -Uri "https://vacationmcp.onrender.com/mcp/tools" -Method GET
   
   # Should return 200 with API key
   $headers = @{ "X-API-Key" = "YOUR_API_KEY" }
   Invoke-RestMethod -Uri "https://vacationmcp.onrender.com/mcp/tools" -Headers $headers
   ```

---

## Solution 5: Check Render Logs

1. Go to Render Dashboard → Your Service → Logs
2. Look for:
   - Authentication errors (401)
   - Request errors (400, 404, 500)
   - Tool discovery attempts

3. Watch logs while testing in Agent Builder:
   - You should see requests to `/mcp/tools` when Agent Builder tries to discover tools

---

## Solution 6: Alternative - Use OpenAI Actions Format

If Agent Builder doesn't support MCP directly, you might need to use OpenAI Actions format instead.

### Option A: Use OpenAPI Spec

1. FastAPI automatically generates OpenAPI spec at `/openapi.json`
2. Point Agent Builder to: `https://vacationmcp.onrender.com/openapi.json`
3. Configure authentication in Agent Builder

### Option B: Manual Function Definition

In Agent Builder, manually add functions:

```json
{
  "type": "function",
  "function": {
    "name": "check_vacation_balance",
    "description": "Check available vacation hours for an employee",
    "parameters": {
      "type": "object",
      "properties": {
        "employee_id": {
          "type": "string",
          "description": "Employee identifier"
        }
      },
      "required": ["employee_id"]
    }
  }
}
```

Then configure actions/fetch URLs pointing to your REST endpoints.

---

## Verification Checklist

- [ ] Code deployed with updated `/mcp/tools` endpoint (returns OpenAI format)
- [ ] CORS middleware added to FastAPI app
- [ ] `/mcp/tools` endpoint returns correct format (verified in Postman)
- [ ] API key matches between Render and Agent Builder
- [ ] Header name is exactly `X-API-Key`
- [ ] URL format tried: `https://vacationmcp.onrender.com/mcp`
- [ ] Render logs show no errors
- [ ] Service is accessible (test `/mcp/health`)

---

## Next Steps After Fix

1. **Redeploy to Render:**
   ```powershell
   git add .
   git commit -m "Fix OpenAI Agent Builder tool discovery format"
   git push origin main
   ```

2. **Wait for deployment** (5-10 minutes)

3. **Test endpoint format:**
   ```powershell
   $headers = @{ "X-API-Key" = "YOUR_API_KEY" }
   Invoke-RestMethod -Uri "https://vacationmcp.onrender.com/mcp/tools" -Headers $headers
   ```
   Verify it returns OpenAI format with `"type": "function"`

4. **In Agent Builder:**
   - Remove and re-add the MCP server
   - Use URL: `https://vacationmcp.onrender.com/mcp`
   - Set header: `X-API-Key: YOUR_API_KEY`
   - Click "Refresh" or "Discover Tools"

5. **If still not working:**
   - Check Render logs for errors
   - Try alternative URL formats listed above
   - Consider using OpenAI Actions/OpenAPI format instead

---

## Debugging Commands

```powershell
# Test health (no auth)
Invoke-RestMethod -Uri "https://vacationmcp.onrender.com/mcp/health"

# Test root endpoint (no auth)
Invoke-RestMethod -Uri "https://vacationmcp.onrender.com/mcp/"

# Test tools endpoint (requires auth)
$headers = @{ "X-API-Key" = "YOUR_API_KEY" }
$response = Invoke-RestMethod -Uri "https://vacationmcp.onrender.com/mcp/tools" -Headers $headers
$response.tools | ConvertTo-Json -Depth 5

# Test tool call
$headers = @{
    "X-API-Key" = "YOUR_API_KEY"
    "Content-Type" = "application/json"
}
$body = @{
    name = "check_vacation_balance"
    arguments = @{
        employee_id = "alice"
    }
} | ConvertTo-Json
Invoke-RestMethod -Uri "https://vacationmcp.onrender.com/mcp/tools/call" -Method POST -Headers $headers -Body $body
```

