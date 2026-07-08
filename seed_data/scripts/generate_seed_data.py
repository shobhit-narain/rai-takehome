#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


DEFAULT_OUTPUT_DIR = Path("seed_data")
DEFAULT_SEED = 20260705
DEFAULT_EMPLOYEE_COUNT = 5000
DEFAULT_MANAGER_COUNT = 250
DEFAULT_ADMIN_COUNT = 5
DEFAULT_LOCATIONS = [
    "loc_us_ca",
    "loc_us_tx",
    "loc_us_ny",
    "loc_us_wa",
    "loc_us_il",
]
DEFAULT_LEAVE_TYPES = ["pto", "sick"]


@dataclass
class UserRow:
    id: str
    email: str
    name: str
    role: str
    manager_id: str
    location_id: str
    is_active: str
    created_ts: str
    updated_ts: str


@dataclass
class LeaveBalanceRow:
    id: str
    user_id: str
    location_id: str
    leave_type: str
    num_available: str
    num_ytd_taken: str
    num_limit: str
    external_updated_ts: str
    updated_ts: str


@dataclass
class LeaveRequestRow:
    id: str
    external_hcm_id: str
    requestor_id: str
    approver_id: str
    location_id: str
    leave_type: str
    leave_duration: str
    leave_start: str
    leave_end: str
    status: str
    failure_reason: str
    version: str
    created_ts: str
    updated_ts: str
    approved_ts: str
    complete_ts: str
    last_synced_ts: str


@dataclass
class HcmConfigRow:
    id: str
    provider_name: str
    base_url: str
    auth_type: str
    token_ref: str
    rate_limit_default: str
    is_active: str
    created_ts: str
    updated_ts: str


@dataclass
class ScriptRunRow:
    id: str
    script_name: str
    status: str
    schedule_expression: str
    params_json: str
    started_ts: str
    finished_ts: str
    cancel_requested: str
    error_message: str


@dataclass
class AuditEventRow:
    id: str
    entity_type: str
    entity_id: str
    action: str
    actor_user_id: str
    payload_json: str
    created_ts: str


def ts(days_offset: int = 0, minutes_offset: int = 0) -> str:
    base = datetime(2026, 7, 1, 12, 0, 0)
    return (base + timedelta(days=days_offset, minutes=minutes_offset)).isoformat()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows provided for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def build_admins(rng: random.Random, count: int, locations: list[str]) -> list[UserRow]:
    rows: list[UserRow] = []
    for i in range(1, count + 1):
        user_id = f"user_admin_{i:03d}"
        location_id = locations[(i - 1) % len(locations)]
        rows.append(
            UserRow(
                id=user_id,
                email=f"{user_id}@example.com",
                name=f"Admin {i}",
                role="admin",
                manager_id="",
                location_id=location_id,
                is_active="true",
                created_ts=ts(),
                updated_ts=ts(),
            )
        )
    return rows


def build_managers(
    rng: random.Random,
    count: int,
    locations: list[str],
    admin_ids: list[str],
) -> list[UserRow]:
    rows: list[UserRow] = []
    for i in range(1, count + 1):
        user_id = f"user_mgr_{i:04d}"
        location_id = locations[(i - 1) % len(locations)]
        manager_id = admin_ids[(i - 1) % len(admin_ids)]
        rows.append(
            UserRow(
                id=user_id,
                email=f"{user_id}@example.com",
                name=f"Manager {i}",
                role="manager",
                manager_id=manager_id,
                location_id=location_id,
                is_active="true",
                created_ts=ts(),
                updated_ts=ts(),
            )
        )
    return rows


def build_employees(
    rng: random.Random,
    count: int,
    managers: list[UserRow],
    locations: list[str],
) -> list[UserRow]:
    rows: list[UserRow] = []
    managers_by_location: dict[str, list[UserRow]] = defaultdict(list)
    for manager in managers:
        managers_by_location[manager.location_id].append(manager)

    for i in range(1, count + 1):
        user_id = f"user_emp_{i:05d}"
        location_id = locations[(i - 1) % len(locations)]
        location_managers = managers_by_location[location_id]
        assigned_manager = location_managers[(i - 1) % len(location_managers)]
        rows.append(
            UserRow(
                id=user_id,
                email=f"{user_id}@example.com",
                name=f"Employee {i}",
                role="employee",
                manager_id=assigned_manager.id,
                location_id=location_id,
                is_active="true",
                created_ts=ts(),
                updated_ts=ts(),
            )
        )
    return rows


