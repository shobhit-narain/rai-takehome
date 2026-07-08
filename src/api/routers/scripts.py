from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.schemas.scripts import (
    CancelScriptResponse,
    RunScriptRequest,
    ScheduleScriptRequest,
    ScriptRunResponse,
)
from src.app.dependencies import get_scripts_service
from src.auth.dependencies import require_admin
from src.services.scripts_service import ScriptsService

router = APIRouter(
    prefix="/api/v1/scripts", tags=["scripts"], dependencies=[Depends(require_admin)]
)


@router.post("/{name}/run", response_model=ScriptRunResponse)
def run_script(
    name: str,
    payload: RunScriptRequest,
    scripts_service: ScriptsService = Depends(get_scripts_service),
) -> ScriptRunResponse:
    try:
        run = scripts_service.run_script(name, payload.params)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ScriptRunResponse.model_validate(run)


@router.post("/{name}/schedule", response_model=ScriptRunResponse)
def schedule_script(
    name: str,
    payload: ScheduleScriptRequest,
    scripts_service: ScriptsService = Depends(get_scripts_service),
) -> ScriptRunResponse:
    try:
        run = scripts_service.schedule_script(name, payload.cron_expression, payload.params)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ScriptRunResponse.model_validate(run)


@router.get("/runs/{run_id}", response_model=ScriptRunResponse)
def get_script_status(
    run_id: str, scripts_service: ScriptsService = Depends(get_scripts_service)
) -> ScriptRunResponse:
    run = scripts_service.get_status(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="script run not found")
    return ScriptRunResponse.model_validate(run)


@router.post("/runs/{run_id}/cancel", response_model=CancelScriptResponse)
def cancel_script_run(
    run_id: str, scripts_service: ScriptsService = Depends(get_scripts_service)
) -> CancelScriptResponse:
    run = scripts_service.cancel_run(run_id)
    return CancelScriptResponse(id=run.id, cancel_requested=run.cancel_requested)
