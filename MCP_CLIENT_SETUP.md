# Using VacationMCP with MCP Clients

This guide explains how to connect your VacationMCP service (deployed on Render) to MCP clients like Claude Desktop, Cursor, or other MCP-compatible tools.

## Current Architecture

Your VacationMCP service is currently a **REST API** deployed on Render. To use it with MCP clients, you have two options:

1. **Add an MCP Server Endpoint** (Recommended) - Expose MCP protocol endpoints alongside REST
2. **Use HTTP Transport** - Configure MCP clients to call REST endpoints directly

---

## Option 1: Add MCP Server Endpoint (Recommended)

This involves adding MCP protocol support to your FastAPI app so MCP clients can discover and call your tools natively.

### Step 1: Install MCP Python SDK

Add the MCP SDK to your requirements:

```bash
pip install mcp
```

Update `requirements.txt`:
```txt
fastapi==0.115.0
uvicorn==0.30.6
pydantic==2.9.2
python-dotenv==1.0.1
mcp>=0.1.0
```

### Step 2: Add MCP Server Endpoint

Create an MCP server endpoint in your FastAPI app. Add this to `src/app.py`:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from src.mcp.tools import check_vacation_balance, request_vacation, list_vacation_requests

# Initialize MCP server
mcp_server = Server("vacation-mcp")

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="check_vacation_balance",
            description="Check available vacation hours for an employee (0-120 hours)",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Employee identifier"
                    }
                },
                "required": ["employee_id"]
            }
        ),
        Tool(
            name="request_vacation",
            description="Request vacation time off. Returns status and reason if declined.",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Employee identifier"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in ISO format (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in ISO format (YYYY-MM-DD)"
                    }
                },
                "required": ["employee_id", "start_date", "end_date"]
            }
        ),
        Tool(
            name="list_vacation_requests",
            description="List all vacation requests for an employee",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Employee identifier"
                    }
                },
                "required": ["employee_id"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "check_vacation_balance":
        employee_id = arguments.get("employee_id")
        hours = check_vacation_balance(employee_id)
        return [TextContent(type="text", text=str(hours))]
    
    elif name == "request_vacation":
        employee_id = arguments.get("employee_id")
        start_date = arguments.get("start_date")
        end_date = arguments.get("end_date")
        result = request_vacation(employee_id, start_date, end_date)
        return [TextContent(type="text", text=str(result))]
    
    elif name == "list_vacation_requests":
        employee_id = arguments.get("employee_id")
        requests = list_vacation_requests(employee_id)
        return [TextContent(type="text", text=str(requests))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

# Add HTTP endpoint for MCP
@app.post("/mcp")
async def mcp_endpoint(request: dict):
    """HTTP endpoint for MCP protocol."""
    # Handle MCP protocol requests
    # This is a simplified version - full implementation depends on MCP HTTP transport spec
    pass
```

**Note**: The exact implementation depends on the MCP SDK version and HTTP transport specification. You may need to check the MCP documentation for the current HTTP transport format.

### Step 3: Configure MCP Client

#### For Cursor (Windows)

Create or edit `%APPDATA%\Cursor\User\globalStorage\mcp.json`:

```json
{
  "mcpServers": {
    "vacation-mcp": {
      "url": "https://your-vacation-mcp.onrender.com/mcp",
      "headers": {
        "X-API-Key": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

#### For Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vacation-mcp": {
      "url": "https://your-vacation-mcp.onrender.com/mcp",
      "headers": {
        "X-API-Key": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

---

## Option 2: Configure MCP Client to Call REST API Directly

Some MCP clients support HTTP transport that can call REST APIs directly. This approach uses your existing REST endpoints.

### For Cursor with Custom MCP Configuration

Create a custom MCP server configuration that maps to your REST API:

```json
{
  "mcpServers": {
    "vacation-mcp": {
      "command": "python",
      "args": ["-m", "mcp_http_client"],
      "env": {
        "VACATION_API_URL": "https://your-vacation-mcp.onrender.com",
        "VACATION_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

You would need to create a small wrapper script (`mcp_http_client.py`) that:
1. Implements the MCP protocol via stdio
2. Translates MCP tool calls to REST API calls
3. Returns results in MCP format

---

## Option 3: Local MCP Server (Alternative)

If HTTP transport isn't available, you can run a local MCP server that proxies to your Render service:

### Create Local MCP Server (`mcp_server.py`)

```python
#!/usr/bin/env python3
"""Local MCP server that proxies to VacationMCP REST API."""
import os
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

API_URL = os.getenv("VACATION_API_URL", "https://your-vacation-mcp.onrender.com")
API_KEY = os.getenv("VACATION_API_KEY")

server = Server("vacation-mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="check_vacation_balance",
            description="Check available vacation hours for an employee (0-120 hours)",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string"}
                },
                "required": ["employee_id"]
            }
        ),
        Tool(
            name="request_vacation",
            description="Request vacation time off",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"}
                },
                "required": ["employee_id", "start_date", "end_date"]
            }
        ),
        Tool(
            name="list_vacation_requests",
            description="List all vacation requests for an employee",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string"}
                },
                "required": ["employee_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    headers = {"X-API-Key": API_KEY}
    
    if name == "check_vacation_balance":
        employee_id = arguments["employee_id"]
        response = requests.get(
            f"{API_URL}/balance",
            headers={**headers, "X-Employee-Id": employee_id}
        )
        result = response.json()
        return [TextContent(type="text", text=f"Available hours: {result['hoursAvailable']}")]
    
    elif name == "request_vacation":
        payload = {
            "employeeId": arguments["employee_id"],
            "startDate": arguments["start_date"],
            "endDate": arguments["end_date"]
        }
        response = requests.post(
            f"{API_URL}/vacation-requests",
            headers=headers,
            json=payload
        )
        result = response.json()
        status_text = f"Status: {result['status']}"
        if result.get("reason"):
            status_text += f", Reason: {result['reason']}"
        return [TextContent(type="text", text=status_text)]
    
    elif name == "list_vacation_requests":
        employee_id = arguments["employee_id"]
        response = requests.get(
            f"{API_URL}/vacation-requests",
            headers={**headers, "X-Employee-Id": employee_id}
        )
        requests_list = response.json()
        return [TextContent(type="text", text=str(requests_list))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

if __name__ == "__main__":
    asyncio.run(stdio_server(server))
```

### Configure Cursor to Use Local Server

```json
{
  "mcpServers": {
    "vacation-mcp": {
      "command": "python",
      "args": ["C:\\path\\to\\mcp_server.py"],
      "env": {
        "VACATION_API_URL": "https://your-vacation-mcp.onrender.com",
        "VACATION_API_KEY": "YOUR_API_KEY_HERE"
      }
    }
  }
}
```

---

## Testing MCP Integration

Once configured, test with your MCP client:

1. **Check Balance**: Ask your AI assistant:
   - "Check vacation balance for employee alice"
   - "How many vacation hours does bob have?"

2. **Request Vacation**: 
   - "Request vacation for alice from 2024-12-20 to 2024-12-22"
   - "Submit a vacation request for bob starting December 1st"

3. **List Requests**:
   - "Show all vacation requests for alice"
   - "What vacation requests does bob have?"

---

## Troubleshooting

### MCP Client Not Finding Server

1. **Check Configuration File Path**: Ensure you're editing the correct config file for your MCP client
2. **Restart Client**: MCP clients typically need a restart to load new server configurations
3. **Check Logs**: Look for MCP server connection errors in your client's logs

### Authentication Errors

1. **Verify API Key**: Ensure `API_KEY` matches between Render environment and your MCP config
2. **Check Headers**: Confirm headers are being sent correctly (case-sensitive)

### Connection Issues

1. **Service Health**: Verify your Render service is running: `https://your-service.onrender.com/health`
2. **Network Access**: Ensure your MCP client can reach the Render URL
3. **CORS**: If using browser-based clients, ensure CORS is configured on your FastAPI app

---

## Recommended Approach

For the quickest setup, **Option 3 (Local MCP Server)** is recommended because:
- ✅ Works with any MCP client that supports stdio transport
- ✅ No changes needed to your Render deployment
- ✅ Simple to set up and test locally
- ✅ Can be packaged as a standalone script

You can later migrate to Option 1 if you want MCP endpoints directly on your Render service.

