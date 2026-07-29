"""Pruebas unitarias de asignación y operación del reparto."""

import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Administrador,
    Asignacion,
    EvidenciaEntrega,
    HistorialEstado,
    Pedido,
    Repartidor,
    UbicacionTrayecto,
)
from app.services import (
    ConflictoServicio,
    ErrorValidacion,
    acusar_recepcion,
    asignar_repartidor,
    confirmar_entrega,
    iniciar_trayecto,
    registrar_llegada,
    registrar_ubicacion_trayecto,
)


def scalar_result(value: object) -> MagicMock:
    """Simula un resultado con cero o una fila escalar."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


class RepartoServiceTest(unittest.IsolatedAsyncioTestCase):
    """Comprueba el flujo sin Telegram, mapa o PostgreSQL."""

    def setUp(self) -> None:
        """Prepara una sesión asíncrona observable."""
        self.session = MagicMock(spec=AsyncSession)
        self.session.get = AsyncMock()
        self.session.execute = AsyncMock()
        self.session.flush = AsyncMock()
        self.session.commit = AsyncMock()

    def admin(self) -> Administrador:
        """Construye un administrador habilitado."""
        return Administrador(
            id=9,
            nombre_usuario="admin",
            credencial_hash="hash",
            activo=True,
        )

    def repartidor(self, repartidor_id: int = 7) -> Repartidor:
        """Construye un repartidor habilitado."""
        return Repartidor(
            id=repartidor_id,
            chat_id=str(repartidor_id),
            activo=True,
        )

    def pedido(self, estado: str) -> Pedido:
        """Construye un pedido persistido en el estado indicado."""
        return Pedido(
            id=1,
            cliente_id=4,
            menu_id=2,
            estado_actual=estado,
            total=Decimal("20.00"),
        )

    def asignacion(
        self,
        *,
        repartidor_id: int = 7,
        activa: bool = True,
    ) -> Asignacion:
        """Construye una asignación persistida."""
        return Asignacion(
            id=3,
            pedido_id=1,
            repartidor_id=repartidor_id,
            activa=activa,
        )

    async def test_asignar_creates_active_assignment(self) -> None:
        """Vincula un repartidor y cambia el pedido a ASIGNADO."""
        pedido = self.pedido("PAGO_CONFIRMADO")
        self.session.get.side_effect = [
            self.admin(),
            self.repartidor(),
            pedido,
        ]
        self.session.execute.return_value = scalar_result(None)

        nueva = await asignar_repartidor(
            self.session,
            pedido_id=1,
            repartidor_id=7,
            administrador_id=9,
        )

        self.assertTrue(nueva.activa)
        self.assertEqual(nueva.repartidor_id, 7)
        self.assertEqual(pedido.estado_actual, "ASIGNADO")
        added = [item.args[0] for item in self.session.add.call_args_list]
        self.assertTrue(any(isinstance(item, HistorialEstado) for item in added))
        self.session.commit.assert_not_awaited()

    async def test_reasignar_closes_previous_assignment(self) -> None:
        """Conserva el historial y no crea otro pedido."""
        pedido = self.pedido("EN_CAMINO")
        anterior = self.asignacion(repartidor_id=6)
        self.session.get.side_effect = [
            self.admin(),
            self.repartidor(7),
            pedido,
        ]
        self.session.execute.return_value = scalar_result(anterior)

        nueva = await asignar_repartidor(
            self.session,
            pedido_id=1,
            repartidor_id=7,
            administrador_id=9,
        )

        self.assertFalse(anterior.activa)
        self.assertIsNotNone(anterior.fecha_cierre)
        self.assertTrue(nueva.activa)
        self.assertEqual(pedido.estado_actual, "ASIGNADO")
        self.session.delete.assert_not_called()

    async def test_asignar_same_repartidor_is_idempotent(self) -> None:
        """Devuelve la asignación activa sin duplicarla."""
        pedido = self.pedido("ASIGNADO")
        anterior = self.asignacion()
        self.session.get.side_effect = [
            self.admin(),
            self.repartidor(),
            pedido,
        ]
        self.session.execute.return_value = scalar_result(anterior)

        result = await asignar_repartidor(
            self.session,
            pedido_id=1,
            repartidor_id=7,
            administrador_id=9,
        )

        self.assertIs(result, anterior)
        self.session.add.assert_not_called()
        self.session.flush.assert_not_awaited()

    async def test_asignar_rejects_inactive_repartidor(self) -> None:
        """Impide asignar una identidad deshabilitada."""
        repartidor = self.repartidor()
        repartidor.activo = False
        self.session.get.side_effect = [self.admin(), repartidor]

        with self.assertRaises(ConflictoServicio):
            await asignar_repartidor(
                self.session,
                pedido_id=1,
                repartidor_id=7,
                administrador_id=9,
            )

    async def test_acusar_recepcion_records_date_and_state(self) -> None:
        """Registra el acuse del repartidor asignado."""
        asignacion = self.asignacion()
        pedido = self.pedido("ASIGNADO")
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(),
            pedido,
        ]

        result = await acusar_recepcion(
            self.session,
            asignacion_id=3,
            repartidor_id=7,
        )

        self.assertIs(result, asignacion)
        self.assertIsNotNone(asignacion.fecha_acuse)
        self.assertEqual(pedido.estado_actual, "ACEPTADO_REPARTIDOR")

    async def test_wrong_repartidor_cannot_operate_assignment(self) -> None:
        """Evita eventos producidos por otro repartidor."""
        asignacion = self.asignacion(repartidor_id=7)
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(8),
        ]

        with self.assertRaises(ConflictoServicio):
            await acusar_recepcion(
                self.session,
                asignacion_id=3,
                repartidor_id=8,
            )
        self.session.flush.assert_not_awaited()

    async def test_iniciar_trayecto_is_idempotent(self) -> None:
        """Avanza una vez y luego conserva EN_CAMINO."""
        asignacion = self.asignacion()
        pedido = self.pedido("ACEPTADO_REPARTIDOR")
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(),
            pedido,
        ]

        first = await iniciar_trayecto(
            self.session,
            asignacion_id=3,
            repartidor_id=7,
        )

        self.assertEqual(first.estado_actual, "EN_CAMINO")
        self.assertEqual(self.session.add.call_count, 1)

    async def test_registrar_ubicacion_adds_new_point(self) -> None:
        """Vincula coordenadas válidas con la asignación activa."""
        asignacion = self.asignacion()
        pedido = self.pedido("EN_CAMINO")
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(),
            pedido,
        ]
        self.session.execute.return_value = scalar_result(None)

        ubicacion = await registrar_ubicacion_trayecto(
            self.session,
            asignacion_id=3,
            repartidor_id=7,
            latitud="-17.97",
            longitud="-67.11",
        )

        self.assertEqual(ubicacion.asignacion_id, 3)
        self.assertEqual(ubicacion.latitud, Decimal("-17.97"))
        self.session.add.assert_called_once_with(ubicacion)

    async def test_registrar_ubicacion_deduplicates_retry(self) -> None:
        """Devuelve el último punto cuando las coordenadas se repiten."""
        asignacion = self.asignacion()
        pedido = self.pedido("EN_CAMINO")
        ultima = UbicacionTrayecto(
            id=5,
            asignacion_id=3,
            latitud=Decimal("-17.97"),
            longitud=Decimal("-67.11"),
        )
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(),
            pedido,
        ]
        self.session.execute.return_value = scalar_result(ultima)

        result = await registrar_ubicacion_trayecto(
            self.session,
            asignacion_id=3,
            repartidor_id=7,
            latitud="-17.97",
            longitud="-67.11",
        )

        self.assertIs(result, ultima)
        self.session.add.assert_not_called()
        self.session.flush.assert_not_awaited()

    async def test_registrar_ubicacion_rejects_invalid_range(self) -> None:
        """No persiste coordenadas fuera del rango geográfico."""
        asignacion = self.asignacion()
        pedido = self.pedido("EN_CAMINO")
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(),
            pedido,
        ]

        with self.assertRaises(ErrorValidacion):
            await registrar_ubicacion_trayecto(
                self.session,
                asignacion_id=3,
                repartidor_id=7,
                latitud="0",
                longitud="181",
            )
        self.session.execute.assert_not_awaited()

    async def test_registrar_llegada_is_separate_from_delivery(self) -> None:
        """Pasa a EN_DESTINO sin cerrar la asignación."""
        asignacion = self.asignacion()
        pedido = self.pedido("EN_CAMINO")
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(),
            pedido,
        ]

        result = await registrar_llegada(
            self.session,
            asignacion_id=3,
            repartidor_id=7,
        )

        self.assertEqual(result.estado_actual, "EN_DESTINO")
        self.assertTrue(asignacion.activa)

    async def test_confirmar_entrega_with_photo_closes_assignment(
        self,
    ) -> None:
        """Conserva los metadatos y completa el pedido."""
        asignacion = self.asignacion()
        pedido = self.pedido("EN_DESTINO")
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(),
            pedido,
        ]
        self.session.execute.return_value = scalar_result(None)

        evidencia = await confirmar_entrega(
            self.session,
            asignacion_id=3,
            repartidor_id=7,
            tipo="fotografia",
            valor_referencia="entregas/1/foto.jpg",
            tipo_mime="image/jpeg",
            tamanio_bytes=500,
        )

        self.assertEqual(evidencia.tipo, "FOTOGRAFIA")
        self.assertEqual(pedido.estado_actual, "ENTREGADO")
        self.assertFalse(asignacion.activa)
        self.assertIsNotNone(asignacion.fecha_cierre)

    async def test_confirmar_entrega_with_code_omits_file_metadata(
        self,
    ) -> None:
        """Admite un código sin fingir que existe una fotografía."""
        asignacion = self.asignacion()
        pedido = self.pedido("EN_DESTINO")
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(),
            pedido,
        ]
        self.session.execute.return_value = scalar_result(None)

        evidencia = await confirmar_entrega(
            self.session,
            asignacion_id=3,
            repartidor_id=7,
            tipo="CODIGO",
            valor_referencia="ABC123",
            tipo_mime="image/jpeg",
            tamanio_bytes=500,
        )

        self.assertEqual(evidencia.tipo, "CODIGO")
        self.assertIsNone(evidencia.tipo_mime)
        self.assertIsNone(evidencia.tamanio_bytes)

    async def test_confirmar_entrega_is_idempotent(self) -> None:
        """Devuelve la evidencia existente después del cierre."""
        asignacion = self.asignacion(activa=False)
        asignacion.fecha_cierre = MagicMock()
        pedido = self.pedido("ENTREGADO")
        evidencia = EvidenciaEntrega(
            id=6,
            asignacion_id=3,
            tipo="CODIGO",
            valor_referencia="ABC123",
        )
        self.session.get.side_effect = [
            asignacion,
            self.repartidor(),
            pedido,
        ]
        self.session.execute.return_value = scalar_result(evidencia)

        result = await confirmar_entrega(
            self.session,
            asignacion_id=3,
            repartidor_id=7,
            tipo="CODIGO",
            valor_referencia="ABC123",
        )

        self.assertIs(result, evidencia)
        self.session.add.assert_not_called()
        self.session.flush.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
