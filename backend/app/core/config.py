"""Configuración del backend obtenida desde el entorno."""

from typing import Literal

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Configuración mínima requerida por la capa de persistencia."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: PostgresDsn


class Settings(DatabaseSettings):
    """Valores necesarios para integrar todos los componentes del MVP."""

    app_env: Literal["development", "test", "production"] = "development"
    telegram_bot_token: SecretStr = Field(min_length=1)
    jwt_secret: SecretStr = Field(min_length=32)


def get_database_settings() -> DatabaseSettings:
    """Carga únicamente la configuración requerida por PostgreSQL."""
    return DatabaseSettings()


def get_settings() -> Settings:
    """Carga y valida la configuración cuando una operación la solicita."""
    return Settings()
