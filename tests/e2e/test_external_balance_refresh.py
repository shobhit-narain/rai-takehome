from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header


def test_external_balance_refresh_reconciles_local_store(
    test_client, employee_user: UserRecord, admin_user: UserRecord
) -> None:
    response = test_client.post(
        "/api/v1/scripts/sync_all_balances/run",
        headers=make_auth_header(admin_user.id),
        json={"params": {}},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

    balances_response = test_client.get(
        "/api/v1/leaves/balance", headers=make_auth_header(employee_user.id)
    )
    assert balances_response.status_code == 200
    assert len(balances_response.json()["items"]) == 2
