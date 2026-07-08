from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class CanonicalBalance(BaseModel):
    user_id: str
    location_id: str
    leave_type: str
    num_available: float
    num_ytd_taken: float
    num_limit: float
    external_updated_ts: datetime | None = None


class BatchBalanceRequest(BaseModel):
    user_ids: list[str]


class CanonicalLeaveCreateRequest(BaseModel):
    user_id: str
    location_id: str
    leave_type: str
    leave_duration: float
    leave_start: date
    leave_end: date
    approver_id: str | None = None
    external_hcm_id: str | None = None


class CanonicalLeaveUpdateRequest(BaseModel):
    external_hcm_id: str
    action: str


class CanonicalLeaveResult(BaseModel):
    status: str
    external_hcm_id: str | None = None
    failure_reason: str | None = None
