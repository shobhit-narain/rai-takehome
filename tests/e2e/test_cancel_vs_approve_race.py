from __future__ import annotations

from src.infra.db.models import UserRecord
from tests.helpers.auth import make_auth_header
from tests.helpers.fixtures import build_leave_create_payload, build_leave_update_payload


def test_cancel_vs_approve_race_resolves_without_silent_overwrite(
    test_client, employee_user: UserRecord, manager_user: UserRecord
) -> None:
    created = test_client.post(
        "/api/v1/leaves/request",
        headers=make_auth_header(employee_user.id),
        json=build_leave_create_payload(),
    ).json()

    approved = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(manager_user.id),
        json=build_leave_update_payload("approve"),
    ).json()
    assert approved["status"] == "approved"
    assert approved["version"] == created["version"] + 1

    canceled = test_client.post(
        f"/api/v1/leaves/{created['id']}/update",
        headers=make_auth_header(employee_user.id),
        json=build_leave_update_payload("cancel"),
    ).json()

    assert canceled["status"] == "canceled"
    assert canceled["version"] == approved["version"] + 1
    assert canceled["approved_ts"][:19] == approved["approved_ts"][:19]
