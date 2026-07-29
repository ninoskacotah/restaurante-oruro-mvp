"""Configuración del backend obtenida desde el entorno."""

from typing import Literal

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentSettings(BaseSettings):
    """Reglas compartidas para leer configuración desde el entorno."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DatabaseSettings(EnvironmentSettings):
    """Configuración mínima requerida por la capa de persistencia."""

    database_url: PostgresDsn


class JwtSettings(EnvironmentSettings):
    """Configuración mínima requerida para firmar y validar JWT."""

    jwt_secret: SecretStr = Field(min_length=32)


class Settings(DatabaseSettings, JwtSettings):
    """Valores necesarios para integrar todos los componentes del MVP."""

    app_env: Literal["development", "test", "production"] = "development"
    telegram_bot_token: SecretStr = Field(min_length=1)


def get_database_settings() -> DatabaseSettings:
    """Carga únicamente la configuración requerida por PostgreSQL."""
    return DatabaseSettings()


def get_jwt_settings() -> JwtSettings:
    """Carga únicamente el secreto requerido por el servicio JWT."""
    return JwtSettings()


def get_settings() -> Settings:
    """Carga y valida la configuración cuando una operación la solicita."""
    return Settings()
