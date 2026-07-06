from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header


def test_scheduled_sync_all_balances(test_client, employee_user: UserRecord, admin_user: UserRecord) -> None:
    scheduled = test_client.post(
        "/api/v1/scripts/sync_all_balances/schedule",
        headers=make_auth_header(admin_user.id),
        json={"cron_expression": "0 * * * *", "params": {}},
    )
    assert scheduled.status_code == 200
    assert scheduled.json()["schedule_expression"] == "0 * * * *"

    run = test_client.post(
        "/api/v1/scripts/sync_all_balances/run",
        headers=make_auth_header(admin_user.id),
        json={"params": {}},
    )
    assert run.status_code == 200
    assert run.json()["status"] == "completed"

    balances = test_client.get(
        "/api/v1/leaves/balance", headers=make_auth_header(employee_user.id)
    )
    assert len(balances.json()["items"]) == 2
