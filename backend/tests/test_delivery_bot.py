"""Pruebas de la lógica auxiliar del bot del repartidor."""

import asyncio
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.bot.delivery_service import (
    DeliverySummary,
    authenticated_courier,
    format_delivery,
)
from app.bot.storage import delivery_evidence_path, resolve_media_path


class DeliveryBotServiceTests(unittest.TestCase):
    """Valida autorización y presentación sin servicios externos."""

    def test_authenticated_courier_uses_persisted_chat(self) -> None:
        courier = SimpleNamespace(id=8, chat_id="555", activo=True)
        result = SimpleNamespace(scalar_one_or_none=lambda: courier)
        session = SimpleNamespace(execute=AsyncMock(return_value=result))
        found = asyncio.run(authenticated_courier(session, 555))
        self.assertIs(found, courier)
        session.execute.assert_awaited_once()

    def test_unknown_courier_is_rejected(self) -> None:
        result = SimpleNamespace(scalar_one_or_none=lambda: None)
        session = SimpleNamespace(execute=AsyncMock(return_value=result))
        found = asyncio.run(authenticated_courier(session, 999))
        self.assertIsNone(found)

    def test_format_delivery_contains_required_operational_data(self) -> None:
        summary = DeliverySummary(
            assignment=SimpleNamespace(id=3),
            order=SimpleNamespace(
                codigo_seguimiento="RET-ABC",
                total=Decimal("45.50"),
                referencia_entrega="Portón azul",
                estado_actual="ASIGNADO",
            ),
            client=SimpleNamespace(
                nombre="Cliente de prueba",
                telefono="70000000",
            ),
            lines=[
                SimpleNamespace(
                    cantidad=2,
                    nombre_plato="Plato de prueba",
                )
            ],
        )
        text = format_delivery(summary)
        for expected in (
            "RET-ABC",
            "2 × Plato de prueba",
            "Bs 45.50",
            "Pago: Confirmado",
            "Cliente de prueba",
            "70000000",
            "Portón azul",
        ):
            self.assertIn(expected, text)


class DeliveryEvidenceStorageTests(unittest.TestCase):
    """Comprueba referencias privadas para evidencias de entrega."""

    def test_delivery_photo_uses_separate_directory(self) -> None:
        reference = delivery_evidence_path(Path("media"), "image/jpeg")
        self.assertEqual(reference.parent, Path("entregas"))
        self.assertEqual(reference.suffix, ".jpg")

    def test_delivery_photo_resolves_inside_media_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = delivery_evidence_path(root, "image/jpeg")
            target = resolve_media_path(root, reference)
            self.assertEqual(target.parent, root / "entregas")
