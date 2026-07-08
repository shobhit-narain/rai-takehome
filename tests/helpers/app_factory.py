from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.main import create_app


def build_test_app(overrides: dict | None = None) -> FastAPI:
    app = create_app()
    if overrides:
        app.dependency_overrides.update(overrides)
    return app


def build_test_client(overrides: dict | None = None) -> TestClient:
    return TestClient(build_test_app(overrides))
