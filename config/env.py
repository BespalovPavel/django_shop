from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "production", "testing"] = "development"
    debug: bool = False
    secret_key: SecretStr
    allowed_hosts: list[str] = ["*"]

    database_url: str = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

    email_backend: str = "django.core.mail.backends.console.EmailBackend"
    email_host: str = "localhost"
    email_port: int = 587
    email_host_user: str = ""
    email_host_password: SecretStr = SecretStr("")
    email_use_tls: bool = False
    email_use_ssl: bool = False
    default_from_email: str = "noreply@shop.local"

    access_token_lifetime_minutes: int = 60
    refresh_token_lifetime_days: int = 7

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()


app_settings = get_app_settings()
