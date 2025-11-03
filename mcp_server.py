#!/usr/bin/env python3
"""Local MCP server that proxies to VacationMCP REST API.

This script implements an MCP server via stdio transport that translates
MCP tool calls to REST API calls to your VacationMCP service on Render.

Usage:
    Set environment variables:
        VACATION_API_URL=https://your-service.onrender.com
        VACATION_API_KEY=your_api_key
    
    Then configure your MCP client to run:
        python mcp_server.py
"""

import os
import sys
import json
import requests
from typing import Any, Sequence

# Try to import MCP SDK, provide helpful error if not available
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Get configuration from environment
API_URL = os.getenv("VACATION_API_URL", "https://your-vacation-mcp.onrender.com")
API_KEY = os.getenv("VACATION_API_KEY")

if not API_KEY:
    print("Error: VACATION_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

# Initialize MCP server
server = Server("vacation-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="check_vacation_balance",
            description="Check available vacation hours for an employee (0-120 hours). Returns the number of hours available.",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Employee identifier (e.g., 'alice', 'bob')"
                    }
                },
                "required": ["employee_id"]
            }
        ),
        Tool(
            name="request_vacation",
            description="Request vacation time off. Validates balance and dates. Returns status (Approved/Declined) and reason if declined.",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "string",
                        "description": "Employee identifier"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in ISO format (YYYY-MM-DD), weekdays only"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in ISO format (YYYY-MM-DD), weekdays only"
                    }
                },
                "required": ["employee_id", "start_date", "end_date"]
            }
        ),
        Tool(
            name="list_vacation_requests",
            description="List all vacation requests for an employee. Returns a list of requests with status, dates, and hours.",
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


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls by translating to REST API calls."""
    headers = {"X-API-Key": API_KEY}
    
    try:
        if name == "check_vacation_balance":
            employee_id = arguments.get("employee_id")
            if not employee_id:
                return [TextContent(type="text", text="Error: employee_id is required")]
            
            response = requests.get(
                f"{API_URL}/balance",
                headers={**headers, "X-Employee-Id": employee_id},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return [TextContent(
                type="text",
                text=f"Employee {employee_id} has {result['hoursAvailable']} hours of vacation available."
            )]
        
        elif name == "request_vacation":
            employee_id = arguments.get("employee_id")
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            
            if not all([employee_id, start_date, end_date]):
                return [TextContent(type="text", text="Error: employee_id, start_date, and end_date are all required")]
            
            payload = {
                "employeeId": employee_id,
                "startDate": start_date,
                "endDate": end_date
            }
            response = requests.post(
                f"{API_URL}/vacation-requests",
                headers={**headers, "Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            status_text = f"Vacation request {result.get('id', 'created')}: Status is {result['status']}"
            if result.get("reason"):
                status_text += f". Reason: {result['reason']}"
            
            return [TextContent(type="text", text=status_text)]
        
        elif name == "list_vacation_requests":
            employee_id = arguments.get("employee_id")
            if not employee_id:
                return [TextContent(type="text", text="Error: employee_id is required")]
            
            response = requests.get(
                f"{API_URL}/vacation-requests",
                headers={**headers, "X-Employee-Id": employee_id},
                timeout=10
            )
            response.raise_for_status()
            requests_list = response.json()
            
            if not requests_list:
                return [TextContent(type="text", text=f"No vacation requests found for employee {employee_id}")]
            
            # Format the response nicely
            formatted = [f"Vacation requests for {employee_id}:"]
            for req in requests_list:
                formatted.append(
                    f"  - Request {req['id']}: {req['startDate']} to {req['endDate']} "
                    f"({req['totalDays']} days, {req['totalHours']} hours) - Status: {req['status']}"
                )
                if req.get("reason"):
                    formatted.append(f"    Reason: {req['reason']}")
            
            return [TextContent(type="text", text="\n".join(formatted))]
        
        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]
    
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - HTTP {e.response.status_code}"
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

