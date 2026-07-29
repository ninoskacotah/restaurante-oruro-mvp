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
    """Comprueba la cadena de revisiones sin abrir conexiones."""

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

    def test_script_directory_has_expected_revision_chain(self) -> None:
        """Confirma que el historial contiene las revisiones autorizadas."""
        config = Config(ALEMBIC_INI)
        script = ScriptDirectory.from_config(config)
        revisions = list(script.walk_revisions())

        self.assertEqual(len(revisions), 3)
        self.assertEqual(revisions[0].revision, "0003_administradores")
        self.assertEqual(revisions[0].down_revision, "0002_repartidores")
        self.assertEqual(revisions[1].revision, "0002_repartidores")
        self.assertEqual(revisions[1].down_revision, "0001_clientes")
        self.assertEqual(revisions[2].revision, "0001_clientes")
        self.assertIsNone(revisions[2].down_revision)
        self.assertEqual(
            sorted(
                path.name
                for path in VERSIONS_DIRECTORY.iterdir()
                if path.is_file() and path.suffix != ".pyc"
            ),
            [
                ".gitkeep",
                "0001_crear_tabla_clientes.py",
                "0002_crear_tabla_repartidores.py",
                "0003_crear_tabla_administradores.py",
            ],
        )

    def test_heads_command_lists_third_revision(self) -> None:
        """Inspecciona el historial sin necesitar PostgreSQL."""
        result = self.run_alembic("heads")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0003_administradores (head)", result.stdout)

    def test_offline_upgrade_succeeds_without_connection(self) -> None:
        """Genera el SQL de avance con una URL ficticia."""
        result = self.run_alembic("upgrade", "head", "--sql")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CREATE TABLE clientes", result.stdout)
        self.assertIn("CREATE TABLE repartidores", result.stdout)
        self.assertIn("CREATE TABLE administradores", result.stdout)
        self.assertIn("uq_clientes_chat_id", result.stdout)
        self.assertIn("uq_repartidores_chat_id", result.stdout)
        self.assertIn(
            "uq_administradores_nombre_usuario",
            result.stdout,
        )

    def test_offline_downgrade_succeeds_without_connection(self) -> None:
        """Genera el SQL de reversión sin conectarse a PostgreSQL."""
        result = self.run_alembic(
            "downgrade",
            "0003_administradores:0002_repartidores",
            "--sql",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DROP TABLE administradores", result.stdout)
        self.assertNotIn("DROP TABLE repartidores", result.stdout)
        self.assertNotIn("DROP TABLE clientes", result.stdout)

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
