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

    def test_windows_migrations_select_a_psycopg_compatible_loop(self) -> None:
        """Evita reintroducir ProactorEventLoop en la ejecución local."""
        source = (BACKEND_DIRECTORY / "alembic" / "env.py").read_text(
            encoding="utf-8"
        )

        self.assertIn('sys.platform == "win32"', source)
        self.assertIn("loop_factory=asyncio.SelectorEventLoop", source)

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

        self.assertEqual(len(revisions), 15)
        expected_chain = [
            ("0015_pedido_menu", "0014_historial_estados"),
            ("0014_historial_estados", "0013_evidencias_entrega"),
            ("0013_evidencias_entrega", "0012_ubicaciones_trayecto"),
            ("0012_ubicaciones_trayecto", "0011_asignaciones"),
            ("0011_asignaciones", "0010_comprobantes_pago"),
            ("0010_comprobantes_pago", "0009_detalles_pedido"),
            ("0009_detalles_pedido", "0008_pedidos"),
            ("0008_pedidos", "0007_detalles_menu"),
            ("0007_detalles_menu", "0006_menus"),
            ("0006_menus", "0005_platos"),
            ("0005_platos", "0004_tokens_revocados"),
            ("0004_tokens_revocados", "0003_administradores"),
            ("0003_administradores", "0002_repartidores"),
            ("0002_repartidores", "0001_clientes"),
            ("0001_clientes", None),
        ]
        self.assertEqual(
            [
                (revision.revision, revision.down_revision)
                for revision in revisions
            ],
            expected_chain,
        )
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
                "0004_crear_tabla_tokens_revocados.py",
                "0005_crear_tabla_platos.py",
                "0006_crear_tabla_menus.py",
                "0007_crear_tabla_detalles_menu.py",
                "0008_crear_tabla_pedidos.py",
                "0009_crear_tabla_detalles_pedido.py",
                "0010_crear_tabla_comprobantes_pago.py",
                "0011_crear_tabla_asignaciones.py",
                "0012_crear_tabla_ubicaciones_trayecto.py",
                "0013_crear_tabla_evidencias_entrega.py",
                "0014_crear_tabla_historial_estados.py",
                "0015_vincular_pedido_menu.py",
            ],
        )

    def test_heads_command_lists_fifteenth_revision(self) -> None:
        """Inspecciona el historial sin necesitar PostgreSQL."""
        result = self.run_alembic("heads")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0015_pedido_menu (head)", result.stdout)

    def test_offline_upgrade_succeeds_without_connection(self) -> None:
        """Genera el SQL de avance con una URL ficticia."""
        result = self.run_alembic("upgrade", "head", "--sql")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CREATE TABLE clientes", result.stdout)
        self.assertIn("CREATE TABLE repartidores", result.stdout)
        self.assertIn("CREATE TABLE administradores", result.stdout)
        self.assertIn("CREATE TABLE tokens_revocados", result.stdout)
        self.assertIn("CREATE TABLE platos", result.stdout)
        self.assertIn("CREATE TABLE menus", result.stdout)
        self.assertIn("CREATE TABLE detalles_menu", result.stdout)
        self.assertIn("CREATE TABLE pedidos", result.stdout)
        self.assertIn("CREATE TABLE detalles_pedido", result.stdout)
        self.assertIn("CREATE TABLE comprobantes_pago", result.stdout)
        self.assertIn("CREATE TABLE asignaciones", result.stdout)
        self.assertIn("CREATE TABLE ubicaciones_trayecto", result.stdout)
        self.assertIn("CREATE TABLE evidencias_entrega", result.stdout)
        self.assertIn("CREATE TABLE historial_estados", result.stdout)
        self.assertIn("ADD COLUMN menu_id", result.stdout)
        self.assertIn("fk_pedidos_menu_id_menus", result.stdout)
        self.assertIn("uq_clientes_chat_id", result.stdout)
        self.assertIn("uq_repartidores_chat_id", result.stdout)
        self.assertIn(
            "uq_administradores_nombre_usuario",
            result.stdout,
        )
        self.assertIn("uq_tokens_revocados_jti", result.stdout)
        self.assertIn("ck_platos_precio", result.stdout)
        self.assertIn("uq_menus_fecha", result.stdout)
        self.assertIn("uq_detalles_menu_menu_id", result.stdout)
        self.assertIn("ck_detalles_menu_stock", result.stdout)
        self.assertIn("uq_pedidos_codigo_seguimiento", result.stdout)
        self.assertIn("ck_pedidos_total", result.stdout)
        self.assertIn(
            "ck_detalles_pedido_precio_unitario",
            result.stdout,
        )
        self.assertIn("ck_detalles_pedido_cantidad", result.stdout)
        self.assertIn("ck_detalles_pedido_subtotal", result.stdout)
        self.assertIn(
            "ck_comprobantes_pago_tamanio_bytes",
            result.stdout,
        )
        self.assertIn(
            "CREATE UNIQUE INDEX uq_asignaciones_pedido_activa",
            result.stdout,
        )
        self.assertIn(
            "ck_evidencias_entrega_tamanio_bytes",
            result.stdout,
        )
        self.assertIn("ck_historial_estados_un_actor", result.stdout)

    def test_offline_downgrade_succeeds_without_connection(self) -> None:
        """Genera el SQL de reversión sin conectarse a PostgreSQL."""
        result = self.run_alembic(
            "downgrade",
            "0015_pedido_menu:0014_historial_estados",
            "--sql",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DROP COLUMN menu_id", result.stdout)
        self.assertNotIn("DROP TABLE historial_estados", result.stdout)
        self.assertNotIn("DROP TABLE comprobantes_pago", result.stdout)
        self.assertNotIn("DROP TABLE detalles_pedido", result.stdout)
        self.assertNotIn("DROP TABLE pedidos", result.stdout)
        self.assertNotIn("DROP TABLE detalles_menu", result.stdout)
        self.assertNotIn("DROP TABLE menus", result.stdout)
        self.assertNotIn("DROP TABLE platos", result.stdout)
        self.assertNotIn("DROP TABLE tokens_revocados", result.stdout)
        self.assertNotIn("DROP TABLE administradores", result.stdout)
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
