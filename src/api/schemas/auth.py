from __future__ import annotations

from pydantic import BaseModel


class AuthenticatedUserResponse(BaseModel):
    user_id: str
    role: str
    manager_id: str | None
    location_id: str
