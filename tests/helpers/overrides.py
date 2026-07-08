from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from src.app.dependencies import get_hcm_service
from src.auth.current_user import LoggedInUser
from src.auth.dependencies import get_logged_in_user


def override_logged_in_user(app: FastAPI, user: LoggedInUser) -> None:
    app.dependency_overrides[get_logged_in_user] = lambda: user


def override_hcm_service(app: FastAPI, hcm_service: Any) -> None:
    app.dependency_overrides[get_hcm_service] = lambda: hcm_service


def clear_dependency_overrides(app: FastAPI) -> None:
    app.dependency_overrides.clear()
