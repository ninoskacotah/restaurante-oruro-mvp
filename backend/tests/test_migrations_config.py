"""Pruebas de la configuración inicial de Alembic."""

import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.core.config import DatabaseSettings


BACKEND_DIRECTORY = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_DIRECTORY / "alembic.ini"
VERSIONS_DIRECTORY = BACKEND_DIRECTORY / "alembic" / "versions"
FAKE_DATABASE_URL = (
    "postgresql+psycopg://test_user:test_password@localhost/test_db"
)


class AlembicConfigTest(unittest.TestCase):
    """Comprueba Alembic sin crear revisiones ni abrir conexiones."""

    def test_ini_has_script_location_without_database_url(self) -> None:
        """Evita almacenar la conexión en el archivo versionado."""
        config = Config(ALEMBIC_INI)

        self.assertEqual(config.get_main_option("script_location"), "alembic")
        self.assertIsNone(config.get_main_option("sqlalchemy.url"))

    def test_database_settings_do_not_require_other_secrets(self) -> None:
        """Carga solo PostgreSQL sin exigir Telegram o JWT."""
        with patch.dict(
            os.environ,
            {"DATABASE_URL": FAKE_DATABASE_URL},
            clear=True,
        ):
            settings = DatabaseSettings(_env_file=None)

        self.assertEqual(str(settings.database_url), FAKE_DATABASE_URL)

    def test_script_directory_has_no_revisions(self) -> None:
        """Confirma que el historial todavía no contiene migraciones."""
        config = Config(ALEMBIC_INI)
        script = ScriptDirectory.from_config(config)

        self.assertEqual(list(script.walk_revisions()), [])
        self.assertEqual(
            sorted(path.name for path in VERSIONS_DIRECTORY.iterdir()),
            [".gitkeep"],
        )

    def test_heads_command_succeeds_without_revisions(self) -> None:
        """Inspecciona el historial sin necesitar PostgreSQL."""
        result = self.run_alembic("heads")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")

    def test_offline_upgrade_succeeds_without_connection(self) -> None:
        """Ejecuta el entorno offline con una URL ficticia."""
        result = self.run_alembic("upgrade", "head", "--sql")

        self.assertEqual(result.returncode, 0, result.stderr)

    def run_alembic(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        """Ejecuta Alembic con un entorno mínimo y controlado."""
        environment = os.environ.copy()
        environment.pop("TELEGRAM_BOT_TOKEN", None)
        environment.pop("JWT_SECRET", None)
        environment["DATABASE_URL"] = FAKE_DATABASE_URL

        return subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                "alembic.ini",
                *arguments,
            ],
            cwd=BACKEND_DIRECTORY,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
