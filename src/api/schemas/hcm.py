from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MockHcmLeaveCreateRequest(BaseModel):
    user_id: str
    location_id: str
    leave_type: str
    leave_duration: float
    leave_start: str
    leave_end: str
    approver_id: str | None = None
    external_hcm_id: str | None = None
    last_updated_ts: str | None = None


class MockHcmLeaveUpdateRequest(BaseModel):
    action: str


class MockScenarioActivationRequest(BaseModel):
    enabled: bool = Field(default=True)
    params: dict[str, Any] = Field(default_factory=dict)