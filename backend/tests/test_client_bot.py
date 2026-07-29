"""Pruebas unitarias de la lógica auxiliar del bot del cliente."""

import asyncio
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from app.bot.client_service import format_cart, get_or_create_client
from app.bot.storage import payment_receipt_path, resolve_media_path
from app.core.config import Settings


class ClientBotServiceTests(unittest.TestCase):
    """Comprueba comportamiento sin conectarse a Telegram o PostgreSQL."""

    def test_format_cart_lists_lines_and_total(self) -> None:
        lines = [
            SimpleNamespace(
                cantidad=2,
                nombre_plato="Plato de prueba",
                subtotal=Decimal("25.00"),
            )
        ]
        result = format_cart(lines, Decimal("25.00"))
        self.assertIn("2 × Plato de prueba", result)
        self.assertIn("Total: Bs 25.00", result)

    def test_format_cart_handles_empty_order(self) -> None:
        self.assertEqual(format_cart([], Decimal("0.00")), "Tu carrito está vacío.")

    def test_get_or_create_client_persists_chat_id(self) -> None:
        scalar_result = SimpleNamespace(scalar_one_or_none=lambda: None)
        session = SimpleNamespace(
            execute=AsyncMock(return_value=scalar_result),
            add=Mock(),
            flush=AsyncMock(),
        )
        client = asyncio.run(
            get_or_create_client(
                session,
                chat_id=123456,
                name="  Cliente de prueba  ",
            )
        )
        self.assertEqual(client.chat_id, "123456")
        self.assertEqual(client.nombre, "Cliente de prueba")
        session.add.assert_called_once_with(client)
        session.flush.assert_awaited_once()


class ReceiptStorageTests(unittest.TestCase):
    """Protege el directorio persistente de comprobantes."""

    def test_receipt_reference_has_safe_extension(self) -> None:
        reference = payment_receipt_path(Path("media"), "image/jpeg")
        self.assertEqual(reference.parent, Path("comprobantes"))
        self.assertEqual(reference.suffix, ".jpg")
        self.assertNotIn("..", reference.parts)

    def test_rejects_unsupported_receipt_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "imagen"):
            payment_receipt_path(Path("media"), "application/pdf")

    def test_resolves_reference_inside_media_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = resolve_media_path(
                root,
                Path("comprobantes") / "receipt.jpg",
            )
            self.assertEqual(target.parent, root / "comprobantes")
            self.assertTrue(target.parent.is_dir())

    def test_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "segura"):
                resolve_media_path(Path(directory), Path("..") / "secret.txt")


class BotSettingsTests(unittest.TestCase):
    """Verifica las rutas configurables necesarias en el VPS."""

    def test_media_and_qr_paths_are_read_from_environment(self) -> None:
        settings = Settings(
            database_url="postgresql+psycopg://user:pass@localhost/db",
            jwt_secret="x" * 32,
            telegram_bot_token="telegram-token",
            media_root="private/media",
            payment_qr_path="private/qr.png",
        )
        self.assertEqual(settings.media_root, Path("private/media"))
        self.assertEqual(settings.payment_qr_path, Path("private/qr.png"))

    def test_bot_uses_psycopg_compatible_loop_on_windows(self) -> None:
        source = (
            Path(__file__).resolve().parents[1] / "app" / "bot" / "run.py"
        ).read_text(encoding="utf-8")

        self.assertIn('sys.platform == "win32"', source)
        self.assertIn("loop_factory=asyncio.SelectorEventLoop", source)

    def test_rejected_payment_has_a_client_notification(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "bot"
            / "notifications.py"
        ).read_text(encoding="utf-8")

        self.assertIn('"PAGO_RECHAZADO"', source)
        self.assertIn("Envía una nueva fotografía", source)
