import logging
from typing import List
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.lib.logging import setup_logging
from src.middleware.auth import require_api_key
from src.models.schemas import BalanceResponse, CreateRequest, RequestResponse, VacationRequest as VacationRequestModel
from src.services.balance_service import BalanceService
from src.services.request_service import RequestService
from src.mcp.mcp_endpoints import mcp_router

setup_logging()
logger = logging.getLogger("vacationmcp")

app = FastAPI(title="VacationMCP Service")

# Add CORS middleware for OpenAI Agent Builder
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify OpenAI domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
