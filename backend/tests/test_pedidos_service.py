"""Pruebas unitarias del carrito y confirmación de pedidos."""

import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Cliente,
    DetalleMenu,
    DetallePedido,
    HistorialEstado,
    Pedido,
    Plato,
)
from app.services import (
    ConflictoServicio,
    ErrorValidacion,
    RecursoNoEncontrado,
    agregar_plato_al_carrito,
    confirmar_pedido,
    modificar_cantidad_carrito,
    obtener_o_crear_borrador,
    retirar_detalle_carrito,
)


def scalar_result(value: object) -> MagicMock:
    """Construye un resultado simulado con cero o una fila escalar."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def tuple_result(value: object) -> MagicMock:
    """Construye un resultado simulado para una consulta de dos modelos."""
    result = MagicMock()
    result.tuples.return_value.one_or_none.return_value = value
    return result


def list_result(values: list[object]) -> MagicMock:
    """Construye un resultado simulado para una lista de escalares."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


class PedidosServiceTest(unittest.IsolatedAsyncioTestCase):
    """Comprueba el núcleo del pedido sin PostgreSQL activo."""

    def setUp(self) -> None:
        """Prepara una sesión asíncrona observable."""
        self.session = MagicMock(spec=AsyncSession)
        self.session.get = AsyncMock()
        self.session.execute = AsyncMock()
        self.session.flush = AsyncMock()
        self.session.delete = AsyncMock()
        self.session.commit = AsyncMock()

    async def test_obtener_o_crear_borrador_returns_existing(self) -> None:
        """Evita crear otro carrito para el mismo cliente."""
        cliente = Cliente(id=1, chat_id=100)
        pedido = Pedido(
            id=2,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("0.00"),
        )
        self.session.get.return_value = cliente
        self.session.execute.return_value = scalar_result(pedido)

        result = await obtener_o_crear_borrador(self.session, 1)

        self.assertIs(result, pedido)
        self.session.get.assert_awaited_once_with(
            Cliente,
            1,
            with_for_update=True,
        )
        self.session.add.assert_not_called()

    async def test_obtener_o_crear_borrador_creates_one(self) -> None:
        """Crea una cabecera vacía sin confirmar la transacción."""
        self.session.get.return_value = Cliente(id=1, chat_id=100)
        self.session.execute.return_value = scalar_result(None)

        pedido = await obtener_o_crear_borrador(self.session, 1)

        self.assertEqual(pedido.estado_actual, "BORRADOR")
        self.assertEqual(pedido.total, Decimal("0.00"))
        self.session.add.assert_called_once_with(pedido)
        self.session.commit.assert_not_awaited()

    async def test_obtener_borrador_requires_existing_client(self) -> None:
        """Impide crear pedidos para un cliente inexistente."""
        self.session.get.return_value = None

        with self.assertRaises(RecursoNoEncontrado):
            await obtener_o_crear_borrador(self.session, 99)
        self.session.execute.assert_not_awaited()

    async def test_agregar_plato_creates_historical_detail(self) -> None:
        """Copia nombre y precio y actualiza el total del borrador."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("0.00"),
        )
        oferta = DetalleMenu(
            id=10,
            menu_id=4,
            plato_id=2,
            stock=5,
            disponible=True,
        )
        plato = Plato(
            id=2,
            nombre="Sopa",
            descripcion=None,
            precio=Decimal("12.50"),
            activo=True,
        )
        self.session.get.return_value = pedido
        self.session.execute.side_effect = [
            tuple_result((oferta, plato)),
            scalar_result(None),
            list_result(
                [
                    DetallePedido(
                        id=3,
                        pedido_id=1,
                        plato_id=2,
                        nombre_plato="Sopa",
                        precio_unitario=Decimal("12.50"),
                        cantidad=2,
                        subtotal=Decimal("25.00"),
                    )
                ]
            ),
        ]

        detalle = await agregar_plato_al_carrito(
            self.session,
            pedido_id=1,
            detalle_menu_id=10,
            cantidad=2,
        )

        self.assertEqual(detalle.nombre_plato, "Sopa")
        self.assertEqual(detalle.precio_unitario, Decimal("12.50"))
        self.assertEqual(detalle.subtotal, Decimal("25.00"))
        self.assertEqual(pedido.total, Decimal("25.00"))
        self.session.commit.assert_not_awaited()

    async def test_agregar_same_plato_increments_existing_detail(self) -> None:
        """Evita duplicar una línea del mismo plato."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("12.50"),
        )
        oferta = DetalleMenu(
            id=10,
            menu_id=4,
            plato_id=2,
            stock=5,
            disponible=True,
        )
        plato = Plato(
            id=2,
            nombre="Sopa",
            descripcion=None,
            precio=Decimal("12.50"),
            activo=True,
        )
        detalle = DetallePedido(
            id=3,
            pedido_id=1,
            plato_id=2,
            nombre_plato="Sopa",
            precio_unitario=Decimal("12.50"),
            cantidad=1,
            subtotal=Decimal("12.50"),
        )
        self.session.get.return_value = pedido
        self.session.execute.side_effect = [
            tuple_result((oferta, plato)),
            scalar_result(detalle),
            list_result([detalle]),
        ]

        result = await agregar_plato_al_carrito(
            self.session,
            pedido_id=1,
            detalle_menu_id=10,
            cantidad=2,
        )

        self.assertIs(result, detalle)
        self.assertEqual(detalle.cantidad, 3)
        self.assertEqual(detalle.subtotal, Decimal("37.50"))
        self.assertEqual(pedido.total, Decimal("37.50"))

    async def test_agregar_rejects_quantity_above_stock(self) -> None:
        """Conserva el carrito cuando las unidades no están disponibles."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("0.00"),
        )
        oferta = DetalleMenu(
            id=10,
            menu_id=4,
            plato_id=2,
            stock=1,
            disponible=True,
        )
        plato = Plato(
            id=2,
            nombre="Sopa",
            descripcion=None,
            precio=Decimal("12.50"),
            activo=True,
        )
        self.session.get.return_value = pedido
        self.session.execute.side_effect = [
            tuple_result((oferta, plato)),
            scalar_result(None),
        ]

        with self.assertRaises(ConflictoServicio):
            await agregar_plato_al_carrito(
                self.session,
                pedido_id=1,
                detalle_menu_id=10,
                cantidad=2,
            )
        self.session.add.assert_not_called()

    async def test_agregar_rejects_non_positive_quantity(self) -> None:
        """Rechaza la cantidad antes de consultar la oferta."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("0.00"),
        )
        self.session.get.return_value = pedido

        with self.assertRaises(ErrorValidacion):
            await agregar_plato_al_carrito(
                self.session,
                pedido_id=1,
                detalle_menu_id=10,
                cantidad=0,
            )
        self.session.execute.assert_not_awaited()

    async def test_modificar_cantidad_updates_historical_subtotal(
        self,
    ) -> None:
        """Usa el precio guardado y no el precio actual del catálogo."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("10.00"),
        )
        detalle = DetallePedido(
            id=3,
            pedido_id=1,
            plato_id=2,
            nombre_plato="Sopa",
            precio_unitario=Decimal("10.00"),
            cantidad=1,
            subtotal=Decimal("10.00"),
        )
        oferta = DetalleMenu(
            id=10,
            menu_id=4,
            plato_id=2,
            stock=5,
            disponible=True,
        )
        plato = Plato(
            id=2,
            nombre="Sopa nueva",
            descripcion=None,
            precio=Decimal("15.00"),
            activo=True,
        )
        self.session.get.side_effect = [detalle, pedido]
        self.session.execute.side_effect = [
            tuple_result((oferta, plato)),
            list_result([detalle]),
        ]

        result = await modificar_cantidad_carrito(
            self.session,
            detalle_pedido_id=3,
            detalle_menu_id=10,
            cantidad=2,
        )

        self.assertEqual(result.subtotal, Decimal("20.00"))
        self.assertEqual(pedido.total, Decimal("20.00"))

    async def test_retirar_detail_is_limited_to_draft(self) -> None:
        """Impide eliminar contenido después de la confirmación."""
        detalle = DetallePedido(
            id=3,
            pedido_id=1,
            plato_id=2,
            nombre_plato="Sopa",
            precio_unitario=Decimal("10.00"),
            cantidad=1,
            subtotal=Decimal("10.00"),
        )
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="PENDIENTE_UBICACION",
            total=Decimal("10.00"),
        )
        self.session.get.side_effect = [detalle, pedido]

        with self.assertRaises(ConflictoServicio):
            await retirar_detalle_carrito(self.session, 3)
        self.session.delete.assert_not_awaited()

    async def test_confirmar_rejects_empty_cart(self) -> None:
        """No genera código ni historial para un carrito vacío."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("0.00"),
        )
        self.session.get.return_value = pedido
        self.session.execute.return_value = list_result([])

        with self.assertRaises(ErrorValidacion):
            await confirmar_pedido(
                self.session,
                pedido_id=1,
                menu_id=4,
            )
        self.session.add.assert_not_called()

    async def test_confirmar_validates_all_rows_before_discount(self) -> None:
        """Evita un descuento parcial si falla el segundo plato."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("20.00"),
        )
        first = DetallePedido(
            id=3,
            pedido_id=1,
            plato_id=2,
            nombre_plato="Sopa",
            precio_unitario=Decimal("10.00"),
            cantidad=1,
            subtotal=Decimal("10.00"),
        )
        second = DetallePedido(
            id=4,
            pedido_id=1,
            plato_id=3,
            nombre_plato="Segundo",
            precio_unitario=Decimal("10.00"),
            cantidad=1,
            subtotal=Decimal("10.00"),
        )
        first_offer = DetalleMenu(
            id=10,
            menu_id=4,
            plato_id=2,
            stock=3,
            disponible=True,
        )
        self.session.get.return_value = pedido
        self.session.execute.side_effect = [
            list_result([first, second]),
            scalar_result(first_offer),
            scalar_result(None),
        ]

        with self.assertRaises(ConflictoServicio):
            await confirmar_pedido(
                self.session,
                pedido_id=1,
                menu_id=4,
            )

        self.assertEqual(first_offer.stock, 3)
        self.assertEqual(pedido.estado_actual, "BORRADOR")
        self.assertIsNone(pedido.codigo_seguimiento)

    async def test_confirmar_discounts_and_records_transition(self) -> None:
        """Completa una confirmación correcta una sola vez."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("0.00"),
        )
        detalle = DetallePedido(
            id=3,
            pedido_id=1,
            plato_id=2,
            nombre_plato="Sopa",
            precio_unitario=Decimal("10.00"),
            cantidad=2,
            subtotal=Decimal("20.00"),
        )
        oferta = DetalleMenu(
            id=10,
            menu_id=4,
            plato_id=2,
            stock=2,
            disponible=True,
        )
        self.session.get.return_value = pedido
        self.session.execute.side_effect = [
            list_result([detalle]),
            scalar_result(oferta),
            scalar_result(None),
        ]

        result = await confirmar_pedido(
            self.session,
            pedido_id=1,
            menu_id=4,
            generador_codigo=lambda: "RET-PRUEBA",
        )

        self.assertIs(result, pedido)
        self.assertEqual(pedido.total, Decimal("20.00"))
        self.assertEqual(pedido.codigo_seguimiento, "RET-PRUEBA")
        self.assertEqual(pedido.menu_id, 4)
        self.assertEqual(pedido.estado_actual, "PENDIENTE_UBICACION")
        self.assertEqual(oferta.stock, 0)
        self.assertFalse(oferta.disponible)
        history = [
            call.args[0]
            for call in self.session.add.call_args_list
            if isinstance(call.args[0], HistorialEstado)
        ]
        self.assertEqual(len(history), 1)
        self.session.commit.assert_not_awaited()

    async def test_confirmar_is_idempotent_after_success(self) -> None:
        """Devuelve el pedido existente sin volver a consultar el stock."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="PENDIENTE_UBICACION",
            total=Decimal("20.00"),
            codigo_seguimiento="RET-EXISTENTE",
        )
        self.session.get.return_value = pedido

        result = await confirmar_pedido(
            self.session,
            pedido_id=1,
            menu_id=4,
        )

        self.assertIs(result, pedido)
        self.session.execute.assert_not_awaited()
        self.session.add.assert_not_called()
        self.session.flush.assert_not_awaited()

    async def test_confirmar_retries_a_duplicated_tracking_code(
        self,
    ) -> None:
        """Descarta un candidato existente antes de descontar stock."""
        pedido = Pedido(
            id=1,
            cliente_id=1,
            estado_actual="BORRADOR",
            total=Decimal("10.00"),
        )
        detalle = DetallePedido(
            id=3,
            pedido_id=1,
            plato_id=2,
            nombre_plato="Sopa",
            precio_unitario=Decimal("10.00"),
            cantidad=1,
            subtotal=Decimal("10.00"),
        )
        oferta = DetalleMenu(
            id=10,
            menu_id=4,
            plato_id=2,
            stock=2,
            disponible=True,
        )
        self.session.get.return_value = pedido
        self.session.execute.side_effect = [
            list_result([detalle]),
            scalar_result(oferta),
            scalar_result(99),
            scalar_result(None),
        ]
        candidates = iter(["RET-DUPLICADO", "RET-NUEVO"])

        result = await confirmar_pedido(
            self.session,
            pedido_id=1,
            menu_id=4,
            generador_codigo=lambda: next(candidates),
        )

        self.assertEqual(result.codigo_seguimiento, "RET-NUEVO")
        self.assertEqual(oferta.stock, 1)


if __name__ == "__main__":
    unittest.main()
