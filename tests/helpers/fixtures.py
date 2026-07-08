from __future__ import annotations

from datetime import date


def build_leave_create_payload(**overrides: object) -> dict:
    payload: dict[str, object] = {
        "leave_type": "pto",
        "leave_duration": 1.0,
        "leave_start": date(2026, 9, 10).isoformat(),
        "leave_end": date(2026, 9, 10).isoformat(),
        "location_id": "loc_us_ca",
    }
    payload.update(overrides)
    return payload


def build_leave_update_payload(action: str = "approve", **overrides: object) -> dict:
    payload: dict[str, object] = {"action": action}
    payload.update(overrides)
    return payload


def build_balance_row(**overrides: object) -> dict:
    payload: dict[str, object] = {
        "user_id": "user_emp_00001",
        "location_id": "loc_us_ca",
        "leave_type": "pto",
        "num_available": 10.0,
        "num_ytd_taken": 2.0,
        "num_limit": 15.0,
    }
    payload.update(overrides)
    return payload
