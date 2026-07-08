# Tests for admin-facing leave API routes.
# Validates admin override capabilities for leave updates and audit event generation.

from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload, build_leave_update_payload


# Admin can perform leave update (approve) on any request regardless of reporting structure
def test_admin_can_run_privileged_leave_update_if_supported(
    test_client, employee_user: UserRecord, admin_user: UserRecord
) -> None:
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    response = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(admin_user.id),
        json=build_leave_update_payload("approve"),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
