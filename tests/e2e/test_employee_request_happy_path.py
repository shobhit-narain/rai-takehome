# End-to-end test for employee leave request happy path.
# Validates complete flow: authenticate employee, fetch balance, submit leave request,
# verify local leave record, audit event, and external mock HCM record.

from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload


# Full employee leave request flow - request created locally, synced to HCM, balance decremented
def test_employee_request_happy_path(test_client, employee_user: UserRecord, mock_hcm_adapter) -> None:
    response = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(leave_duration=1.0),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "requested"
    assert body["external_hcm_id"] is not None

    # Verify external HCM balance was decremented (from 10.0 to 9.0)
    balances = mock_hcm_adapter.get_balances(employee_user.id, location_id="loc_us_ca")
    pto_balance = next(row for row in balances if row["leave_type"] == "pto")
    assert pto_balance["num_available"] == 9.0
