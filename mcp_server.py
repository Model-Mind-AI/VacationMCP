#!/usr/bin/env python3
"""VacationMCP Server using FastMCP.

This MCP server provides vacation management tools that can be used by LLMs
and AI assistants through the Model Context Protocol.

Usage:
    python mcp_server.py
    
    Or for development with auto-reload:
    fastmcp dev mcp_server.py
"""

from fastmcp import FastMCP
from src.lib.logging import setup_logging
from src.services.balance_service import BalanceService

# Setup logging
setup_logging()

# Initialize FastMCP server
mcp = FastMCP("VacationMCP")


@mcp.tool()
def check_vacation_balance(employee_id: str) -> str:
    """Check available vacation hours for an employee (0-120 hours). Returns the number of hours available.
    
    Args:
        employee_id: Employee identifier (e.g., 'alice', 'bob')
    
    Returns:
        A message indicating the employee's available vacation hours.
    """
    from src.mcp.tools import check_vacation_balance as check_balance
    hours = check_balance(employee_id)
    return f"Employee {employee_id} has {hours} hours of vacation available."


@mcp.tool()
def request_vacation(employee_id: str, start_date: str, end_date: str) -> str:
    """Request vacation time off. Validates balance and dates. Returns status (Approved/Declined) and reason if declined.
    
    Args:
        employee_id: Employee identifier
        start_date: Start date in ISO format (YYYY-MM-DD), weekdays only
        end_date: End date in ISO format (YYYY-MM-DD), weekdays only
    
    Returns:
        A message indicating the request status and reason if declined.
    """
    from src.mcp.tools import request_vacation as request_vac
    result = request_vac(employee_id, start_date, end_date)
    
    status_text = f"Vacation request {result.get('id', 'created')}: Status is {result['status']}"
    if result.get("reason"):
        status_text += f". Reason: {result['reason']}"
    
    return status_text


@mcp.tool()
def list_vacation_requests(employee_id: str) -> str:
    """List all vacation requests for an employee. Returns a list of requests with status, dates, and hours.
    
    Args:
        employee_id: Employee identifier
    
    Returns:
        A formatted list of vacation requests for the employee.
    """
    from src.mcp.tools import list_vacation_requests as list_requests
    requests_list = list_requests(employee_id)
    
    if not requests_list:
        return f"No vacation requests found for employee {employee_id}"
    
    # Format the response nicely
    formatted = [f"Vacation requests for {employee_id}:"]
    for req in requests_list:
        formatted.append(
            f"  - Request {req['id']}: {req['startDate']} to {req['endDate']} "
            f"({req['totalDays']} days, {req['totalHours']} hours) - Status: {req['status']}"
        )
        if req.get("reason"):
            formatted.append(f"    Reason: {req['reason']}")
    
    return "\n".join(formatted)


# Seed demo data on startup
@mcp.on_startup()
async def seed_demo_data():
    """Seed demo balances for quick testing."""
    BalanceService.seed_balance("alice", 80)
    BalanceService.seed_balance("bob", 16)


if __name__ == "__main__":
    mcp.run()