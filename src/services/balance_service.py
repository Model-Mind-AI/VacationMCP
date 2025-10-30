from __future__ import annotations
from typing import Optional
from src.lib.store import store


class BalanceService:
    @staticmethod
    def get_balance_hours(employee_id: str) -> int:
        hours = store.get_balance(employee_id)
        # Ensure bounds 0..120
        if hours < 0:
            hours = 0
        if hours > 120:
            hours = 120
        return hours

    @staticmethod
    def seed_balance(employee_id: str, hours: int) -> None:
        # Helper for demos/tests
        bounded = max(0, min(120, hours))
        store.set_balance(employee_id, bounded)
