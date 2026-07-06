from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload


def test_repair_pending_reconciliation(
    test_client, employee_user: UserRecord, admin_user: UserRecord, mock_hcm_adapter
) -> None:
    mock_hcm_adapter.activate_scenario("ambiguous_success", enabled=True)
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    )
    assert created.status_code == 202

    current = test_client.get(
        "/api/v1/leaves/current", headers=make_auth_header(employee_user.id)
    ).json()
    assert len(current["items"]) == 1
    assert current["items"][0]["status"] == "pending_reconciliation"

    mock_hcm_adapter.activate_scenario("ambiguous_success", enabled=False)

    response = test_client.post(
        "/api/v1/scripts/repair_pending_reconciliation/run",
        headers=make_auth_header(admin_user.id),
        json={"params": {}},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
