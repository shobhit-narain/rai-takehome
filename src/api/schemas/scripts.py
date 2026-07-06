from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RunScriptRequest(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)


class ScheduleScriptRequest(BaseModel):
    cron_expression: str
    params: dict[str, Any] = Field(default_factory=dict)


class ScriptRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    script_name: str
    status: str
    schedule_expression: str | None = None
    started_ts: datetime | None = None
    finished_ts: datetime | None = None
    cancel_requested: bool
    error_message: str | None = None


class CancelScriptResponse(BaseModel):
    id: str
    cancel_requested: bool
