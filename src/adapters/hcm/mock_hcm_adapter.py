from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


class MockHcmAdapter:
    def __init__(self, state_file: str | Path = "seed_data/mock_hcm_state.json") -> None:
        self.state_file = Path(state_file)
        self._state: dict[str, Any] = self._load_state()

    def reload(self) -> None:
        self._state = self._load_state()

    def get_state(self) -> dict[str, Any]:
        return deepcopy(self._state)

    def save_state(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with self.state_file.open("w", encoding="utf-8") as handle:
            json.dump(self._state, handle, indent=2, sort_keys=True)

    def get_balances(self, user_id: str, location_id: str | None = None) -> list[dict[str, Any]]:
        balances = self._state.get("balances_by_user", {}).get(user_id, [])
        if location_id:
            balances = [row for row in balances if row.get("location_id") == location_id]
        return deepcopy(balances)

    def batch_get_balances(self, user_ids: list[str]) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = {}
        for user_id in user_ids:
            result[user_id] = self.get_balances(user_id)
        return result

    def create_leave(self, payload: dict[str, Any]) -> dict[str, Any]:
        scenarios = self._state.get("scenarios", {})
        if scenarios.get("invalid_dimension", {}).get("enabled"):
            return {
                "status": "rejected",
                "failure_reason": "invalid dimension",
            }

        user_id = payload["user_id"]
        location_id = payload["location_id"]
        leave_type = payload["leave_type"]
        leave_duration = float(payload["leave_duration"])

        balances = self._state.get("balances_by_user", {}).get(user_id, [])
        matching_balance = None
        for row in balances:
            if row["location_id"] == location_id and row["leave_type"] == leave_type:
                matching_balance = row
                break

        if matching_balance is None:
            return {
                "status": "rejected",
                "failure_reason": "balance not found",
            }

        if scenarios.get("insufficient_balance", {}).get("enabled"):
            return {
                "status": "rejected",
                "failure_reason": "insufficient balance",
            }

        if float(matching_balance["num_available"]) < leave_duration:
            return {
                "status": "rejected",
                "failure_reason": "insufficient balance",
            }

        external_id = payload.get("external_hcm_id") or self._next_external_leave_id()

        new_leave = {
            "external_hcm_id": external_id,
            "requestor_id": user_id,
            "approver_id": payload.get("approver_id", ""),
            "location_id": location_id,
            "leave_type": leave_type,
            "leave_duration": leave_duration,
            "leave_start": payload["leave_start"],
            "leave_end": payload["leave_end"],
            "status": "requested",
            "failure_reason": "",
            "last_updated_ts": payload.get("last_updated_ts", ""),
        }

        self._state.setdefault("leaves_by_external_id", {})[external_id] = new_leave

        delayed_consistency = scenarios.get("delayed_consistency", {}).get("enabled", False)
        ambiguous_success = scenarios.get("ambiguous_success", {}).get("enabled", False)

        if not delayed_consistency:
            matching_balance["num_available"] = round(float(matching_balance["num_available"]) - leave_duration, 1)

        self.save_state()

        if ambiguous_success:
            return {
                "status": "pending_reconciliation",
                "external_hcm_id": external_id,
                "failure_reason": "ambiguous upstream confirmation",
            }

        return {
            "status": "requested",
            "external_hcm_id": external_id,
            "failure_reason": "",
        }

    def update_leave(self, external_hcm_id: str, action: str) -> dict[str, Any]:
        leaves = self._state.get("leaves_by_external_id", {})
        leave = leaves.get(external_hcm_id)
        if not leave:
            return {
                "status": "not_found",
                "failure_reason": "external leave not found",
            }

        scenarios = self._state.get("scenarios", {})
        if scenarios.get("ambiguous_success", {}).get("enabled"):
            leave["status"] = "pending_reconciliation"
            self.save_state()
            return {
                "status": "pending_reconciliation",
                "external_hcm_id": external_hcm_id,
                "failure_reason": "ambiguous upstream confirmation",
            }

        if action == "approve":
            leave["status"] = "approved"
        elif action == "deny":
            leave["status"] = "denied"
            leave["failure_reason"] = "manager denied request"
        elif action == "cancel":
            leave["status"] = "canceled"
            leave["failure_reason"] = "request canceled"
        elif action == "complete":
            leave["status"] = "complete"
        elif action == "request_change":
            leave["status"] = "requested"
        else:
            return {
                "status": "rejected",
                "failure_reason": f"unsupported action: {action}",
            }

        self.save_state()
        return {
            "status": leave["status"],
            "external_hcm_id": external_hcm_id,
            "failure_reason": leave.get("failure_reason", ""),
        }

    def activate_scenario(self, scenario_name: str, enabled: bool, params: dict[str, Any] | None = None) -> dict[str, Any]:
        scenarios = self._state.setdefault("scenarios", {})
        if scenario_name not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        scenarios[scenario_name] = {
            "enabled": enabled,
            "params": params or {},
        }
        self.save_state()
        return deepcopy(scenarios[scenario_name])

    def get_leave(self, external_hcm_id: str) -> dict[str, Any] | None:
        leave = self._state.get("leaves_by_external_id", {}).get(external_hcm_id)
        return deepcopy(leave) if leave else None

    def _load_state(self) -> dict[str, Any]:
        if not self.state_file.exists():
            return {
                "metadata": {},
                "scenarios": {
                    "insufficient_balance": {"enabled": False, "params": {}},
                    "invalid_dimension": {"enabled": False, "params": {}},
                    "delayed_consistency": {"enabled": False, "params": {}},
                    "anniversary_refresh": {"enabled": False, "params": {}},
                    "ambiguous_success": {"enabled": False, "params": {}},
                    "intermittent_validation_gap": {"enabled": False, "params": {}},
                },
                "balances_by_user": {},
                "leaves_by_external_id": {},
            }

        with self.state_file.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _next_external_leave_id(self) -> str:
        leaves = self._state.get("leaves_by_external_id", {})
        if not leaves:
            return "hcm_leave_0000001"

        max_num = 0
        for key in leaves.keys():
            try:
                max_num = max(max_num, int(key.split("_")[-1]))
            except ValueError:
                continue
        return f"hcm_leave_{max_num + 1:07d}"