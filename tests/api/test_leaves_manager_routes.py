# Tests for manager-facing leave API routes.
# Validates queue listing with status filtering, approval/denial workflows,
# authorization checks for reporting tree, and mitigating circumstances requirements.

from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload, build_leave_update_payload


# Manager can list leave requests for their direct/indirect reports
def test_manager_can_list_managed_leave_requests(
    test_client, employee_user: UserRecord, manager_user: UserRecord
) -> None:
    test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    )

    response = test_client.get(
        "/api/v1/leaves/manager/queue", headers=make_auth_header(manager_user.id)
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


# Manager queue excludes terminal statuses (approved/denied/complete) by default
def test_manager_queue_excludes_terminal_statuses_by_default(
    test_client, employee_user: UserRecord, manager_user: UserRecord
) -> None:
    # Create a request and approve it
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("approve"),
    )

    # Queue should be empty now (approved is terminal-ish, excluded by default)
    response = test_client.get(
        "/api/v1/leaves/manager/queue", headers=make_auth_header(manager_user.id)
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 0


# Manager queue includes terminal statuses when include_all=true query param is set
def test_manager_queue_includes_terminal_statuses_when_requested(
    test_client, employee_user: UserRecord, manager_user: UserRecord
) -> None:
    # Create a request and approve it
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("approve"),
    )

    # Queue should include terminal statuses when requested
    response = test_client.get(
        "/api/v1/leaves/manager/queue?include_all=true",
        headers=make_auth_header(manager_user.id)
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["status"] == "approved"


# Manager can approve a pending leave request for their report
def test_manager_can_approve_pending_request(
    test_client, employee_user: UserRecord, manager_user: UserRecord
) -> None:
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    response = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("approve"),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


# Manager cannot approve leave request for employee outside their reporting tree
def test_manager_cannot_approve_unrelated_employee_request(
    test_client, employee_user: UserRecord, manager_user: UserRecord, db_session
) -> None:
    from src.infra.db.factories import build_user_record

    db_session.add(build_user_record(id="user_other_mgr", role="manager"))
    db_session.flush()

    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    response = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header("user_other_mgr"),
        json=build_leave_update_payload("approve"),
    )
    assert response.status_code == 403


# Manager cannot deny already-approved leave without mitigating circumstances
def test_manager_cannot_deny_approved_leave_without_mitigating_circumstances(
    test_client, employee_user: UserRecord, manager_user: UserRecord
) -> None:
    # Create and approve a leave request
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("approve"),
    )

    # Try to deny without mitigating_circumstances - should fail
    response = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("deny"),
    )
    assert response.status_code == 403
    assert "mitigating_circumstances" in response.json()["message"]


# Manager can deny approved leave when mitigating circumstances are provided
def test_manager_can_deny_approved_leave_with_mitigating_circumstances(
    test_client, employee_user: UserRecord, manager_user: UserRecord
) -> None:
    # Create and approve a leave request
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("approve"),
    )

    # Deny with mitigating_circumstances - should succeed
    response = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("deny", mitigating_circumstances="Business needs changed"),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "denied"


# Manager can deny requested (not yet approved) leave without mitigating circumstances
def test_manager_can_deny_requested_leave_without_mitigating_circumstances(
    test_client, employee_user: UserRecord, manager_user: UserRecord
) -> None:
    # Create a leave request (still in REQUESTED state)
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    # Deny without mitigating_circumstances - should succeed for REQUESTED status
    response = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("deny"),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "denied"
