from __future__ import annotations

from fastapi import FastAPI

from src.api.routers.health import router as health_router
from src.api.routers.mock_hcm import router as mock_hcm_router


def create_app() -> FastAPI:
    app = FastAPI(title="Time-Off Microservice")
    app.include_router(health_router)
    app.include_router(mock_hcm_router)
    return app


app = create_app()