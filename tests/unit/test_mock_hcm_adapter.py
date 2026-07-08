# Tests for MockHcmAdapter unit functionality.
# Validates balance retrieval, leave creation with balance decrements, insufficient balance handling,
# scenario-based behavior toggling (insufficient_balance, ambiguous_success), leave updates, and scenario persistence.

from __future__ import annotations

from pathlib import Path

from src.adapters.hcm.mock_hcm_adapter import MockHcmAdapter
from tests.helpers.mock_hcm import write_mock_hcm_state


# get_balances returns all balances for a user across locations
def test_get_balances_returns_user_balances(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    balances = adapter.get_balances("user_emp_00001")

    assert len(balances) == 2
    assert balances[0]["user_id"] == "user_emp_00001"


# get_balances filters results by location_id when provided
def test_get_balances_filters_by_location(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    balances = adapter.get_balances("user_emp_00001", location_id="loc_us_ca")

    assert len(balances) == 2
    assert all(row["location_id"] == "loc_us_ca" for row in balances)


# create_leave creates external leave record and decrements PTO balance
def test_create_leave_creates_external_leave_and_decrements_balance(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    result = adapter.create_leave(
        {
            "user_id": "user_emp_00001",
            "location_id": "loc_us_ca",
            "leave_type": "pto",
            "leave_duration": 2.0,
            "leave_start": "2026-09-10",
            "leave_end": "2026-09-11",
            "approver_id": "user_mgr_0001",
        }
    )

    assert result["status"] == "requested"
    assert result["external_hcm_id"].startswith("hcm_leave_")

    # Verify balance was decremented from 10.0 to 8.0
    balances = adapter.get_balances("user_emp_00001", location_id="loc_us_ca")
    pto_balance = [row for row in balances if row["leave_type"] == "pto"][0]
    assert pto_balance["num_available"] == 8.0

    # Verify created leave is retrievable
    created_leave = adapter.get_leave(result["external_hcm_id"])
    assert created_leave is not None
    assert created_leave["status"] == "requested"


# create_leave returns rejected status when balance is insufficient
def test_create_leave_returns_rejected_when_balance_is_insufficient(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    result = adapter.create_leave(
        {
            "user_id": "user_emp_00001",
            "location_id": "loc_us_ca",
            "leave_type": "pto",
            "leave_duration": 99.0,
            "leave_start": "2026-09-10",
            "leave_end": "2026-09-30",
            "approver_id": "user_mgr_0001",
        }
    )

    assert result["status"] == "rejected"
    assert result["failure_reason"] == "insufficient balance"


# insufficient_balance scenario forces rejection regardless of actual balance
def test_create_leave_returns_rejected_when_scenario_is_enabled(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)
    adapter.activate_scenario("insufficient_balance", enabled=True)

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

    assert result["status"] == "rejected"
    assert result["failure_reason"] == "insufficient balance"


# ambiguous_success scenario returns pending_reconciliation status
def test_create_leave_returns_pending_reconciliation_when_ambiguous_success_enabled(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)
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


# update_leave with approve action changes leave status to approved
def test_update_leave_approve_changes_status(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    result = adapter.update_leave("hcm_leave_0000001", "approve")

    assert result["status"] == "approved"

    leave = adapter.get_leave("hcm_leave_0000001")
    assert leave is not None
    assert leave["status"] == "approved"


# update_leave returns not_found for non-existent external leave ID
def test_update_leave_returns_not_found_for_unknown_leave(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)

    result = adapter.update_leave("hcm_leave_missing", "approve")

    assert result["status"] == "not_found"
    assert result["failure_reason"] == "external leave not found"


# activate_scenario persists scenario state across adapter reloads
def test_activate_scenario_persists_updated_state(tmp_path: Path) -> None:
    state_file = write_mock_hcm_state(tmp_path / "mock_hcm_state.json")
    adapter = MockHcmAdapter(state_file=state_file)
    adapter.activate_scenario(
        "delayed_consistency",
        enabled=True,
        params={"user_id": "user_emp_00001"},
    )

    # Reload adapter from same state file to verify persistence
    reloaded = MockHcmAdapter(state_file=state_file)
    state = reloaded.get_state()

    assert state["scenarios"]["delayed_consistency"]["enabled"] is True
    assert state["scenarios"]["delayed_consistency"]["params"]["user_id"] == "user_emp_00001"