def build_leave_balances(
    rng: random.Random,
    employees: list[UserRow],
    leave_types: list[str],
) -> list[LeaveBalanceRow]:
    rows: list[LeaveBalanceRow] = []
    counter = 1
    for employee in employees:
        for leave_type in leave_types:
            if leave_type == "pto":
                num_limit = rng.choice([15.0, 18.0, 20.0])
                ytd_taken = round(rng.uniform(0, min(10.0, num_limit)), 1)
                num_available = round(max(0.0, num_limit - ytd_taken - rng.uniform(0, 3.0)), 1)
            else:
                num_limit = rng.choice([8.0, 10.0, 12.0])
                ytd_taken = round(rng.uniform(0, min(5.0, num_limit)), 1)
                num_available = round(max(0.0, num_limit - ytd_taken - rng.uniform(0, 1.5)), 1)

            rows.append(
                LeaveBalanceRow(
                    id=f"bal_{counter:07d}",
                    user_id=employee.id,
                    location_id=employee.location_id,
                    leave_type=leave_type,
                    num_available=f"{num_available:.1f}",
                    num_ytd_taken=f"{ytd_taken:.1f}",
                    num_limit=f"{num_limit:.1f}",
                    external_updated_ts=ts(days_offset=-3),
                    updated_ts=ts(days_offset=0),
                )
            )
            counter += 1
    return rows


def build_leave_requests(
    rng: random.Random,
    employees: list[UserRow],
    manager_lookup: dict[str, str],
    leave_types: list[str],
    request_ratio: float = 0.22,
) -> list[LeaveRequestRow]:
    rows: list[LeaveRequestRow] = []
    counter = 1
    status_weights = [
        ("requested", 0.40),
        ("approved", 0.28),
        ("denied", 0.10),
        ("canceled", 0.08),
        ("complete", 0.09),
        ("pending_reconciliation", 0.05),
    ]
    statuses = [s for s, _ in status_weights]
    weights = [w for _, w in status_weights]

    request_count = int(len(employees) * request_ratio)

    selected_indexes = list(range(len(employees)))
    rng.shuffle(selected_indexes)
    selected_indexes = selected_indexes[:request_count]

    for i in selected_indexes:
        employee = employees[i]
        leave_type = rng.choice(leave_types)
        duration = rng.choice([0.5, 1.0, 2.0, 3.0, 5.0])
        start_day = rng.randint(1, 180)
        leave_start = date(2026, 1, 1) + timedelta(days=start_day)
        leave_end = leave_start + timedelta(days=max(0, int(duration) - 1))
        status = rng.choices(statuses, weights=weights, k=1)[0]
        approver_id = manager_lookup.get(employee.id, "")
        created_ts = ts(days_offset=-rng.randint(1, 45), minutes_offset=rng.randint(0, 600))
        updated_ts = ts(days_offset=-rng.randint(0, 30), minutes_offset=rng.randint(0, 600))
        approved_ts = ""
        complete_ts = ""
        failure_reason = ""

        if status == "approved":
            approved_ts = updated_ts
        elif status == "complete":
            approved_ts = ts(days_offset=-rng.randint(20, 40), minutes_offset=rng.randint(0, 600))
            complete_ts = updated_ts
        elif status == "denied":
            failure_reason = "manager denied request"
        elif status == "canceled":
            failure_reason = "employee canceled request"
        elif status == "pending_reconciliation":
            failure_reason = "awaiting external confirmation"

        rows.append(
            LeaveRequestRow(
                id=f"leave_{counter:07d}",
                external_hcm_id=f"hcm_leave_{counter:07d}",
                requestor_id=employee.id,
                approver_id=approver_id,
                location_id=employee.location_id,
                leave_type=leave_type,
                leave_duration=f"{duration:.1f}",
                leave_start=leave_start.isoformat(),
                leave_end=leave_end.isoformat(),
                status=status,
                failure_reason=failure_reason,
                version=str(rng.randint(1, 4)),
                created_ts=created_ts,
                updated_ts=updated_ts,
                approved_ts=approved_ts,
                complete_ts=complete_ts,
                last_synced_ts=updated_ts,
            )
        )
        counter += 1

    rows.sort(key=lambda x: x.id)
    return rows


