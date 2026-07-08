# Tests for MockHcmAdapter integration with file-based state persistence.
# Validates leave creation/update persistence, batch balance reads, and scenario behavior toggling.

from __future__ import annotations

import json
from pathlib import Path

from src.adapters.hcm.mock_hcm_adapter import MockHcmAdapter
from tests.helpers.mock_hcm import write_mock_hcm_state


# create_leave persists leave record to mock HCM state file
def test_mock_hcm_adapter_integration_creates_leave_in_mock_store(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    result = adapter.create_leave(
        {
            "user_id": "user_emp_00001",
            "location_id": "loc_us_ca",
            "leave_type": "pto",
            "leave_duration": 1.0,
            "leave_start": "2026-09-10",
            "leave_end": "2026-09-10",
            "approver_id": "user_mgr_0001",
        }
    )

    assert result["status"] == "requested"
    assert result["external_hcm_id"].startswith("hcm_leave_")

    # Verify the leave was persisted to the file
    with state_file.open("r", encoding="utf-8") as f:
        state = json.load(f)

    created_leave = state["leaves_by_external_id"][result["external_hcm_id"]]
    assert created_leave["status"] == "requested"
    assert created_leave["requestor_id"] == "user_emp_00001"
    assert created_leave["leave_type"] == "pto"


# update_leave persists status change to mock HCM state file
def test_mock_hcm_adapter_integration_updates_leave_in_mock_store(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    # First create a leave
    create_result = adapter.create_leave(
        {
            "user_id": "user_emp_00001",
            "location_id": "loc_us_ca",
            "leave_type": "pto",
            "leave_duration": 1.0,
            "leave_start": "2026-09-10",
            "leave_end": "2026-09-10",
            "approver_id": "user_mgr_0001",
        }
    )

    external_id = create_result["external_hcm_id"]

    # Update the leave via the adapter
    update_result = adapter.update_leave(external_id, "approve")

    assert update_result["status"] == "approved"
    assert update_result["external_hcm_id"] == external_id

    # Verify the leave was persisted to the file
    with state_file.open("r", encoding="utf-8") as f:
        state = json.load(f)

    updated_leave = state["leaves_by_external_id"][external_id]
    assert updated_leave["status"] == "approved"


# batch_get_balances returns balances for multiple users
def test_mock_hcm_adapter_integration_batch_balance_read(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    balances = adapter.batch_get_balances(["user_emp_00001", "user_emp_00002"])

    assert "user_emp_00001" in balances
    assert "user_emp_00002" in balances
    assert len(balances["user_emp_00001"]) == 2


# activate_scenario toggles behavior (ambiguous_success returns pending_reconciliation)
def test_mock_hcm_adapter_integration_scenario_toggles_alter_behavior(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    # Enable ambiguous_success scenario
    adapter.activate_scenario("ambiguous_success", enabled=True)

    result = adapter.create_leave(
        {
            "user_id": "user_emp_00001",
            "location_id": "loc_us_ca",
            "leave_type": "pto",
            "leave_duration": 1.0,
            "leave_start": "2026-09-10",
            "leave_end": "2026-09-10",
            "approver_id": "user_mgr_0001",
        }
    )

    assert result["status"] == "pending_reconciliation"
    assert result["failure_reason"] == "ambiguous upstream confirmation"

    # Verify scenario persisted to file
    with state_file.open("r", encoding="utf-8") as f:
        state = json.load(f)

    assert state["scenarios"]["ambiguous_success"]["enabled"] is True
