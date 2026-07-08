from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from src.domain.enums import LeaveAction, LeaveStatus, LeaveType, ScriptRunStatus


class LeaveBalanceDomainModel(BaseModel):
    user_id: str
    location_id: str
    leave_type: LeaveType
    num_available: float
    num_ytd_taken: float
    num_limit: float
    external_updated_ts: datetime | None = None
    updated_ts: datetime


class LeaveRequestDomainModel(BaseModel):
    id: str
    external_hcm_id: str | None = None
    requestor_id: str
    approver_id: str | None = None
    location_id: str
    leave_type: LeaveType
    leave_duration: float
    leave_start: date
    leave_end: date
    status: LeaveStatus
    failure_reason: str | None = None
    version: int
    created_ts: datetime
    updated_ts: datetime
    approved_ts: datetime | None = None
    complete_ts: datetime | None = None
    last_synced_ts: datetime | None = None


class LeaveCreateCommand(BaseModel):
    leave_type: LeaveType
    leave_duration: float
    leave_start: date
    leave_end: date
    location_id: str
    notes: str | None = None


class LeaveUpdateCommand(BaseModel):
    action: LeaveAction
    leave_duration: float | None = None
    leave_start: date | None = None
    leave_end: date | None = None
    notes: str | None = None
    mitigating_circumstances: str | None = None


class ScriptRunDomainModel(BaseModel):
    id: str
    script_name: str
    status: ScriptRunStatus
    schedule_expression: str | None = None
    params: dict
    started_ts: datetime | None = None
    finished_ts: datetime | None = None
    cancel_requested: bool = False
    error_message: str | None = None
