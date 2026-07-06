from __future__ import annotations

from typing import Any

from src.adapters.hcm.canonical_models import (
    CanonicalBalance,
    CanonicalLeaveCreateRequest,
    CanonicalLeaveResult,
)


class HcmMapper:
    def to_create_payload(self, request: CanonicalLeaveCreateRequest) -> dict[str, Any]:
        return {
            "user_id": request.user_id,
            "location_id": request.location_id,
            "leave_type": request.leave_type,
            "leave_duration": request.leave_duration,
            "leave_start": request.leave_start.isoformat(),
            "leave_end": request.leave_end.isoformat(),
            "approver_id": request.approver_id,
            "external_hcm_id": request.external_hcm_id,
        }

    def to_update_payload(self, external_hcm_id: str, action: str) -> dict[str, Any]:
        return {"external_hcm_id": external_hcm_id, "action": action}

    def to_canonical_balance(self, raw: dict[str, Any]) -> CanonicalBalance:
        return CanonicalBalance(**raw)

    def to_canonical_leave_result(self, raw: dict[str, Any]) -> CanonicalLeaveResult:
        return CanonicalLeaveResult(
            status=raw.get("status", "unknown"),
            external_hcm_id=raw.get("external_hcm_id") or None,
            failure_reason=raw.get("failure_reason") or None,
        )
