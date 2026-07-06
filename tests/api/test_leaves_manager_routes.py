from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload, build_leave_update_payload


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
