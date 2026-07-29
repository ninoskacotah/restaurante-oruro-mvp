"""Pruebas unitarias del servicio asíncrono de catálogo."""

import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Plato
from app.services import (
    ErrorValidacion,
    RecursoNoEncontrado,
    actualizar_plato,
    crear_plato,
    desactivar_plato,
    obtener_plato,
)


class CatalogoServiceTest(unittest.IsolatedAsyncioTestCase):
    """Comprueba reglas del catálogo sin PostgreSQL ni endpoints."""

    def setUp(self) -> None:
        """Prepara una sesión simulada que permite revisar interacciones."""
        self.session = MagicMock(spec=AsyncSession)
        self.session.get = AsyncMock()
        self.session.flush = AsyncMock()
        self.session.commit = AsyncMock()

    async def test_crear_plato_normalizes_values_without_commit(self) -> None:
        """Crea el modelo limpio e inactivo dentro de la unidad de trabajo."""
        plato = await crear_plato(
            self.session,
            nombre="  Sopa del día  ",
            descripcion="  Preparación diaria  ",
            precio=Decimal("12.50"),
        )

        self.assertEqual(plato.nombre, "Sopa del día")
        self.assertEqual(plato.descripcion, "Preparación diaria")
        self.assertEqual(plato.precio, Decimal("12.50"))
        self.assertFalse(plato.activo)
        self.session.add.assert_called_once_with(plato)
        self.session.flush.assert_awaited_once()
        self.session.commit.assert_not_awaited()

    async def test_crear_plato_rejects_empty_name(self) -> None:
        """Impide persistir nombres formados únicamente por espacios."""
        with self.assertRaises(ErrorValidacion):
            await crear_plato(
                self.session,
                nombre="   ",
                descripcion=None,
                precio=Decimal("10.00"),
            )
        self.session.add.assert_not_called()

    async def test_crear_plato_rejects_negative_price(self) -> None:
        """Impide persistir un precio menor que cero."""
        with self.assertRaises(ErrorValidacion):
            await crear_plato(
                self.session,
                nombre="Plato",
                descripcion=None,
                precio=Decimal("-0.01"),
            )
        self.session.add.assert_not_called()

    async def test_obtener_plato_reports_missing_resource(self) -> None:
        """Traduce la ausencia del modelo a un error del servicio."""
        self.session.get.return_value = None

        with self.assertRaises(RecursoNoEncontrado):
            await obtener_plato(self.session, 99)

    async def test_actualizar_plato_replaces_editable_values(self) -> None:
        """Actualiza datos y delega el commit a la unidad de trabajo."""
        plato = Plato(
            id=1,
            nombre="Anterior",
            descripcion=None,
            precio=Decimal("5.00"),
            activo=False,
        )
        self.session.get.return_value = plato

        result = await actualizar_plato(
            self.session,
            1,
            nombre="  Nuevo  ",
            descripcion="  Descripción  ",
            precio=Decimal("8.00"),
            activo=True,
        )

        self.assertIs(result, plato)
        self.assertEqual(plato.nombre, "Nuevo")
        self.assertEqual(plato.descripcion, "Descripción")
        self.assertEqual(plato.precio, Decimal("8.00"))
        self.assertTrue(plato.activo)
        self.session.flush.assert_awaited_once()
        self.session.commit.assert_not_awaited()

    async def test_desactivar_plato_preserves_the_model(self) -> None:
        """Realiza una baja lógica y no elimina el registro."""
        plato = Plato(
            id=1,
            nombre="Plato",
            descripcion=None,
            precio=Decimal("5.00"),
            activo=True,
        )
        self.session.get.return_value = plato

        result = await desactivar_plato(self.session, 1)

        self.assertIs(result, plato)
        self.assertFalse(plato.activo)
        self.session.delete.assert_not_called()
        self.session.commit.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
