from pydantic import BaseModel, Field
from typing import Optional, Literal


class BalanceResponse(BaseModel):
    hoursAvailable: int = Field(ge=0, le=120)


class CreateRequest(BaseModel):
    employeeId: str
    startDate: str  # ISO date
    endDate: str    # ISO date


class RequestResponse(BaseModel):
    id: str
    status: Literal["Pending", "Approved", "Declined"]
    reason: Optional[str] = None


class VacationRequest(BaseModel):
    id: str
    employeeId: str
    startDate: str
    endDate: str
    totalDays: int
    totalHours: int
    status: Literal["Pending", "Approved", "Declined"]
    reason: Optional[str] = None
