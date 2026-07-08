# Tests for mock HCM API routes.
# Validates balance/leave retrieval, leave creation/update, scenario toggling, state reload, and full state inspection.

from __future__ import annotations

import json
from pathlib import Path


# GET /mock-hcm/balances/{user_id} returns seeded balance data
def test_get_mock_balances_returns_seeded_balances(client) -> None:
    response = client.get("/api/v1/mock-hcm/balances/user_emp_00001")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 2
    assert payload["items"][0]["user_id"] == "user_emp_00001"


# GET /mock-hcm/leaves/{external_id} returns existing leave record
def test_get_mock_leave_returns_existing_leave(client) -> None:
    response = client.get("/api/v1/mock-hcm/leaves/hcm_leave_0000001")

    assert response.status_code == 200
    payload = response.json()
    assert payload["external_hcm_id"] == "hcm_leave_0000001"
    assert payload["status"] == "requested"


# GET /mock-hcm/leaves/{external_id} returns 404 for non-existent leave
def test_get_mock_leave_returns_404_for_missing_leave(client) -> None:
    response = client.get("/api/v1/mock-hcm/leaves/missing_leave")

    assert response.status_code == 404


# POST /mock-hcm/leaves creates new leave record with 201 Created
def test_create_mock_leave_returns_201_for_valid_request(client) -> None:
    response = client.post(
        "/api/v1/mock-hcm/leaves",
        json={
            "user_id": "user_emp_00001",
            "location_id": "loc_us_ca",
            "leave_type": "pto",
            "leave_duration": 2.0,
            "leave_start": "2026-09-10",
            "leave_end": "2026-09-11",
            "approver_id": "user_mgr_0001",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "requested"
    assert payload["external_hcm_id"].startswith("hcm_leave_")


# POST /mock-hcm/leaves returns 409 Conflict when balance is insufficient
def test_create_mock_leave_returns_409_for_insufficient_balance(client) -> None:
    response = client.post(
        "/api/v1/mock-hcm/leaves",
        json={
            "user_id": "user_emp_00001",
            "location_id": "loc_us_ca",
            "leave_type": "pto",
            "leave_duration": 99.0,
            "leave_start": "2026-09-10",
            "leave_end": "2026-09-30",
            "approver_id": "user_mgr_0001",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "insufficient balance"


# POST /mock-hcm/leaves/{external_id}/update approves leave successfully
def test_update_mock_leave_approve_returns_200(client) -> None:
    response = client.post(
        "/api/v1/mock-hcm/leaves/hcm_leave_0000001/update",
        json={"action": "approve"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "approved"


# POST /mock-hcm/leaves/{external_id}/update returns 404 for missing leave
def test_update_mock_leave_returns_404_for_missing_external_leave(client) -> None:
    response = client.post(
        "/api/v1/mock-hcm/leaves/hcm_leave_missing/update",
        json={"action": "approve"},
    )

    assert response.status_code == 404


# POST /mock-hcm/scenarios/{name} activates scenario and returns updated state
def test_activate_mock_scenario_returns_updated_state(client) -> None:
    response = client.post(
        "/api/v1/mock-hcm/scenarios/ambiguous_success",
        json={
            "enabled": True,
            "params": {"user_id": "user_emp_00001"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario_name"] == "ambiguous_success"
    assert payload["enabled"] is True
    assert payload["params"]["user_id"] == "user_emp_00001"


# POST /mock-hcm/scenarios/{name} returns 404 for unknown scenario
def test_activate_mock_scenario_returns_404_for_unknown_scenario(client) -> None:
    response = client.post(
        "/api/v1/mock-hcm/scenarios/not_a_real_scenario",
        json={"enabled": True, "params": {}},
    )

    assert response.status_code == 404


# POST /mock-hcm/reload reloads state from file and reflects changes
def test_reload_mock_state_reloads_file_contents(client, mock_hcm_state_file: Path) -> None:
    original = json.loads(mock_hcm_state_file.read_text(encoding="utf-8"))
    original["metadata"]["seed"] = 999
    mock_hcm_state_file.write_text(json.dumps(original, indent=2), encoding="utf-8")

    response = client.post("/api/v1/mock-hcm/reload")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "reloaded"
    assert payload["metadata"]["seed"] == 999


# GET /mock-hcm/state returns full mock HCM state (balances, leaves, scenarios)
def test_get_mock_state_returns_full_state(client) -> None:
    response = client.get("/api/v1/mock-hcm/state")

    assert response.status_code == 200
    payload = response.json()
    assert "balances_by_user" in payload
    assert "leaves_by_external_id" in payload
    assert "scenarios" in payload
