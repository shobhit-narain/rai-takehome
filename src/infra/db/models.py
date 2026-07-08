from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.db.base import Base


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    manager_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("users.id"), nullable=True)
    location_id: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class LeaveRequestRecord(Base):
    __tablename__ = "leave_requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    external_hcm_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    requestor_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), nullable=False)
    approver_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("users.id"), nullable=True)
    location_id: Mapped[str] = mapped_column(String(64), nullable=False)
    leave_type: Mapped[str] = mapped_column(String(32), nullable=False)
    leave_duration: Mapped[float] = mapped_column(Float, nullable=False)
    leave_start: Mapped[date] = mapped_column(Date, nullable=False)
    leave_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    approved_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    complete_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_synced_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class LeaveBalanceRecord(Base):
    __tablename__ = "leave_balances"
    __table_args__ = (
        UniqueConstraint("user_id", "location_id", "leave_type", name="uq_leave_balance_scope"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), nullable=False)
    location_id: Mapped[str] = mapped_column(String(64), nullable=False)
    leave_type: Mapped[str] = mapped_column(String(32), nullable=False)
    num_available: Mapped[float] = mapped_column(Float, nullable=False)
    num_ytd_taken: Mapped[float] = mapped_column(Float, nullable=False)
    num_limit: Mapped[float] = mapped_column(Float, nullable=False)
    external_updated_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class HcmConfigRecord(Base):
    __tablename__ = "hcm_configs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_type: Mapped[str] = mapped_column(String(64), nullable=False)
    token_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    rate_limit_default: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ScriptRunRecord(Base):
    __tablename__ = "script_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    script_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    schedule_expression: Mapped[str | None] = mapped_column(String(128), nullable=True)
    params_json: Mapped[str] = mapped_column(Text, nullable=False)
    started_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancel_requested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class AuditEventRecord(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_ts: Mapped[datetime] = mapped_column(DateTime, nullable=False)