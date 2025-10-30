import os
from fastapi.testclient import TestClient
from src.app import app
from src.services.balance_service import BalanceService


def setup_module(module):
    os.environ["API_KEY"] = "devkey"
    BalanceService.seed_balance("alice", 200)


def test_balance_bounds_and_route():
    client = TestClient(app)
    # Service enforces cap at 120
    assert BalanceService.get_balance_hours("alice") == 120
    resp = client.get(
        "/balance",
        headers={"X-API-Key": "devkey", "X-Employee-Id": "alice"},
    )
    assert resp.status_code == 200
    assert 0 <= resp.json()["hoursAvailable"] <= 120
