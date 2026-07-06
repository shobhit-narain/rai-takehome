from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.adapters.hcm.mock_hcm_adapter import MockHcmAdapter
from src.api.routers import mock_hcm as mock_hcm_module
from src.app.config import AppSettings
from src.app.dependencies import get_db_session as app_get_db_session
from src.app.dependencies import get_hcm_service
from src.app.main import create_app
from src.infra.db.base import Base
from src.infra.db.factories import build_user_record
from src.infra.db.models import UserRecord
from src.infra.db.session import build_engine, get_session_factory
from tests.helpers.mock_hcm import build_mock_hcm_state, write_mock_hcm_state


@pytest.fixture
def db_engine():
    engine = build_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Session:
    session_factory = get_session_factory(db_engine)
    session = session_factory()
    yield session
    session.close()


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


@pytest.fixture
def settings() -> AppSettings:
    return AppSettings()


@pytest.fixture
def employee_user(db_session: Session) -> UserRecord:
    manager = build_user_record(id="user_mgr_0001", role="manager", location_id="loc_us_ca")
    admin = build_user_record(id="user_admin_0001", role="admin", location_id="loc_us_ca")
    employee = build_user_record(
        id="user_emp_00001", role="employee", manager_id="user_mgr_0001", location_id="loc_us_ca"
    )
    db_session.add_all([manager, admin, employee])
    db_session.flush()
    return employee


@pytest.fixture
def manager_user(db_session: Session, employee_user: UserRecord) -> UserRecord:
    return db_session.get(UserRecord, "user_mgr_0001")


@pytest.fixture
def admin_user(db_session: Session, employee_user: UserRecord) -> UserRecord:
    return db_session.get(UserRecord, "user_admin_0001")


@pytest.fixture
def test_app(db_session: Session, mock_hcm_adapter: MockHcmAdapter):
    fastapi_app = create_app()

    def _override_db_session():
        yield db_session

    fastapi_app.dependency_overrides[app_get_db_session] = _override_db_session
    fastapi_app.dependency_overrides[get_hcm_service] = lambda: mock_hcm_adapter
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def test_client(test_app):
    with TestClient(test_app) as client:
        yield client