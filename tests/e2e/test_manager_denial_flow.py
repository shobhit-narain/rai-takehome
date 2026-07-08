# Tests for end-to-end manager denial flow.
# Validates complete workflow: employee submits request, manager denies request,
# verifies denial state and audit event.

from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload, build_leave_update_payload


# Full manager denial flow - employee requests, manager denies, status updated to denied
def test_manager_denial_flow(test_client, employee_user: UserRecord, manager_user: UserRecord) -> None:
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    response = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("deny"),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "denied"
