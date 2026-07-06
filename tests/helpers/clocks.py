from __future__ import annotations

from datetime import datetime, timedelta


def fixed_now(iso: str = "2026-07-05T12:00:00+00:00") -> datetime:
    return datetime.fromisoformat(iso)


def advance_time(current: datetime, seconds: float) -> datetime:
    return current + timedelta(seconds=seconds)
