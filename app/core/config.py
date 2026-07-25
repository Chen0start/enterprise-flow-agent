from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "EnterpriseFlow Agent"
    app_version: str = "0.1.0"
    environment: str = "development"

    database_url: str = (
        "postgresql+psycopg://enterprise_flow_user:change_me@localhost:5432/enterprise_flow"
    )

    test_database_url: str = (
        "postgresql+psycopg://enterprise_flow_user:change_me@localhost:5432/enterprise_flow_test"
    )

    jwt_secret_key: SecretStr = SecretStr("change_me")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings instance."""

    return Settings()
