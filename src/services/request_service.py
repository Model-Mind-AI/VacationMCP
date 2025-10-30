from __future__ import annotations
import logging
import uuid
from datetime import date
from typing import Tuple, List

from src.lib.date_utils import count_weekdays_inclusive
from src.lib.store import store, VacationRequest

logger = logging.getLogger("vacationmcp")


class RequestService:
    @staticmethod
    def _overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
        return not (a_end < b_start or b_end < a_start)

    @staticmethod
    def _calc_days_hours(start_iso: str, end_iso: str) -> Tuple[int, int]:
        days = count_weekdays_inclusive(start_iso, end_iso)
        hours = days * 8
        return days, hours

    @staticmethod
    def create_request(employee_id: str, start_iso: str, end_iso: str) -> Tuple[VacationRequest, bool, str | None]:
        # Validate ranges and compute totals
        try:
            total_days, total_hours = RequestService._calc_days_hours(start_iso, end_iso)
        except ValueError as e:
            reason = str(e)
            req = VacationRequest(
                id=str(uuid.uuid4()),
                employee_id=employee_id,
                start_date=start_iso,
                end_date=end_iso,
                total_days=0,
                total_hours=0,
                status="Declined",
                reason=reason,
            )
            return req, False, reason

        if total_days == 0:
            reason = "No weekdays in requested range"
            req = VacationRequest(
                id=str(uuid.uuid4()),
                employee_id=employee_id,
                start_date=start_iso,
                end_date=end_iso,
                total_days=0,
                total_hours=0,
                status="Declined",
                reason=reason,
            )
            return req, False, reason

        # Check overlaps
        for existing in store.list_requests(employee_id):
            if RequestService._overlaps(
                date.fromisoformat(start_iso),
                date.fromisoformat(end_iso),
                date.fromisoformat(existing.start_date),
                date.fromisoformat(existing.end_date),
            ):
                reason = "Overlapping request exists"
                req = VacationRequest(
                    id=str(uuid.uuid4()),
                    employee_id=employee_id,
                    start_date=start_iso,
                    end_date=end_iso,
                    total_days=total_days,
                    total_hours=total_hours,
                    status="Declined",
                    reason=reason,
                )
                return req, False, reason

        # Check balance
        current_balance = store.get_balance(employee_id)
        if total_hours > current_balance:
            reason = "Insufficient balance"
            req = VacationRequest(
                id=str(uuid.uuid4()),
                employee_id=employee_id,
                start_date=start_iso,
                end_date=end_iso,
                total_days=total_days,
                total_hours=total_hours,
                status="Declined",
                reason=reason,
            )
            return req, False, reason

        # Approve and deduct
        new_balance = current_balance - total_hours
        store.set_balance(employee_id, new_balance)
        req = VacationRequest(
            id=str(uuid.uuid4()),
            employee_id=employee_id,
            start_date=start_iso,
            end_date=end_iso,
            total_days=total_days,
            total_hours=total_hours,
            status="Approved",
            reason=None,
        )
        store.add_request(employee_id, req)
        logger.info("vacation_request_approved employee_id=%s id=%s hours=%s new_balance=%s", employee_id, req.id, total_hours, new_balance)
        return req, True, None

    @staticmethod
    def list_requests(employee_id: str) -> List[VacationRequest]:
        return store.list_requests(employee_id)
