"""Pruebas de clientes, archivos privados y reportes administrativos."""

import asyncio
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi import HTTPException

from app.api.routes.panel import _safe_media_file
from app.main import app
from app.services.reportes import (
    average_delivery_minutes,
    daily_sales,
    popular_dishes,
)


class PanelOpenApiTests(unittest.TestCase):
    """Comprueba que el panel dispone de contratos públicos."""

    def test_panel_paths_are_documented(self) -> None:
        paths = app.openapi()["paths"]
        for path in (
            "/api/clientes",
            "/api/clientes/{cliente_id}",
            "/api/comprobantes/{comprobante_id}/archivo",
            "/api/reportes",
            "/api/repartidores",
            "/api/repartidores/{repartidor_id}",
        ):
            self.assertIn(path, paths)

    def test_courier_management_methods_are_documented(self) -> None:
        paths = app.openapi()["paths"]

        self.assertIn("post", paths["/api/repartidores"])
        self.assertIn("put", paths["/api/repartidores/{repartidor_id}"])
        self.assertIn("delete", paths["/api/repartidores/{repartidor_id}"])


class PrivateMediaTests(unittest.TestCase):
    """Impide exponer archivos fuera del directorio configurado."""

    def test_resolves_existing_file_inside_media_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "comprobantes" / "pago.jpg"
            target.parent.mkdir()
            target.write_bytes(b"photo")

            result = _safe_media_file(root, "comprobantes/pago.jpg")

            self.assertEqual(result, target)

    def test_rejects_path_outside_media_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(HTTPException) as captured:
                _safe_media_file(Path(directory), "../secret.txt")
            self.assertEqual(captured.exception.status_code, 404)


class ReportServiceTests(unittest.IsolatedAsyncioTestCase):
    """Contrasta cálculos con resultados controlados de persistencia."""

    async def test_daily_sales_returns_total_and_count(self) -> None:
        result = SimpleNamespace(one=lambda: (Decimal("125.50"), 3))
        session = SimpleNamespace(execute=AsyncMock(return_value=result))

        total, count = await daily_sales(session, date(2026, 7, 29))

        self.assertEqual(total, Decimal("125.50"))
        self.assertEqual(count, 3)

    async def test_popular_dishes_preserves_database_ranking(self) -> None:
        result = SimpleNamespace(
            all=lambda: [
                (4, "Plato A", 8),
                (2, "Plato B", 3),
            ]
        )
        session = SimpleNamespace(execute=AsyncMock(return_value=result))

        dishes = await popular_dishes(session, date(2026, 7, 29))

        self.assertEqual(dishes[0], (4, "Plato A", 8))
        self.assertEqual(dishes[1][2], 3)

    async def test_average_delivery_uses_complete_pairs(self) -> None:
        start = datetime(2026, 7, 29, 12, 0, tzinfo=timezone.utc)
        events = [
            SimpleNamespace(
                pedido_id=1,
                estado_nuevo="EN_CAMINO",
                fecha_registro=start,
            ),
            SimpleNamespace(
                pedido_id=1,
                estado_nuevo="ENTREGADO",
                fecha_registro=start + timedelta(minutes=35),
            ),
            SimpleNamespace(
                pedido_id=2,
                estado_nuevo="EN_CAMINO",
                fecha_registro=start,
            ),
        ]
        result = SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: events)
        )
        session = SimpleNamespace(execute=AsyncMock(return_value=result))

        average = await average_delivery_minutes(
            session,
            date(2026, 7, 29),
        )

        self.assertEqual(average, Decimal("35.00"))

    async def test_average_delivery_is_none_without_complete_orders(self) -> None:
        result = SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: [])
        )
        session = SimpleNamespace(execute=AsyncMock(return_value=result))

        average = await average_delivery_minutes(
            session,
            date(2026, 7, 29),
        )

        self.assertIsNone(average)
