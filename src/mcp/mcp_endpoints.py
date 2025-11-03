import logging
from fastapi import APIRouter, Depends, HTTPException
from src.middleware.auth import require_api_key
from src.mcp.tools import check_vacation_balance, request_vacation, list_vacation_requests

logger = logging.getLogger("vacationmcp")

# Create MCP router
mcp_router = APIRouter(prefix="/mcp", tags=["MCP"])

# MCP tools registry (stored in OpenAI Function Calling format compatible structure)
MCP_TOOLS = [
    {
        "name": "check_vacation_balance",
        "description": "Check available vacation hours for an employee (0-120 hours). Returns the number of hours available.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Employee identifier (e.g., 'alice', 'bob')"
                }
            },
            "required": ["employee_id"]
        }
    },
    {
        "name": "request_vacation",
        "description": "Request vacation time off. Validates balance and dates. Returns status (Approved/Declined) and reason if declined.",
        "inputSchema": {
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
    },
    {
        "name": "list_vacation_requests",
        "description": "List all vacation requests for an employee. Returns a list of requests with status, dates, and hours.",
        "inputSchema": {
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
]


@mcp_router.get("/tools")
async def list_tools(_auth: None = Depends(require_api_key)):
    """List available MCP tools in OpenAI Agent Builder format."""
    import uuid
    
    # Convert to OpenAI Agent Builder MCP format
    mcp_tools = []
    for tool in MCP_TOOLS:
        # Ensure input_schema has the required JSON schema format
        input_schema = tool["inputSchema"].copy()
        if "$schema" not in input_schema:
            input_schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        if "additionalProperties" not in input_schema:
            input_schema["additionalProperties"] = False
        
        mcp_tools.append({
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": input_schema,
            "annotations": None
        })
    
    return {
        "id": f"mcpl_{uuid.uuid4().hex}",
        "type": "mcp_list_tools",
        "server_label": "vacation-mcp",
        "tools": mcp_tools
    }


@mcp_router.post("/tools/call")
async def call_tool(
    request: dict,
    _auth: None = Depends(require_api_key)
):
    """Handle MCP tool calls."""
    tool_name = request.get("name")
    arguments = request.get("arguments", {})
    
    try:
        if tool_name == "check_vacation_balance":
            employee_id = arguments.get("employee_id")
            if not employee_id:
                raise HTTPException(status_code=400, detail="employee_id is required")
            
            hours = check_vacation_balance(employee_id)
            logger.info("mcp_tool_called tool=check_vacation_balance employee_id=%s hours=%s", employee_id, hours)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Employee {employee_id} has {hours} hours of vacation available."
                    }
                ]
            }
        
        elif tool_name == "request_vacation":
            employee_id = arguments.get("employee_id")
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            
            if not all([employee_id, start_date, end_date]):
                raise HTTPException(
                    status_code=400,
                    detail="employee_id, start_date, and end_date are all required"
                )
            
            result = request_vacation(employee_id, start_date, end_date)
            logger.info(
                "mcp_tool_called tool=request_vacation employee_id=%s start=%s end=%s status=%s",
                employee_id, start_date, end_date, result.get("status")
            )
            
            status_text = f"Vacation request {result.get('id', 'created')}: Status is {result['status']}"
            if result.get("reason"):
                status_text += f". Reason: {result['reason']}"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": status_text
                    }
                ]
            }
        
        elif tool_name == "list_vacation_requests":
            employee_id = arguments.get("employee_id")
            if not employee_id:
                raise HTTPException(status_code=400, detail="employee_id is required")
            
            requests_list = list_vacation_requests(employee_id)
            logger.info("mcp_tool_called tool=list_vacation_requests employee_id=%s count=%s", employee_id, len(requests_list))
            
            if not requests_list:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"No vacation requests found for employee {employee_id}"
                        }
                    ]
                }
            
            # Format the response nicely
            formatted = [f"Vacation requests for {employee_id}:"]
            for req in requests_list:
                formatted.append(
                    f"  - Request {req['id']}: {req['startDate']} to {req['endDate']} "
                    f"({req['totalDays']} days, {req['totalHours']} hours) - Status: {req['status']}"
                )
                if req.get("reason"):
                    formatted.append(f"    Reason: {req['reason']}")
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "\n".join(formatted)
                    }
                ]
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("mcp_tool_error tool=%s error=%s", tool_name, str(e))
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }
            ],
            "isError": True
        }


@mcp_router.get("/")
async def mcp_root(_auth: None = Depends(require_api_key)):
    """MCP root endpoint - return tools list in OpenAI Agent Builder format."""
    import uuid
    
    # Convert to OpenAI Agent Builder MCP format
    mcp_tools = []
    for tool in MCP_TOOLS:
        # Ensure input_schema has the required JSON schema format
        input_schema = tool["inputSchema"].copy()
        if "$schema" not in input_schema:
            input_schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        if "additionalProperties" not in input_schema:
            input_schema["additionalProperties"] = False
        
        mcp_tools.append({
            "name": tool["name"],
            "description": tool["description"],
            "input_schema": input_schema,
            "annotations": None
        })
    
    logger.info("mcp_root endpoint called, returning %d tools", len(mcp_tools))
    return {
        "id": f"mcpl_{uuid.uuid4().hex}",
        "type": "mcp_list_tools",
        "server_label": "vacation-mcp",
        "tools": mcp_tools
    }

@mcp_router.post("/")
async def mcp_root_post(request: dict, _auth: None = Depends(require_api_key)):
    """Handle POST /mcp/ - execute tool calls (for OpenAI Agent Builder with trailing slash)."""
    # Reuse the same logic as /tools/call
    return await call_tool(request, _auth)


@mcp_router.get("/health")
async def mcp_health():
    """MCP endpoint health check."""
    return {"status": "ok", "protocol": "mcp"}

