from __future__ import annotations

from src.infra.db.factories import build_leave_balance_record
from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload


def test_employee_can_get_own_balances(test_client, employee_user: UserRecord, db_session) -> None:
    db_session.add_all(
        [
            build_leave_balance_record(user_id=employee_user.id, leave_type="pto"),
            build_leave_balance_record(user_id=employee_user.id, leave_type="sick"),
        ]
    )
    db_session.flush()

    response = test_client.get(
        "/api/v1/leaves/balance", headers=make_auth_header(employee_user.id)
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 2


def test_employee_can_get_own_current_leaves(test_client, employee_user: UserRecord) -> None:
    response = test_client.get(
        "/api/v1/leaves/current", headers=make_auth_header(employee_user.id)
    )
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_employee_can_submit_valid_leave_request(test_client, employee_user: UserRecord) -> None:
    response = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    )
    assert response.status_code == 201
    assert response.json()["status"] == "requested"


def test_employee_cannot_access_manager_queue(test_client, employee_user: UserRecord) -> None:
    response = test_client.get(
        "/api/v1/leaves/manager/queue", headers=make_auth_header(employee_user.id)
    )
    assert response.status_code == 403
