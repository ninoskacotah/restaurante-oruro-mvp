"""Pruebas de las utilidades para preparar el entorno local."""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app.cli.bootstrap_local import _confirmed_secret, write_environment
from app.cli.create_admin import (
    _password_confirmation,
    run_upsert_administrator,
)


class LocalEnvironmentTests(unittest.TestCase):
    """Comprueba que el archivo local contiene solo datos necesarios."""

    def test_writes_expected_environment_without_postgres_password(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / ".env"
            write_environment(
                destination=destination,
                application_user="restaurant_user",
                application_password="clave con espacios",
                database_name="restaurant_las_retamas",
                telegram_token="replace-after-botfather",
            )

            content = destination.read_text(encoding="utf-8")
            self.assertIn("restaurant_user:clave+con+espacios", content)
            self.assertIn("PAYMENT_QR_PATH=var/payment-qr.png", content)
            self.assertIn("JWT_SECRET=", content)
            self.assertNotIn("postgres_password", content.lower())

    @patch(
        "app.cli.bootstrap_local.getpass",
        side_effect=["secreto-local", "secreto-local"],
    )
    def test_confirms_application_secret(self, _mocked_getpass) -> None:
        self.assertEqual(_confirmed_secret("Contraseña: "), "secreto-local")

    @patch(
        "app.cli.bootstrap_local.getpass",
        side_effect=["primera", "segunda"],
    )
    def test_rejects_different_application_secrets(
        self,
        _mocked_getpass,
    ) -> None:
        with self.assertRaisesRegex(ValueError, "no coinciden"):
            _confirmed_secret("Contraseña: ")


class AdministratorPasswordTests(unittest.TestCase):
    """Valida la captura privada de la credencial administrativa."""

    @patch(
        "app.cli.create_admin.getpass",
        side_effect=["clave-segura", "clave-segura"],
    )
    def test_accepts_confirmed_password(self, _mocked_getpass) -> None:
        self.assertEqual(_password_confirmation(), "clave-segura")

    @patch(
        "app.cli.create_admin.getpass",
        side_effect=["corta", "corta"],
    )
    def test_rejects_short_password(self, _mocked_getpass) -> None:
        with self.assertRaisesRegex(ValueError, "10 caracteres"):
            _password_confirmation()

    @patch("app.cli.create_admin.sys.platform", "win32")
    @patch("app.cli.create_admin.asyncio.Runner")
    @patch(
        "app.cli.create_admin.upsert_administrator",
        new_callable=Mock,
    )
    def test_uses_compatible_loop_on_windows(
        self,
        mocked_upsert,
        mocked_runner,
    ) -> None:
        mocked_runner.return_value.__enter__.return_value.run.return_value = (
            "creado"
        )

        result = run_upsert_administrator("admin_prueba", "clave-segura")

        self.assertEqual(result, "creado")
        self.assertEqual(
            mocked_runner.call_args.kwargs["loop_factory"],
            asyncio.SelectorEventLoop,
        )
        mocked_upsert.assert_called_once_with(
            "admin_prueba",
            "clave-segura",
        )
