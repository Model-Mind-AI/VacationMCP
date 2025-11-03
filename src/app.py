import logging
from typing import List
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.lib.logging import setup_logging
from src.middleware.auth import require_api_key, security
from src.models.schemas import BalanceResponse, CreateRequest, RequestResponse, VacationRequest as VacationRequestModel
from src.services.balance_service import BalanceService
from src.services.request_service import RequestService
from src.mcp.mcp_endpoints import mcp_router

setup_logging()
logger = logging.getLogger("vacationmcp")

app = FastAPI(
    title="VacationMCP Service",
    description="Vacation management service with MCP support",
    version="1.0.0"
)

# Add OAuth2 security scheme to OpenAPI docs
app.openapi_schema = None  # Force regeneration

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add OAuth2 Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "API Key",
            "description": "OAuth2 Bearer token authentication. Pass your API key as the Bearer token."
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add CORS middleware for OpenAI Agent Builder
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify OpenAI domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add handlers for /mcp without trailing slash FIRST (to avoid 307 redirect)
# OpenAI Agent Builder calls /mcp directly - GET for tools list, POST for tool execution
# This must be registered BEFORE the router to prevent FastAPI redirect

@app.get("/mcp", include_in_schema=False)
async def mcp_get_tools():
    """Handle GET /mcp - return tools list in OpenAI Agent Builder MCP format."""
    from src.mcp.mcp_endpoints import MCP_TOOLS
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
    
    logger.info("mcp_get_tools endpoint called, returning %d tools", len(mcp_tools))
    return {
        "id": f"mcpl_{uuid.uuid4().hex}",
        "type": "mcp_list_tools",
        "server_label": "vacation-mcp",
        "tools": mcp_tools
    }

@app.post("/mcp", include_in_schema=False)
async def mcp_post_tool_call(request: dict):
    """Handle POST /mcp - execute tool calls for OpenAI Agent Builder."""
    from src.mcp.tools import check_vacation_balance, request_vacation, list_vacation_requests
    
    logger.info("mcp_post_tool_call received request: %s", request)
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

# Include MCP router for OpenAI Agent Builder support
app.include_router(mcp_router)


@app.on_event("startup")
def seed_demo_data() -> None:
    # Seed demo balances for quick testing
    BalanceService.seed_balance("alice", 80)
    BalanceService.seed_balance("bob", 16)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/balance", response_model=BalanceResponse)
def get_balance(
    employee_id: str = Header(..., alias="X-Employee-Id"),
    _auth: None = Depends(require_api_key),
) -> BalanceResponse:
    if not employee_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Employee-Id header")
    hours = BalanceService.get_balance_hours(employee_id)
    logger.info("balance_checked employee_id=%s hours=%s", employee_id, hours)
    return BalanceResponse(hoursAvailable=hours)


@app.post("/vacation-requests", response_model=RequestResponse, status_code=201)
def create_vacation_request(
    payload: CreateRequest,
    _auth: None = Depends(require_api_key),
) -> RequestResponse:
    req, ok, reason = RequestService.create_request(payload.employeeId, payload.startDate, payload.endDate)
    if not ok:
        logger.info(
            "vacation_request_declined employee_id=%s reason=%s start=%s end=%s",
            payload.employeeId,
            reason,
            payload.startDate,
            payload.endDate,
        )
        return RequestResponse(id=req.id, status=req.status, reason=req.reason)

    return RequestResponse(id=req.id, status=req.status, reason=None)


@app.get("/vacation-requests", response_model=List[VacationRequestModel])
def list_vacation_requests(
    employee_id: str = Header(..., alias="X-Employee-Id"),
    _auth: None = Depends(require_api_key),
) -> List[VacationRequestModel]:
    if not employee_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing X-Employee-Id header")
    items = RequestService.list_requests(employee_id)
    return [
        VacationRequestModel(
            id=i.id,
            employeeId=i.employee_id,
            startDate=i.start_date,
            endDate=i.end_date,
            totalDays=i.total_days,
            totalHours=i.total_hours,
            status=i.status,
            reason=i.reason,
        )
        for i in items
    ]
