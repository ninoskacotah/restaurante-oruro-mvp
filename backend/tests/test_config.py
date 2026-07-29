"""Pruebas de la configuración obtenida desde el entorno."""

import importlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from app.core.config import JwtSettings, Settings


class SettingsTest(unittest.TestCase):
    """Comprueba la carga explícita y la prioridad del entorno."""

    def test_explicit_values_are_loaded(self) -> None:
        """Valida valores ficticios proporcionados directamente."""
        settings = Settings(
            app_env="test",
            database_url="postgresql://test_user:test_password@localhost/test_db",
            telegram_bot_token="test-telegram-token",
            jwt_secret="test-jwt-secret-with-at-least-32-characters",
            _env_file=None,
        )

        self.assertEqual(settings.app_env, "test")
        self.assertEqual(
            str(settings.database_url),
            "postgresql://test_user:test_password@localhost/test_db",
        )
        self.assertEqual(
            settings.telegram_bot_token.get_secret_value(),
            "test-telegram-token",
        )
        self.assertEqual(
            settings.jwt_secret.get_secret_value(),
            "test-jwt-secret-with-at-least-32-characters",
        )

    def test_environment_has_priority_over_dotenv_file(self) -> None:
        """Confirma que el sistema reemplaza el valor escrito en .env."""
        with tempfile.TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text(
                "\n".join(
                    [
                        "APP_ENV=development",
                        "DATABASE_URL=postgresql://file_user:file_password@localhost/file_db",
                        "TELEGRAM_BOT_TOKEN=file-telegram-token",
                        "JWT_SECRET=file-jwt-secret-with-at-least-32-characters",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {"APP_ENV": "production"}, clear=True):
                settings = Settings(_env_file=env_file)

        self.assertEqual(settings.app_env, "production")

    def test_main_import_does_not_require_settings(self) -> None:
        """Importa FastAPI sin variables ni conexiones externas."""
        with patch.dict(os.environ, {}, clear=True):
            module = importlib.import_module("app.main")

        self.assertIsNotNone(module.app)

    def test_jwt_settings_do_not_require_other_services(self) -> None:
        """Carga el secreto sin exigir PostgreSQL ni Telegram."""
        with patch.dict(
            os.environ,
            {"JWT_SECRET": "s" * 32},
            clear=True,
        ):
            settings = JwtSettings(_env_file=None)

        self.assertEqual(settings.jwt_secret.get_secret_value(), "s" * 32)

    def test_jwt_secret_rejects_short_values(self) -> None:
        """Hace explícito el mínimo aprobado para la clave de firma."""
        with self.assertRaises(ValidationError):
            JwtSettings(jwt_secret="secreto-corto", _env_file=None)


if __name__ == "__main__":
    unittest.main()
