from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from src.adapters.hcm.mock_hcm_adapter import MockHcmAdapter
from src.api.schemas.hcm import (
    MockHcmLeaveCreateRequest,
    MockHcmLeaveUpdateRequest,
    MockScenarioActivationRequest,
)

router = APIRouter(prefix="/api/v1/mock-hcm", tags=["mock-hcm"])

adapter = MockHcmAdapter()


@router.get("/balances/{user_id}")
def get_mock_balances(user_id: str, location_id: str | None = None) -> dict:
    balances = adapter.get_balances(user_id=user_id, location_id=location_id)
    return {"items": balances}


@router.get("/leaves/{external_hcm_id}")
def get_mock_leave(external_hcm_id: str) -> dict:
    leave = adapter.get_leave(external_hcm_id)
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mock HCM leave not found",
        )
    return leave


@router.post("/leaves", status_code=status.HTTP_201_CREATED)
def create_mock_leave(payload: MockHcmLeaveCreateRequest) -> dict:
    result = adapter.create_leave(payload.model_dump())

    if result["status"] == "rejected":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=result["failure_reason"],
        )

    if result["status"] == "pending_reconciliation":
        return result

    return result


@router.post("/leaves/{external_hcm_id}/update")
def update_mock_leave(external_hcm_id: str, payload: MockHcmLeaveUpdateRequest) -> dict:
    result = adapter.update_leave(external_hcm_id=external_hcm_id, action=payload.action)

    if result["status"] == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["failure_reason"],
        )

    if result["status"] == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["failure_reason"],
        )

    return result


@router.post("/scenarios/{scenario_name}")
def activate_mock_scenario(scenario_name: str, payload: MockScenarioActivationRequest) -> dict:
    try:
        scenario = adapter.activate_scenario(
            scenario_name=scenario_name,
            enabled=payload.enabled,
            params=payload.params,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return {
        "scenario_name": scenario_name,
        "enabled": scenario["enabled"],
        "params": scenario["params"],
    }


@router.post("/reload")
def reload_mock_state() -> dict:
    adapter.reload()
    state = adapter.get_state()
    return {
        "status": "reloaded",
        "metadata": state.get("metadata", {}),
    }


@router.get("/state")
def get_mock_state() -> dict:
    return adapter.get_state()