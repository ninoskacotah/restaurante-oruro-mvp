"""Pruebas de ubicación, pago y cancelación del pedido."""

import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Administrador,
    Asignacion,
    ComprobantePago,
    DetalleMenu,
    DetallePedido,
    HistorialEstado,
    Pedido,
)
from app.services import (
    ConflictoServicio,
    ErrorValidacion,
    cancelar_pedido,
    registrar_comprobante_pago,
    registrar_ubicacion_entrega,
    revisar_comprobante_pago,
)


def scalar_result(value: object) -> MagicMock:
    """Simula un resultado con cero o una fila escalar."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def list_result(values: list[object]) -> MagicMock:
    """Simula un resultado con una colección de escalares."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


class CicloPedidoServiceTest(unittest.IsolatedAsyncioTestCase):
    """Verifica transiciones sin archivos, PostgreSQL o interfaces."""

    def setUp(self) -> None:
        """Prepara una sesión asíncrona observable."""
        self.session = MagicMock(spec=AsyncSession)
        self.session.get = AsyncMock()
        self.session.execute = AsyncMock()
        self.session.flush = AsyncMock()
        self.session.commit = AsyncMock()

    async def test_registrar_ubicacion_advances_the_order(self) -> None:
        """Guarda el destino y registra el actor cliente."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PENDIENTE_UBICACION",
            total=Decimal("20.00"),
        )
        self.session.get.return_value = pedido

        result = await registrar_ubicacion_entrega(
            self.session,
            pedido_id=1,
            latitud="-17.9707",
            longitud="-67.1142",
            referencia="  Puerta principal  ",
            cliente_id=4,
        )

        self.assertIs(result, pedido)
        self.assertEqual(pedido.entrega_latitud, Decimal("-17.9707"))
        self.assertEqual(pedido.entrega_longitud, Decimal("-67.1142"))
        self.assertEqual(pedido.referencia_entrega, "Puerta principal")
        self.assertEqual(pedido.estado_actual, "PENDIENTE_COMPROBANTE")
        history = self.session.add.call_args.args[0]
        self.assertIsInstance(history, HistorialEstado)
        self.assertEqual(history.cliente_id, 4)
        self.session.commit.assert_not_awaited()

    async def test_registrar_ubicacion_rejects_out_of_range(self) -> None:
        """No modifica el pedido cuando una coordenada es inválida."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PENDIENTE_UBICACION",
            total=Decimal("20.00"),
        )
        self.session.get.return_value = pedido

        with self.assertRaises(ErrorValidacion):
            await registrar_ubicacion_entrega(
                self.session,
                pedido_id=1,
                latitud="91",
                longitud="0",
                referencia=None,
                cliente_id=4,
            )

        self.assertEqual(pedido.estado_actual, "PENDIENTE_UBICACION")
        self.session.add.assert_not_called()

    async def test_registrar_ubicacion_requires_order_owner(self) -> None:
        """Evita que otro cliente modifique el destino."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PENDIENTE_UBICACION",
            total=Decimal("20.00"),
        )
        self.session.get.return_value = pedido

        with self.assertRaises(ConflictoServicio):
            await registrar_ubicacion_entrega(
                self.session,
                pedido_id=1,
                latitud="0",
                longitud="0",
                referencia=None,
                cliente_id=8,
            )

    async def test_registrar_comprobante_does_not_confirm_payment(
        self,
    ) -> None:
        """Crea metadatos pendientes y pasa a revisión."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PENDIENTE_COMPROBANTE",
            total=Decimal("20.00"),
        )
        self.session.get.return_value = pedido

        comprobante = await registrar_comprobante_pago(
            self.session,
            pedido_id=1,
            cliente_id=4,
            archivo_referencia="pedidos/1/comprobante.jpg",
            nombre_generado="archivo-seguro.jpg",
            tipo_mime="image/jpeg",
            tamanio_bytes=1234,
        )

        self.assertEqual(comprobante.estado_revision, "PENDIENTE")
        self.assertEqual(pedido.estado_actual, "PAGO_EN_REVISION")
        self.assertNotEqual(pedido.estado_actual, "PAGO_CONFIRMADO")
        added = [item.args[0] for item in self.session.add.call_args_list]
        self.assertIn(comprobante, added)

    async def test_registrar_comprobante_rejects_negative_size(self) -> None:
        """Impide persistir metadatos inconsistentes."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PENDIENTE_COMPROBANTE",
            total=Decimal("20.00"),
        )
        self.session.get.return_value = pedido

        with self.assertRaises(ErrorValidacion):
            await registrar_comprobante_pago(
                self.session,
                pedido_id=1,
                cliente_id=4,
                archivo_referencia="archivo.jpg",
                nombre_generado="seguro.jpg",
                tipo_mime="image/jpeg",
                tamanio_bytes=-1,
            )
        self.session.add.assert_not_called()

    async def test_revisar_requires_active_administrator(self) -> None:
        """Rechaza una identidad administrativa deshabilitada."""
        comprobante = ComprobantePago(
            id=5,
            pedido_id=1,
            archivo_referencia="archivo.jpg",
            nombre_generado="seguro.jpg",
            tipo_mime="image/jpeg",
            tamanio_bytes=100,
            estado_revision="PENDIENTE",
        )
        admin = Administrador(
            id=8,
            nombre_usuario="admin",
            credencial_hash="hash",
            activo=False,
        )
        self.session.get.side_effect = [comprobante, admin]

        with self.assertRaises(ConflictoServicio):
            await revisar_comprobante_pago(
                self.session,
                comprobante_id=5,
                administrador_id=8,
                aprobado=True,
                observacion=None,
            )

        self.assertEqual(comprobante.estado_revision, "PENDIENTE")

    async def test_approve_comprobante_confirms_payment(self) -> None:
        """Conserva revisor, fecha, decisión e historial."""
        comprobante = ComprobantePago(
            id=5,
            pedido_id=1,
            archivo_referencia="archivo.jpg",
            nombre_generado="seguro.jpg",
            tipo_mime="image/jpeg",
            tamanio_bytes=100,
            estado_revision="PENDIENTE",
        )
        admin = Administrador(
            id=8,
            nombre_usuario="admin",
            credencial_hash="hash",
            activo=True,
        )
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PAGO_EN_REVISION",
            total=Decimal("20.00"),
        )
        self.session.get.side_effect = [comprobante, admin, pedido]

        result = await revisar_comprobante_pago(
            self.session,
            comprobante_id=5,
            administrador_id=8,
            aprobado=True,
            observacion="  Verificado  ",
        )

        self.assertIs(result, pedido)
        self.assertEqual(comprobante.estado_revision, "APROBADO")
        self.assertEqual(comprobante.administrador_id, 8)
        self.assertEqual(comprobante.observacion, "Verificado")
        self.assertIsNotNone(comprobante.fecha_revision)
        self.assertEqual(pedido.estado_actual, "PAGO_CONFIRMADO")

    async def test_reject_comprobante_allows_another_attempt(self) -> None:
        """Conserva el rechazo y vuelve a esperar otro archivo."""
        comprobante = ComprobantePago(
            id=5,
            pedido_id=1,
            archivo_referencia="archivo.jpg",
            nombre_generado="seguro.jpg",
            tipo_mime="image/jpeg",
            tamanio_bytes=100,
            estado_revision="PENDIENTE",
        )
        admin = Administrador(
            id=8,
            nombre_usuario="admin",
            credencial_hash="hash",
            activo=True,
        )
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PAGO_EN_REVISION",
            total=Decimal("20.00"),
        )
        self.session.get.side_effect = [comprobante, admin, pedido]

        await revisar_comprobante_pago(
            self.session,
            comprobante_id=5,
            administrador_id=8,
            aprobado=False,
            observacion="No se distingue",
        )

        self.assertEqual(comprobante.estado_revision, "RECHAZADO")
        self.assertEqual(pedido.estado_actual, "PENDIENTE_COMPROBANTE")

    async def test_cancelar_restock_and_record_once(self) -> None:
        """Repone cantidades y conserva el motivo en un único evento."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PENDIENTE_COMPROBANTE",
            total=Decimal("20.00"),
        )
        detalle = DetallePedido(
            id=3,
            pedido_id=1,
            plato_id=7,
            nombre_plato="Sopa",
            precio_unitario=Decimal("10.00"),
            cantidad=2,
            subtotal=Decimal("20.00"),
        )
        oferta = DetalleMenu(
            id=9,
            menu_id=2,
            plato_id=7,
            stock=3,
            disponible=True,
        )
        self.session.get.return_value = pedido
        self.session.execute.side_effect = [
            list_result([detalle]),
            scalar_result(oferta),
        ]

        result = await cancelar_pedido(
            self.session,
            pedido_id=1,
            motivo="Cambio de planes",
            origen="CLIENTE",
            cliente_id=4,
        )

        self.assertIs(result, pedido)
        self.assertEqual(oferta.stock, 5)
        self.assertEqual(pedido.estado_actual, "CANCELADO")
        history = self.session.add.call_args.args[0]
        self.assertEqual(
            history.evento,
            "CANCELAR_PEDIDO:Cambio de planes",
        )
        self.session.commit.assert_not_awaited()

    async def test_cancelar_validates_all_rows_before_restock(self) -> None:
        """Evita una reposición parcial si falta la segunda oferta."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PAGO_CONFIRMADO",
            total=Decimal("20.00"),
        )
        first = DetallePedido(
            id=3,
            pedido_id=1,
            plato_id=7,
            nombre_plato="Sopa",
            precio_unitario=Decimal("10.00"),
            cantidad=1,
            subtotal=Decimal("10.00"),
        )
        second = DetallePedido(
            id=4,
            pedido_id=1,
            plato_id=8,
            nombre_plato="Segundo",
            precio_unitario=Decimal("10.00"),
            cantidad=1,
            subtotal=Decimal("10.00"),
        )
        oferta = DetalleMenu(
            id=9,
            menu_id=2,
            plato_id=7,
            stock=3,
            disponible=True,
        )
        self.session.get.return_value = pedido
        self.session.execute.side_effect = [
            list_result([first, second]),
            scalar_result(oferta),
            scalar_result(None),
        ]

        with self.assertRaises(ConflictoServicio):
            await cancelar_pedido(
                self.session,
                pedido_id=1,
                motivo="Error",
                origen="ADMINISTRADOR",
                administrador_id=8,
            )

        self.assertEqual(oferta.stock, 3)
        self.assertEqual(pedido.estado_actual, "PAGO_CONFIRMADO")

    async def test_cancelar_closes_active_assignment(self) -> None:
        """Evita dejar trabajo operativo después del estado final."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="ASIGNADO",
            total=Decimal("10.00"),
        )
        detalle = DetallePedido(
            id=3,
            pedido_id=1,
            plato_id=7,
            nombre_plato="Sopa",
            precio_unitario=Decimal("10.00"),
            cantidad=1,
            subtotal=Decimal("10.00"),
        )
        oferta = DetalleMenu(
            id=9,
            menu_id=2,
            plato_id=7,
            stock=3,
            disponible=True,
        )
        asignacion = Asignacion(
            id=6,
            pedido_id=1,
            repartidor_id=2,
            activa=True,
        )
        self.session.get.return_value = pedido
        self.session.execute.side_effect = [
            list_result([detalle]),
            scalar_result(oferta),
            list_result([asignacion]),
        ]

        await cancelar_pedido(
            self.session,
            pedido_id=1,
            motivo="Cambio",
            origen="CLIENTE",
            cliente_id=4,
        )

        self.assertEqual(pedido.estado_actual, "CANCELADO")
        self.assertFalse(asignacion.activa)
        self.assertIsNotNone(asignacion.fecha_cierre)
        self.assertEqual(oferta.stock, 4)

    async def test_cancelar_is_idempotent(self) -> None:
        """No consulta ni repone stock en una repetición."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="CANCELADO",
            total=Decimal("20.00"),
        )
        self.session.get.return_value = pedido

        result = await cancelar_pedido(
            self.session,
            pedido_id=1,
            motivo="Repetición",
            origen="CLIENTE",
            cliente_id=4,
        )

        self.assertIs(result, pedido)
        self.session.execute.assert_not_awaited()
        self.session.add.assert_not_called()
        self.session.flush.assert_not_awaited()

    async def test_cancelar_rejects_delivered_order(self) -> None:
        """Protege el estado final entregado."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="ENTREGADO",
            total=Decimal("20.00"),
        )
        self.session.get.return_value = pedido

        with self.assertRaises(ConflictoServicio):
            await cancelar_pedido(
                self.session,
                pedido_id=1,
                motivo="Tarde",
                origen="CLIENTE",
                cliente_id=4,
            )

    async def test_cancelar_requires_order_owner(self) -> None:
        """Evita que otro cliente cancele y reponga el pedido."""
        pedido = Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual="PENDIENTE_COMPROBANTE",
            total=Decimal("20.00"),
        )
        self.session.get.return_value = pedido

        with self.assertRaises(ConflictoServicio):
            await cancelar_pedido(
                self.session,
                pedido_id=1,
                motivo="Cambio",
                origen="CLIENTE",
                cliente_id=9,
            )

        self.session.execute.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
