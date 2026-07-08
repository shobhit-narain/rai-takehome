from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
def get_health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
def get_readiness() -> dict:
    return {"status": "ready"}