def build_hcm_configs() -> list[HcmConfigRow]:
    return [
        HcmConfigRow(
            id="hcm_cfg_001",
            provider_name="mock_hcm",
            base_url="http://127.0.0.1:8000/api/v1/mock-hcm",
            auth_type="bearer",
            token_ref="local-dev-token",
            rate_limit_default="100",
            is_active="true",
            created_ts=ts(),
            updated_ts=ts(),
        )
    ]


def build_script_runs() -> list[ScriptRunRow]:
    return [
        ScriptRunRow(
            id="run_000001",
            script_name="sync_all_balances",
            status="completed",
            schedule_expression="",
            params_json="{}",
            started_ts=ts(days_offset=-7),
            finished_ts=ts(days_offset=-7, minutes_offset=5),
            cancel_requested="false",
            error_message="",
        ),
        ScriptRunRow(
            id="run_000002",
            script_name="reconcile_recent_leaves",
            status="failed",
            schedule_expression="",
            params_json="{}",
            started_ts=ts(days_offset=-2),
            finished_ts=ts(days_offset=-2, minutes_offset=2),
            cancel_requested="false",
            error_message="upstream timeout",
        ),
    ]


def build_audit_events(
    rng: random.Random,
    leave_requests: list[LeaveRequestRow],
) -> list[AuditEventRow]:
    rows: list[AuditEventRow] = []
    counter = 1

    for leave in leave_requests[: min(len(leave_requests), 3000)]:
        rows.append(
            AuditEventRow(
                id=f"audit_{counter:07d}",
                entity_type="leave_request",
                entity_id=leave.id,
                action="created",
                actor_user_id=leave.requestor_id,
                payload_json=json.dumps({"status": leave.status}, sort_keys=True),
                created_ts=leave.created_ts,
            )
        )
        counter += 1

        if leave.status in {"approved", "complete"} and leave.approver_id:
            rows.append(
                AuditEventRow(
                    id=f"audit_{counter:07d}",
                    entity_type="leave_request",
                    entity_id=leave.id,
                    action="approved",
                    actor_user_id=leave.approver_id,
                    payload_json=json.dumps({"status": leave.status}, sort_keys=True),
                    created_ts=leave.updated_ts,
                )
            )
            counter += 1

        if leave.status == "denied" and leave.approver_id:
            rows.append(
                AuditEventRow(
                    id=f"audit_{counter:07d}",
                    entity_type="leave_request",
                    entity_id=leave.id,
                    action="denied",
                    actor_user_id=leave.approver_id,
                    payload_json=json.dumps({"status": leave.status}, sort_keys=True),
                    created_ts=leave.updated_ts,
                )
            )
            counter += 1

        if leave.status == "canceled":
            rows.append(
                AuditEventRow(
                    id=f"audit_{counter:07d}",
                    entity_type="leave_request",
                    entity_id=leave.id,
                    action="canceled",
                    actor_user_id=leave.requestor_id,
                    payload_json=json.dumps({"status": leave.status}, sort_keys=True),
                    created_ts=leave.updated_ts,
                )
            )
            counter += 1

        if leave.status == "pending_reconciliation":
            rows.append(
                AuditEventRow(
                    id=f"audit_{counter:07d}",
                    entity_type="leave_request",
                    entity_id=leave.id,
                    action="reconciliation_requested",
                    actor_user_id=leave.approver_id or leave.requestor_id,
                    payload_json=json.dumps({"status": leave.status}, sort_keys=True),
                    created_ts=leave.updated_ts,
                )
            )
            counter += 1

    return rows


