from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.adapters.hcm.mock_hcm_adapter import MockHcmAdapter
from src.api.routers import mock_hcm as mock_hcm_module
from src.app.main import create_app
from tests.helpers.mock_hcm import build_mock_hcm_state, write_mock_hcm_state


@pytest.fixture
def mock_hcm_state_payload() -> dict:
    return build_mock_hcm_state()


@pytest.fixture
def mock_hcm_state_file(tmp_path: Path, mock_hcm_state_payload: dict) -> Path:
    return write_mock_hcm_state(tmp_path / "mock_hcm_state.json", mock_hcm_state_payload)


@pytest.fixture
def mock_hcm_adapter(mock_hcm_state_file: Path) -> MockHcmAdapter:
    return MockHcmAdapter(state_file=mock_hcm_state_file)


@pytest.fixture
def app(mock_hcm_adapter: MockHcmAdapter):
    mock_hcm_module.adapter = mock_hcm_adapter
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client