from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from src.api.schemas.leaves import (
    LeaveCreateRequest,
    LeaveListResponse,
    LeaveRequestResponse,
    LeaveUpdateRequest,
)
from src.app.dependencies import get_balances_service, get_leaves_service
from src.auth.current_user import LoggedInUser
from src.auth.dependencies import require_authenticated_user, require_manager_or_admin
from src.domain.models import LeaveCreateCommand, LeaveUpdateCommand
from src.infra.db.models import LeaveBalanceRecord
from src.services.balances_service import BalancesService
from src.services.leaves_service import LeavesService

router = APIRouter(prefix="/api/v1/leaves", tags=["leaves"])


@router.get("/balance")
def get_balance(
    actor: LoggedInUser = Depends(require_authenticated_user),
    balances_service: BalancesService = Depends(get_balances_service),
) -> dict:
    rows = balances_service.get_user_balances(actor.user_id)
    return {"items": [_balance_to_dict(row) for row in rows]}


@router.get("/current", response_model=LeaveListResponse)
def get_current_leaves(
    actor: LoggedInUser = Depends(require_authenticated_user),
    leaves_service: LeavesService = Depends(get_leaves_service),
) -> LeaveListResponse:
    records = leaves_service.get_current_leaves(actor)
    return LeaveListResponse(items=[LeaveRequestResponse.model_validate(r) for r in records])


@router.post("/request", response_model=LeaveRequestResponse, status_code=201)
def request_leave(
    payload: LeaveCreateRequest,
    actor: LoggedInUser = Depends(require_authenticated_user),
    leaves_service: LeavesService = Depends(get_leaves_service),
) -> LeaveRequestResponse:
    command = LeaveCreateCommand(**payload.model_dump())
    record = leaves_service.request_leave(actor, command)
    return LeaveRequestResponse.model_validate(record)


from src.domain.enums import LeaveStatus

# Non-terminal leave statuses that should appear in manager queue by default
QUEUE_NON_TERMINAL_STATUSES = {
    LeaveStatus.CREATED.value,
    LeaveStatus.REQUESTED.value,
    LeaveStatus.PENDING_RECONCILIATION.value,
}

@router.get("/manager/queue", response_model=LeaveListResponse)
def get_leave_requests(
    status: list[str] | None = Query(default=None),
    include_all: bool = Query(default=False, description="Include all statuses (including approved, denied, canceled, complete)"),
    actor: LoggedInUser = Depends(require_manager_or_admin),
    leaves_service: LeavesService = Depends(get_leaves_service),
) -> LeaveListResponse:
    filters = {"status": status[0]} if status else None
    
    # If not including all statuses and no specific status filter, show only non-terminal statuses
    if not include_all and not status:
        filters = {"status_in": list(QUEUE_NON_TERMINAL_STATUSES)}
    
    records = leaves_service.get_manager_leave_requests(actor, filters)
    return LeaveListResponse(items=[LeaveRequestResponse.model_validate(r) for r in records])


@router.post("/{leave_id}/update", response_model=LeaveRequestResponse)
def update_leave_request(
    leave_id: str,
    payload: LeaveUpdateRequest,
    actor: LoggedInUser = Depends(require_authenticated_user),
    leaves_service: LeavesService = Depends(get_leaves_service),
) -> LeaveRequestResponse:
    command = LeaveUpdateCommand(**payload.model_dump())
    record = leaves_service.update_leave_request(actor, leave_id, command)
    return LeaveRequestResponse.model_validate(record)


def _balance_to_dict(row: LeaveBalanceRecord) -> dict:
    return {
        "user_id": row.user_id,
        "location_id": row.location_id,
        "leave_type": row.leave_type,
        "num_available": row.num_available,
        "num_ytd_taken": row.num_ytd_taken,
        "num_limit": row.num_limit,
        "external_updated_ts": row.external_updated_ts.isoformat() if row.external_updated_ts else None,
        "updated_ts": row.updated_ts.isoformat(),
    }
