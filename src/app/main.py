from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routers.health import router as health_router
from src.api.routers.leaves import router as leaves_router
from src.api.routers.mock_hcm import router as mock_hcm_router
from src.api.routers.scripts import router as scripts_router
from src.app.middleware import RequestIdMiddleware, get_request_id
from src.auth.exceptions import AuthError, ForbiddenRoleError
from src.domain.errors import (
    InsufficientBalanceError,
    InvalidStateTransitionError,
    PolicyViolationError,
    ReconciliationRequiredError,
)
from src.repositories.leave_requests_repository import ConflictVersionError


def create_app() -> FastAPI:
    app = FastAPI(title="Time-Off Microservice")
    app.add_middleware(RequestIdMiddleware)
    app.include_router(health_router)
    app.include_router(leaves_router)
    app.include_router(scripts_router)
    app.include_router(mock_hcm_router)
    _register_exception_handlers(app)
    return app


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "details": {},
            "request_id": get_request_id(),
        },
    )


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ForbiddenRoleError)
    async def _forbidden_handler(request: Request, exc: ForbiddenRoleError) -> JSONResponse:
        return _error_response(403, "ACCESS_DENIED", str(exc))

    @app.exception_handler(AuthError)
    async def _auth_handler(request: Request, exc: AuthError) -> JSONResponse:
        return _error_response(exc.status_code, "AUTH_REQUIRED", str(exc))

    @app.exception_handler(PolicyViolationError)
    async def _policy_handler(request: Request, exc: PolicyViolationError) -> JSONResponse:
        return _error_response(403, "ACCESS_DENIED", str(exc))

    @app.exception_handler(InvalidStateTransitionError)
    async def _state_handler(request: Request, exc: InvalidStateTransitionError) -> JSONResponse:
        return _error_response(409, "INVALID_STATE_TRANSITION", str(exc))

    @app.exception_handler(InsufficientBalanceError)
    async def _balance_handler(request: Request, exc: InsufficientBalanceError) -> JSONResponse:
        return _error_response(409, "INSUFFICIENT_BALANCE", str(exc))

    @app.exception_handler(ReconciliationRequiredError)
    async def _reconciliation_handler(
        request: Request, exc: ReconciliationRequiredError
    ) -> JSONResponse:
        return _error_response(202, "RECONCILIATION_REQUIRED", str(exc))

    @app.exception_handler(ConflictVersionError)
    async def _conflict_handler(request: Request, exc: ConflictVersionError) -> JSONResponse:
        return _error_response(409, "CONFLICT", str(exc))


app = create_app()
