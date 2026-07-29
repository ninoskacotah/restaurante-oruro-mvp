"""Pruebas unitarias del servicio asíncrono de menús."""

import unittest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DetalleMenu, Menu, Plato
from app.services import (
    ConflictoServicio,
    ErrorValidacion,
    RecursoNoEncontrado,
    actualizar_estado_menu,
    actualizar_oferta,
    agregar_plato_al_menu,
    consultar_oferta_disponible,
    obtener_o_crear_menu,
    retirar_plato_del_menu,
)


class MenusServiceTest(unittest.IsolatedAsyncioTestCase):
    """Comprueba la oferta diaria sin base de datos activa."""

    def setUp(self) -> None:
        """Prepara una sesión y un resultado SQL simulados."""
        self.session = MagicMock(spec=AsyncSession)
        self.session.get = AsyncMock()
        self.session.execute = AsyncMock()
        self.session.flush = AsyncMock()
        self.session.commit = AsyncMock()

    async def test_obtener_o_crear_menu_returns_existing(self) -> None:
        """Evita duplicar la fecha cuando el menú ya existe."""
        menu = Menu(id=2, fecha=date(2026, 7, 29), activo=True)
        result = MagicMock()
        result.scalar_one_or_none.return_value = menu
        self.session.execute.return_value = result

        found = await obtener_o_crear_menu(self.session, menu.fecha)

        self.assertIs(found, menu)
        self.session.add.assert_not_called()
        self.session.flush.assert_not_awaited()

    async def test_obtener_o_crear_menu_creates_inactive_offer(self) -> None:
        """Crea una oferta inactiva y deja pendiente el commit."""
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = result

        menu = await obtener_o_crear_menu(
            self.session,
            date(2026, 7, 30),
        )

        self.assertFalse(menu.activo)
        self.session.add.assert_called_once_with(menu)
        self.session.flush.assert_awaited_once()
        self.session.commit.assert_not_awaited()

    async def test_agregar_plato_rejects_duplicate(self) -> None:
        """Informa el conflicto antes de insertar otro detalle."""
        menu = Menu(id=1, fecha=date(2026, 7, 29), activo=False)
        plato = Plato(
            id=2,
            nombre="Plato",
            descripcion=None,
            precio=Decimal("10.00"),
            activo=True,
        )
        self.session.get.side_effect = [menu, plato]
        result = MagicMock()
        result.scalar_one_or_none.return_value = DetalleMenu(
            id=3,
            menu_id=1,
            plato_id=2,
            stock=2,
            disponible=True,
        )
        self.session.execute.return_value = result

        with self.assertRaises(ConflictoServicio):
            await agregar_plato_al_menu(
                self.session,
                menu_id=1,
                plato_id=2,
                stock=3,
            )
        self.session.add.assert_not_called()

    async def test_actualizar_estado_menu_preserves_daily_offer(
        self,
    ) -> None:
        """Activa el menú sin eliminar ni recrear su fecha."""
        menu = Menu(id=1, fecha=date(2026, 7, 29), activo=False)
        self.session.get.return_value = menu

        result = await actualizar_estado_menu(
            self.session,
            1,
            activo=True,
        )

        self.assertIs(result, menu)
        self.assertTrue(menu.activo)
        self.session.flush.assert_awaited_once()
        self.session.commit.assert_not_awaited()

    async def test_agregar_plato_creates_detail_without_commit(self) -> None:
        """Incorpora una combinación nueva con stock validado."""
        menu = Menu(id=1, fecha=date(2026, 7, 29), activo=False)
        plato = Plato(
            id=2,
            nombre="Plato",
            descripcion=None,
            precio=Decimal("10.00"),
            activo=True,
        )
        self.session.get.side_effect = [menu, plato]
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = result

        detalle = await agregar_plato_al_menu(
            self.session,
            menu_id=1,
            plato_id=2,
            stock=4,
            disponible=True,
        )

        self.assertEqual(detalle.stock, 4)
        self.assertTrue(detalle.disponible)
        self.session.add.assert_called_once_with(detalle)
        self.session.flush.assert_awaited_once()
        self.session.commit.assert_not_awaited()

    async def test_agregar_plato_reports_missing_menu(self) -> None:
        """Detiene la operación cuando la oferta no existe."""
        self.session.get.return_value = None

        with self.assertRaises(RecursoNoEncontrado):
            await agregar_plato_al_menu(
                self.session,
                menu_id=99,
                plato_id=2,
                stock=1,
            )

    async def test_actualizar_oferta_rejects_negative_stock(self) -> None:
        """Conserva el detalle cuando el stock propuesto es inválido."""
        detalle = DetalleMenu(
            id=3,
            menu_id=1,
            plato_id=2,
            stock=4,
            disponible=True,
        )
        self.session.get.return_value = detalle

        with self.assertRaises(ErrorValidacion):
            await actualizar_oferta(
                self.session,
                3,
                stock=-1,
                disponible=False,
            )
        self.assertEqual(detalle.stock, 4)
        self.assertTrue(detalle.disponible)

    async def test_retirar_plato_only_changes_availability(self) -> None:
        """Oculta el detalle sin borrarlo ni modificar sus existencias."""
        detalle = DetalleMenu(
            id=3,
            menu_id=1,
            plato_id=2,
            stock=4,
            disponible=True,
        )
        self.session.get.return_value = detalle

        result = await retirar_plato_del_menu(self.session, 3)

        self.assertIs(result, detalle)
        self.assertFalse(detalle.disponible)
        self.assertEqual(detalle.stock, 4)
        self.session.delete.assert_not_called()

    async def test_consultar_oferta_returns_rows_from_filtered_query(
        self,
    ) -> None:
        """Devuelve los pares detalle-plato producidos por la consulta."""
        detalle = DetalleMenu(
            id=3,
            menu_id=1,
            plato_id=2,
            stock=4,
            disponible=True,
        )
        plato = Plato(
            id=2,
            nombre="Plato",
            descripcion=None,
            precio=Decimal("10.00"),
            activo=True,
        )
        result = MagicMock()
        result.tuples.return_value.all.return_value = [(detalle, plato)]
        self.session.execute.return_value = result

        rows = await consultar_oferta_disponible(
            self.session,
            date(2026, 7, 29),
        )

        self.assertEqual(rows, [(detalle, plato)])
        self.session.execute.assert_awaited_once()
        self.session.commit.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
