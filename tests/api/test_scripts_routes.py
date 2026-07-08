# Tests for scripts API routes.
# Validates admin-only script execution, status querying, and cancellation request endpoints.

from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header


# Admin can execute a registered script (sync_all_balances)
def test_admin_can_run_script(test_client, admin_user: UserRecord) -> None:
    response = test_client.post(
        "/api/v1/scripts/sync_all_balances/run",
        headers=make_auth_header(admin_user.id),
        json={"params": {}},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


# Non-admin (employee) cannot execute scripts (403 Forbidden)
def test_non_admin_cannot_run_script(test_client, employee_user: UserRecord) -> None:
    response = test_client.post(
        "/api/v1/scripts/sync_all_balances/run",
        headers=make_auth_header(employee_user.id),
        json={"params": {}},
    )
    assert response.status_code == 403


# Admin can query script run status by ID
def test_admin_can_query_script_status(test_client, admin_user: UserRecord) -> None:
    created = test_client.post(
        "/api/v1/scripts/sync_all_balances/run",
        headers=make_auth_header(admin_user.id),
        json={"params": {}},
    ).json()

    response = test_client.get(
        f"/api/v1/scripts/runs/{created['id']}", headers=make_auth_header(admin_user.id)
    )
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


# Admin can request cancellation of a running script
def test_admin_can_request_script_cancellation(test_client, admin_user: UserRecord) -> None:
    created = test_client.post(
        "/api/v1/scripts/sync_all_balances/run",
        headers=make_auth_header(admin_user.id),
        json={"params": {}},
    ).json()

    response = test_client.post(
        f"/api/v1/scripts/runs/{created['id']}/cancel", headers=make_auth_header(admin_user.id)
    )
    assert response.status_code == 200
    assert response.json()["cancel_requested"] is True
