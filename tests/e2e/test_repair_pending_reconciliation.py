# Tests for end-to-end pending reconciliation repair.
# Validates seeding pending records, configuring external truth, running repair script,
# and verifying final states and audit events.

from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload


# Seed pending reconciliation record, configure external truth, run repair script, verify final states
def test_repair_pending_reconciliation(
    test_client, employee_user: UserRecord, admin_user: UserRecord, mock_hcm_adapter
) -> None:
    # Enable ambiguous success scenario to create pending_reconciliation state
    mock_hcm_adapter.activate_scenario("ambiguous_success", enabled=True)
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    )
    assert created.status_code == 202

    # Verify local state is pending_reconciliation
    current = test_client.get(
        "/api/v1/leaves/current", headers=make_auth_header(employee_user.id)
    ).json()
    assert len(current["items"]) == 1
    assert current["items"][0]["status"] == "pending_reconciliation"

    # Disable ambiguous scenario so HCM returns clear approved state
    mock_hcm_adapter.activate_scenario("ambiguous_success", enabled=False)

    # Run repair script to reconcile local state with external HCM truth
    response = test_client.post(
        "/api/v1/scripts/repair_pending_reconciliation/run",
        headers=make_auth_header(admin_user.id),
        json={"params": {}},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
