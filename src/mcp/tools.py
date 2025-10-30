from __future__ import annotations
from typing import List, Dict, Any
from src.services.balance_service import BalanceService
from src.services.request_service import RequestService


def check_vacation_balance(employee_id: str) -> int:
    """Return available vacation hours for the employee (0..120)."""
    return BalanceService.get_balance_hours(employee_id)


def request_vacation(employee_id: str, start_date: str, end_date: str) -> dict:
    """Request vacation; returns {status, reason?, id?}."""
    req, ok, reason = RequestService.create_request(employee_id, start_date, end_date)
    return {"status": req.status, "reason": req.reason, "id": req.id}


def list_vacation_requests(employee_id: str) -> List[Dict[str, Any]]:
    items = RequestService.list_requests(employee_id)
    return [
        {
            "id": i.id,
            "employeeId": i.employee_id,
            "startDate": i.start_date,
            "endDate": i.end_date,
            "totalDays": i.total_days,
            "totalHours": i.total_hours,
            "status": i.status,
            "reason": i.reason,
        }
        for i in items
    ]
