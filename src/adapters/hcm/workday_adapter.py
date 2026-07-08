from __future__ import annotations

from typing import Any


class WorkdayAdapter:
    def get_balances(self, user_id: str, location_id: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError("Workday adapter is not implemented")

    def batch_get_balances(self, user_ids: list[str]) -> dict[str, list[dict[str, Any]]]:
        raise NotImplementedError("Workday adapter is not implemented")

    def create_leave(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Workday adapter is not implemented")

    def update_leave(self, external_hcm_id: str, action: str) -> dict[str, Any]:
        raise NotImplementedError("Workday adapter is not implemented")
