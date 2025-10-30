from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class VacationRequest:
    id: str
    employee_id: str
    start_date: str  # ISO date
    end_date: str    # ISO date
    total_days: int
    total_hours: int
    status: str
    reason: str | None = None


@dataclass
class InMemoryStore:
    employee_id_to_balance: Dict[str, int] = field(default_factory=dict)
    employee_id_to_requests: Dict[str, List[VacationRequest]] = field(default_factory=dict)

    def get_balance(self, employee_id: str) -> int:
        return self.employee_id_to_balance.get(employee_id, 0)

    def set_balance(self, employee_id: str, hours: int) -> None:
        self.employee_id_to_balance[employee_id] = hours

    def add_request(self, employee_id: str, request: VacationRequest) -> None:
        self.employee_id_to_requests.setdefault(employee_id, []).append(request)

    def list_requests(self, employee_id: str) -> List[VacationRequest]:
        return list(self.employee_id_to_requests.get(employee_id, []))


store = InMemoryStore()
