# OpenAI Agent Builder Integration Guide

This guide explains how to deploy your VacationMCP service to Render and configure it with OpenAI Agent Builder as an MCP client.

## Architecture Overview

Your VacationMCP service exposes:
- **REST API endpoints** (`/balance`, `/vacation-requests`, etc.) - for direct API access
- **MCP HTTP endpoints** (`/mcp/tools`, `/mcp/tools/call`) - for OpenAI Agent Builder integration

Both use the same API key authentication (`X-API-Key` header).

---

## Part 1: Deploy to Render (with MCP Endpoints)

### Step 1: Ensure MCP Endpoints Are Included

The MCP endpoints are now included in `src/app.py` via the `mcp_router`. Verify your deployment includes:
- ✅ `src/mcp/mcp_endpoints.py` (MCP router)
- ✅ `src/app.py` (includes mcp_router)
- ✅ All dependencies in `requirements.txt`

### Step 2: Deploy to Render

1. **Commit and push your changes:**
   ```powershell
   git add .
   git commit -m "Add MCP endpoints for OpenAI Agent Builder"
   git push origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Create/update your Web Service
   - Render will auto-detect `render.yaml` and deploy
   - Wait for deployment to complete (5-10 minutes)

3. **Set Environment Variable:**
   - In Render dashboard → Your Service → Environment
   - Set `API_KEY` to a secure value
   - **Save this API key** - you'll need it for Agent Builder

4. **Get your service URL:**
   - After deployment, note your Render URL (e.g., `https://vacation-mcp.onrender.com`)

### Step 3: Verify MCP Endpoints

Test the MCP endpoints are working:

```powershell
$renderUrl = "https://vacation-mcp.onrender.com"
$apiKey = "YOUR_API_KEY_HERE"

# Test MCP health endpoint
Invoke-RestMethod -Uri "$renderUrl/mcp/health" -Method GET

# Test MCP tools listing
$headers = @{ "X-API-Key" = $apiKey }
Invoke-RestMethod -Uri "$renderUrl/mcp/tools" -Method GET -Headers $headers
```

Expected response from `/mcp/tools`:
```json
{
  "tools": [
    {
      "name": "check_vacation_balance",
      "description": "...",
      "inputSchema": {...}
    },
    ...
  ]
}
```

---

## Part 2: Configure OpenAI Agent Builder

### Step 1: Access OpenAI Agent Builder

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Navigate to **Agent Builder** (or **Assistants** → **Agents**)
3. Create a new agent or select an existing one

### Step 2: Add MCP Server

1. **In your agent configuration, find the MCP/Tools section:**
   - Look for "MCP Servers", "Custom Tools", or "External APIs"
   - The exact location depends on your OpenAI account type and interface

2. **Add your MCP server:**
   - **Server URL**: `https://your-vacation-mcp.onrender.com/mcp`
   - **Authentication Method**: Select "API Key" or "Custom Headers"
   - **API Key / Header Name**: `X-API-Key`
   - **API Key Value**: Your `API_KEY` from Render environment variables

3. **Save the configuration**

### Step 3: Configure Tool Discovery

OpenAI Agent Builder should automatically discover tools from your MCP server when you:
- Click "Refresh Tools" or "Discover Tools"
- Or wait for automatic discovery

You should see three tools available:
- `check_vacation_balance`
- `request_vacation`
- `list_vacation_requests`

### Step 4: Test the Integration

1. **In Agent Builder, use the test/chat interface**

2. **Test checking balance:**
   ```
   Check vacation balance for employee alice
   ```
   Expected: Response showing "80 hours"

3. **Test requesting vacation:**
   ```
   Request vacation for alice from 2024-12-20 to 2024-12-22
   ```
   Expected: Response showing request status

4. **Test listing requests:**
   ```
   Show all vacation requests for alice
   ```
   Expected: List of vacation requests

---

## Part 3: Alternative Configuration (If Direct MCP Not Supported)

If OpenAI Agent Builder doesn't support direct MCP HTTP endpoints, you can use OpenAI's Function Calling format instead.

### Option A: Use OpenAI Function Calling

If Agent Builder supports OpenAI Function Calling format, you can create a custom integration that translates function calls to your REST API:

