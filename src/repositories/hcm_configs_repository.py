from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infra.db.models import HcmConfigRecord


class HcmConfigsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_active_config(self, provider_name: str) -> HcmConfigRecord | None:
        stmt = select(HcmConfigRecord).where(
            HcmConfigRecord.provider_name == provider_name,
            HcmConfigRecord.is_active.is_(True),
        )
        return self.session.scalars(stmt).first()

    def list_active_configs(self) -> list[HcmConfigRecord]:
        stmt = select(HcmConfigRecord).where(HcmConfigRecord.is_active.is_(True))
        return list(self.session.scalars(stmt).all())
