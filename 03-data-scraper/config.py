from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ScraperSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_key: str = ""  # SCRAPER_API_KEY
    database_url: str = "sqlite:///./scraper.db"
    request_timeout: int = 30
    max_retries: int = 3
    request_interval: float = 1.5
    proxy_url: str = ""