1. **In Agent Builder, add custom functions:**
   ```json
   {
     "name": "check_vacation_balance",
     "description": "Check available vacation hours for an employee (0-120 hours)",
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
   ```

2. **Configure action/fetch URL:**
   - URL: `https://your-vacation-mcp.onrender.com/balance`
   - Method: `GET`
   - Headers: `X-API-Key: YOUR_API_KEY`, `X-Employee-Id: {employee_id}`

3. **Repeat for other endpoints**

### Option B: Use OpenAI Actions (Beta)

If OpenAI Actions are available in your Agent Builder:

1. **Create an action configuration file** (OpenAPI spec)
2. **Point to your OpenAPI spec** at `https://your-vacation-mcp.onrender.com/openapi.json`
3. **Configure authentication** with API key

---

## Troubleshooting

### MCP Endpoints Not Found (404)

**Check:**
- Ensure `mcp_router` is included in `src/app.py`
- Verify deployment succeeded in Render logs
- Test: `https://your-service.onrender.com/mcp/health`

**Fix:**
```python
# In src/app.py, ensure you have:
from src.mcp.mcp_endpoints import mcp_router
app.include_router(mcp_router)
```

### Authentication Errors (401)

**Check:**
- API key in Agent Builder matches Render's `API_KEY`
- Header name is exactly `X-API-Key` (case-sensitive)
- API key is being sent correctly

**Test manually:**
```powershell
$headers = @{ "X-API-Key" = "your_api_key" }
Invoke-RestMethod -Uri "https://your-service.onrender.com/mcp/tools" -Headers $headers
```

### Tools Not Discovered

**Check:**
- MCP endpoint returns valid JSON: `GET /mcp/tools`
- Tool schema matches expected format
- Agent Builder supports MCP protocol

**Verify tools endpoint:**
```powershell
$headers = @{ "X-API-Key" = "your_api_key" }
$response = Invoke-RestMethod -Uri "https://your-service.onrender.com/mcp/tools" -Headers $headers
$response | ConvertTo-Json -Depth 10
```

### Tool Calls Fail

**Check Render logs:**
- Go to Render dashboard → Your Service → Logs
- Look for error messages
- Check for authentication failures

**Test tool call manually:**
```powershell
$headers = @{
    "X-API-Key" = "your_api_key"
    "Content-Type" = "application/json"
}
$body = @{
    name = "check_vacation_balance"
    arguments = @{
        employee_id = "alice"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://your-service.onrender.com/mcp/tools/call" `
    -Method POST -Headers $headers -Body $body
```

---

## MCP Endpoint Reference

### GET `/mcp/health`
Health check for MCP endpoints (no auth required)

**Response:**
```json
{
  "status": "ok",
  "protocol": "mcp"
}
```

### GET `/mcp/tools`
List available MCP tools (requires `X-API-Key` header)

**Response:**
```json
{
  "tools": [
    {
      "name": "check_vacation_balance",
      "description": "...",
      "inputSchema": {...}
    },
    ...
  ]
}
```

### POST `/mcp/tools/call`
Call an MCP tool (requires `X-API-Key` header)

**Request:**
```json
{
  "name": "check_vacation_balance",
  "arguments": {
    "employee_id": "alice"
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Employee alice has 80 hours of vacation available."
    }
  ]
}
```

---

## Next Steps

Once configured:

1. **Test all tools** through Agent Builder
2. **Monitor usage** in Render logs
3. **Add more features** as needed
4. **Consider rate limiting** if needed (already implemented in middleware)

---

## Quick Reference

- **Render Service URL**: `https://your-service.onrender.com`
- **MCP Base URL**: `https://your-service.onrender.com/mcp`
- **API Key**: Set in Render environment variables
- **Auth Header**: `X-API-Key: your_api_key`
- **Tools Endpoint**: `GET /mcp/tools`
- **Call Endpoint**: `POST /mcp/tools/call`

---

## Additional Resources

- [OpenAI Platform Documentation](https://platform.openai.com/docs)
- [Render Documentation](https://render.com/docs)
- [Model Context Protocol Spec](https://modelcontextprotocol.io)

