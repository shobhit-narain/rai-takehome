from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from src.domain.enums import LeaveAction, LeaveType


class LeaveBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    location_id: str
    leave_type: str
    num_available: float
    num_ytd_taken: float
    num_limit: float
    external_updated_ts: datetime | None = None
    updated_ts: datetime


class LeaveRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    external_hcm_id: str | None = None
    requestor_id: str
    approver_id: str | None = None
    location_id: str
    leave_type: str
    leave_duration: float
    leave_start: date
    leave_end: date
    status: str
    failure_reason: str | None = None
    version: int
    created_ts: datetime
    updated_ts: datetime
    approved_ts: datetime | None = None
    complete_ts: datetime | None = None
    last_synced_ts: datetime | None = None


class LeaveCreateRequest(BaseModel):
    leave_type: LeaveType
    leave_duration: float
    leave_start: date
    leave_end: date
    location_id: str
    notes: str | None = None


class LeaveUpdateRequest(BaseModel):
    action: LeaveAction
    leave_duration: float | None = None
    leave_start: date | None = None
    leave_end: date | None = None
    notes: str | None = None


class LeaveListResponse(BaseModel):
    items: list[LeaveRequestResponse]


class ManagerLeaveQueryParams(BaseModel):
    status: str | None = None
    limit: int = 50
    offset: int = 0
