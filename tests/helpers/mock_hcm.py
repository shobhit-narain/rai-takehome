from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_mock_hcm_state() -> dict[str, Any]:
    return {
        "metadata": {
            "generated_at": "2026-07-05T12:00:00",
            "seed": 20260705,
            "user_count": 1,
            "balance_count": 2,
            "leave_request_count": 1,
        },
        "scenarios": {
            "insufficient_balance": {"enabled": False, "params": {}},
            "invalid_dimension": {"enabled": False, "params": {}},
            "delayed_consistency": {"enabled": False, "params": {}},
            "anniversary_refresh": {"enabled": False, "params": {}},
            "ambiguous_success": {"enabled": False, "params": {}},
            "intermittent_validation_gap": {"enabled": False, "params": {}},
        },
        "balances_by_user": {
            "user_emp_00001": [
                {
                    "user_id": "user_emp_00001",
                    "location_id": "loc_us_ca",
                    "leave_type": "pto",
                    "num_available": 10.0,
                    "num_ytd_taken": 2.0,
                    "num_limit": 15.0,
                    "external_updated_ts": "2026-07-01T12:00:00",
                },
                {
                    "user_id": "user_emp_00001",
                    "location_id": "loc_us_ca",
                    "leave_type": "sick",
                    "num_available": 5.0,
                    "num_ytd_taken": 1.0,
                    "num_limit": 8.0,
                    "external_updated_ts": "2026-07-01T12:00:00",
                },
            ]
        },
        "leaves_by_external_id": {
            "hcm_leave_0000001": {
                "external_hcm_id": "hcm_leave_0000001",
                "requestor_id": "user_emp_00001",
                "approver_id": "user_mgr_0001",
                "location_id": "loc_us_ca",
                "leave_type": "pto",
                "leave_duration": 2.0,
                "leave_start": "2026-08-10",
                "leave_end": "2026-08-11",
                "status": "requested",
                "failure_reason": "",
                "last_updated_ts": "2026-07-05T12:00:00",
            }
        },
    }


def write_mock_hcm_state(path: Path, payload: dict[str, Any] | None = None) -> Path:
    data = payload or build_mock_hcm_state()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path