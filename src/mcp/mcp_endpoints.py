import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Body
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
async def list_tools():
    """List available MCP tools in OpenAI Agent Builder format."""
    return _get_tools_response()

@mcp_router.post("/tools")
async def list_tools_post(request: Optional[dict] = Body(None)):
    """Handle POST request to list tools (for MCP protocol)."""
    return _get_tools_response()

def _get_tools_response():
    """Helper function to generate tools response in MCP format."""
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
    
    response = {
        "id": f"mcpl_{uuid.uuid4().hex}",
        "type": "mcp_list_tools",
        "server_label": "vacation-mcp",
        "tools": mcp_tools
    }
    logger.info("list_tools called, returning %d tools", len(mcp_tools))
    return response


@mcp_router.post("/tools/call")
async def call_tool(request: dict = Body(...)):
    """Handle MCP tool calls."""
    logger.info("MCP tool call received: %s", request)
    
    # Handle different MCP request formats
    # Format 1: Direct format { "name": "...", "arguments": {...} }
    # Format 2: JSON-RPC format { "method": "tools/call", "params": { "name": "...", "arguments": {...} } }
    # Format 3: OpenAI format { "name": "...", "arguments": {...} }
    
    tool_name = None
    arguments = {}
    
    if "params" in request:
        # JSON-RPC format
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
    else:
        # Direct format
        # Support { "tool": { "name": "..." }, ... }
        tool = request.get("tool")
        if tool and isinstance(tool, dict):
            tool_name = tool.get("name")
            arguments = request.get("arguments", {}) or tool.get("arguments", {}) or {}
        else:
            tool_name = request.get("name")
            # Some clients use "args" or "input" instead of "arguments"
            arguments = (
                request.get("arguments")
                or request.get("args")
                or request.get("input")
                or {}
            )
    
    logger.info("Extracted tool_name=%s, arguments=%s", tool_name, arguments)
    
    if not tool_name:
        logger.warning("No tool name in request. Full request: %s", request)
        # Return a helpful error response instead of raising exception
        return {
            "content": [
                {
                    "type": "text",
                    "text": "Error: Missing 'name' field in request. Request format should be: {\"name\": \"tool_name\", \"arguments\": {...}}"
                }
            ],
            "isError": True
        }
    
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
async def mcp_root():
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

# Support non-slash path to avoid redirects from "/mcp" -> "/mcp/"
@mcp_router.get("")
async def mcp_root_noslash():
    return await mcp_root()

@mcp_router.post("/")
async def mcp_root_post(request: Request):
    """Handle POST /mcp/ - execute tool calls or handle MCP protocol messages."""
    try:
        # Parse JSON body, handling empty body gracefully
        body = await request.json()
    except Exception as e:
        # If no body or invalid JSON, return tools list (common for connection tests)
        logger.info("mcp_root_post called with empty/invalid body: %s", str(e))
        # JSON-RPC parse error
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"}
        }
    
    logger.info("mcp_root_post called with request: %s", body)
    
    # Use the parsed body
    request_data = body if body else {}
    
    # If empty body, invalid request
    if not request_data:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": "Invalid Request"}
        }
    
    req_id = request_data.get("id")
    method = request_data.get("method")

    # Check if this is an MCP protocol initialization or other message
    if method:
        params = request_data.get("params", {})
        
        # Handle MCP protocol methods
        if method == "tools/call":
            result = await call_tool({"name": params.get("name"), "arguments": params.get("arguments", {})})
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        elif method == "tools/list":
            # Return tools list in MCP protocol format
            tools_response = _get_tools_response()
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_response.get("tools", [])}}
        elif method == "initialize":
            # MCP initialization - return server capabilities
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "vacation-mcp", "version": "1.0.0"},
                    "capabilities": {"tools": {}}
                }
            }
        else:
            logger.warning("Unknown MCP method: %s", method)
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    
    # If no method field, invalid JSON-RPC request
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid Request"}}

# Support non-slash path to avoid redirects from "/mcp" -> "/mcp/"
@mcp_router.post("")
async def mcp_root_post_noslash(request: Request):
    return await mcp_root_post(request)


@mcp_router.get("/health")
async def mcp_health():
    """MCP endpoint health check."""
    return {"status": "ok", "protocol": "mcp"}

