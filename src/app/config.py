from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    sqlite_url: str = Field(default="sqlite:///./local.db", alias="SQLITE_URL")
    default_hcm_provider: str = Field(default="mock_hcm", alias="DEFAULT_HCM_PROVIDER")
    enable_response_cache: bool = Field(default=False, alias="ENABLE_RESPONSE_CACHE")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )