#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        from src.infra.db.seed import SeedService
        from src.infra.db.session import build_engine, get_session_factory
        from src.app.config import AppSettings
    except ImportError as exc:
        print(f"Import error: {exc}")
        print("Make sure dependencies are installed and the project structure is in place.")
        return 1

    settings = AppSettings()
    engine = build_engine(settings.sqlite_url)
    session_factory = get_session_factory(engine)

    seed_service = SeedService(session_factory=session_factory)
    seed_service.seed_all()

    print("Local database seeded successfully.")
    print(f"SQLite URL: {settings.sqlite_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())