def build_mock_hcm_state(
    rng: random.Random,
    users: list[UserRow],
    leave_balances: list[LeaveBalanceRow],
    leave_requests: list[LeaveRequestRow],
) -> dict:
    balances_by_user: dict[str, list[dict]] = defaultdict(list)
    leaves_by_external_id: dict[str, dict] = {}
    scenarios = {
        "insufficient_balance": {"enabled": False, "params": {}},
        "invalid_dimension": {"enabled": False, "params": {}},
        "delayed_consistency": {"enabled": False, "params": {}},
        "anniversary_refresh": {"enabled": False, "params": {}},
        "ambiguous_success": {"enabled": False, "params": {}},
        "intermittent_validation_gap": {"enabled": False, "params": {}},
    }

    for row in leave_balances:
        external_available = float(row.num_available)
        drift_roll = rng.random()

        if drift_roll < 0.05:
            external_available = round(external_available + rng.choice([1.0, 2.0]), 1)
        elif drift_roll < 0.10:
            external_available = round(max(0.0, external_available - rng.choice([1.0, 2.0])), 1)

        balances_by_user[row.user_id].append(
            {
                "user_id": row.user_id,
                "location_id": row.location_id,
                "leave_type": row.leave_type,
                "num_available": external_available,
                "num_ytd_taken": float(row.num_ytd_taken),
                "num_limit": float(row.num_limit),
                "external_updated_ts": row.external_updated_ts,
            }
        )

    for row in leave_requests:
        leaves_by_external_id[row.external_hcm_id] = {
            "external_hcm_id": row.external_hcm_id,
            "requestor_id": row.requestor_id,
            "approver_id": row.approver_id,
            "location_id": row.location_id,
            "leave_type": row.leave_type,
            "leave_duration": float(row.leave_duration),
            "leave_start": row.leave_start,
            "leave_end": row.leave_end,
            "status": row.status,
            "failure_reason": row.failure_reason,
            "last_updated_ts": row.updated_ts,
        }

    return {
        "metadata": {
            "generated_at": ts(),
            "seed": DEFAULT_SEED,
            "user_count": len(users),
            "balance_count": len(leave_balances),
            "leave_request_count": len(leave_requests),
        },
        "scenarios": scenarios,
        "balances_by_user": balances_by_user,
        "leaves_by_external_id": leaves_by_external_id,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deterministic seed data for the time-off service.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--employee-count", type=int, default=DEFAULT_EMPLOYEE_COUNT)
    parser.add_argument("--manager-count", type=int, default=DEFAULT_MANAGER_COUNT)
    parser.add_argument("--admin-count", type=int, default=DEFAULT_ADMIN_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)

    admins = build_admins(rng, args.admin_count, DEFAULT_LOCATIONS)
    managers = build_managers(rng, args.manager_count, DEFAULT_LOCATIONS, [a.id for a in admins])
    employees = build_employees(rng, args.employee_count, managers, DEFAULT_LOCATIONS)

    users = admins + managers + employees
    manager_lookup = {u.id: u.manager_id for u in employees}
    leave_balances = build_leave_balances(rng, employees, DEFAULT_LEAVE_TYPES)
    leave_requests = build_leave_requests(rng, employees, manager_lookup, DEFAULT_LEAVE_TYPES)
    hcm_configs = build_hcm_configs()
    script_runs = build_script_runs()
    audit_events = build_audit_events(rng, leave_requests)
    mock_hcm_state = build_mock_hcm_state(rng, users, leave_balances, leave_requests)

    write_csv(output_dir / "users.csv", [asdict(row) for row in users])
    write_csv(output_dir / "leave_balances.csv", [asdict(row) for row in leave_balances])
    write_csv(output_dir / "leave_requests.csv", [asdict(row) for row in leave_requests])
    write_csv(output_dir / "hcm_configs.csv", [asdict(row) for row in hcm_configs])
    write_csv(output_dir / "script_runs.csv", [asdict(row) for row in script_runs])
    write_csv(output_dir / "audit_events.csv", [asdict(row) for row in audit_events])
    write_json(output_dir / "mock_hcm_state.json", mock_hcm_state)

    summary = {
        "seed": args.seed,
        "users": len(users),
        "admins": len(admins),
        "managers": len(managers),
        "employees": len(employees),
        "leave_balances": len(leave_balances),
        "leave_requests": len(leave_requests),
        "hcm_configs": len(hcm_configs),
        "script_runs": len(script_runs),
        "audit_events": len(audit_events),
        "output_dir": str(output_dir),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())