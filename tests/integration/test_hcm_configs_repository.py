from __future__ import annotations

from datetime import datetime, timezone

from src.infra.db.models import HcmConfigRecord
from src.repositories.hcm_configs_repository import HcmConfigsRepository


def test_hcm_configs_repository_returns_active_provider_config(db_session) -> None:
    now = datetime.now(timezone.utc)
    db_session.add(
        HcmConfigRecord(
            id="cfg-1",
            provider_name="mock_hcm",
            base_url="https://mock.example.com",
            auth_type="api_key",
            token_ref="mock-token",
            rate_limit_default=100,
            is_active=True,
            created_ts=now,
            updated_ts=now,
        )
    )
    db_session.flush()

    repo = HcmConfigsRepository(db_session)
    config = repo.get_active_config("mock_hcm")
    assert config is not None
    assert config.provider_name == "mock_hcm"
