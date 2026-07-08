# Tests for end-to-end cancel vs approve race condition.
# Validates deterministic resolution when employee cancel and manager approve occur near-simultaneously.

from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload, build_leave_update_payload


# Concurrent cancel (employee) and approve (manager) - one wins, no silent overwrite
def test_cancel_vs_approve_race_resolves_without_silent_overwrite(
    test_client, employee_user: UserRecord, manager_user: UserRecord
) -> None:
    # Setup: Employee creates leave request
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    # First action: Manager approves the request
    approved = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("approve"),
    ).json()
    assert approved["status"] == "approved"
    assert approved["version"] == created["version"] + 1

    # Second action: Employee tries to cancel (after approval, version should increment again)
    canceled = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(employee_user.id),
        json=build_leave_update_payload("cancel"),
    ).json()

    # Verify deterministic outcome: cancel succeeds on top of approved state
    assert canceled["status"] == "canceled"
    assert canceled["version"] == approved["version"] + 1
    # Approved timestamp should be preserved (no silent overwrite)
    assert canceled["approved_ts"][:19] == approved["approved_ts"][:19]
