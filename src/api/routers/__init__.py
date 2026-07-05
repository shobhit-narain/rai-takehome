from src.api.routers.health import router as health_router
from src.api.routers.mock_hcm import router as mock_hcm_router

__all__ = [
    "health_router",
    "mock_hcm_router",
]