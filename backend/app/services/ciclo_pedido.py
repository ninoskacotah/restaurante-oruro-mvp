"""Ubicación, pago y cancelación del pedido confirmado."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
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
from app.services.errors import (
    ConflictoServicio,
    ErrorValidacion,
    RecursoNoEncontrado,
)
from app.services.pedidos import obtener_pedido


ESTADO_PENDIENTE_UBICACION = "PENDIENTE_UBICACION"
ESTADO_PENDIENTE_COMPROBANTE = "PENDIENTE_COMPROBANTE"
ESTADO_PAGO_EN_REVISION = "PAGO_EN_REVISION"
ESTADO_PAGO_CONFIRMADO = "PAGO_CONFIRMADO"
ESTADO_CANCELADO = "CANCELADO"
ESTADOS_CANCELABLES = {
    ESTADO_PENDIENTE_UBICACION,
    ESTADO_PENDIENTE_COMPROBANTE,
    ESTADO_PAGO_EN_REVISION,
    ESTADO_PAGO_CONFIRMADO,
    "ASIGNADO",
    "ACEPTADO_REPARTIDOR",
    "EN_CAMINO",
    "EN_DESTINO",
}
ESTADOS_CON_ASIGNACION = {
    "ASIGNADO",
    "ACEPTADO_REPARTIDOR",
    "EN_CAMINO",
    "EN_DESTINO",
}


def _historial(
    pedido: Pedido,
    *,
    estado_anterior: str,
    estado_nuevo: str,
    evento: str,
    origen: str,
    cliente_id: int | None = None,
    administrador_id: int | None = None,
) -> HistorialEstado:
    """Construye un evento consistente con la restricción de un actor."""
    return HistorialEstado(
        pedido_id=pedido.id,
        cliente_id=cliente_id,
        administrador_id=administrador_id,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        evento=evento,
        origen=origen,
    )


def _decimal_coordenada(value: Decimal | float | str) -> Decimal:
    """Convierte entradas numéricas sin introducir aritmética binaria."""
    try:
        return Decimal(str(value))
    except Exception as error:
        raise ErrorValidacion("La coordenada no es válida.") from error


async def registrar_ubicacion_entrega(
    session: AsyncSession,
    *,
    pedido_id: int,
    latitud: Decimal | float | str,
    longitud: Decimal | float | str,
    referencia: str | None,
    cliente_id: int,
) -> Pedido:
    """Guarda el destino fijo y habilita la recepción del comprobante."""
    pedido = await obtener_pedido(session, pedido_id)
    if pedido.estado_actual != ESTADO_PENDIENTE_UBICACION:
        raise ConflictoServicio("El pedido no espera una ubicación.")
    if pedido.cliente_id != cliente_id:
        raise ConflictoServicio("El pedido no pertenece al cliente.")

    latitud_decimal = _decimal_coordenada(latitud)
    longitud_decimal = _decimal_coordenada(longitud)
    if not Decimal("-90") <= latitud_decimal <= Decimal("90"):
        raise ErrorValidacion("La latitud está fuera de rango.")
    if not Decimal("-180") <= longitud_decimal <= Decimal("180"):
        raise ErrorValidacion("La longitud está fuera de rango.")

    pedido.entrega_latitud = latitud_decimal
    pedido.entrega_longitud = longitud_decimal
    pedido.referencia_entrega = referencia.strip() if referencia else None
    pedido.estado_actual = ESTADO_PENDIENTE_COMPROBANTE
    session.add(
        _historial(
            pedido,
            estado_anterior=ESTADO_PENDIENTE_UBICACION,
            estado_nuevo=ESTADO_PENDIENTE_COMPROBANTE,
            evento="REGISTRAR_UBICACION",
            origen="CLIENTE",
            cliente_id=cliente_id,
        )
    )
    await session.flush()
    return pedido


async def registrar_comprobante_pago(
    session: AsyncSession,
    *,
    pedido_id: int,
    cliente_id: int,
    archivo_referencia: str,
    nombre_generado: str,
    tipo_mime: str,
    tamanio_bytes: int,
) -> ComprobantePago:
    """Registra metadatos sin guardar binarios ni confirmar el pago."""
    pedido = await obtener_pedido(session, pedido_id)
    if pedido.estado_actual != ESTADO_PENDIENTE_COMPROBANTE:
        raise ConflictoServicio("El pedido no espera un comprobante.")
    if pedido.cliente_id != cliente_id:
        raise ConflictoServicio("El pedido no pertenece al cliente.")
    if not archivo_referencia.strip() or not nombre_generado.strip():
        raise ErrorValidacion("La referencia y el nombre son obligatorios.")
    if not tipo_mime.strip():
        raise ErrorValidacion("El tipo MIME es obligatorio.")
    if tamanio_bytes < 0:
        raise ErrorValidacion("El tamaño no puede ser negativo.")

    comprobante = ComprobantePago(
        pedido_id=pedido.id,
        archivo_referencia=archivo_referencia.strip(),
        nombre_generado=nombre_generado.strip(),
        tipo_mime=tipo_mime.strip(),
        tamanio_bytes=tamanio_bytes,
        estado_revision="PENDIENTE",
    )
    session.add(comprobante)
    pedido.estado_actual = ESTADO_PAGO_EN_REVISION
    session.add(
        _historial(
            pedido,
            estado_anterior=ESTADO_PENDIENTE_COMPROBANTE,
            estado_nuevo=ESTADO_PAGO_EN_REVISION,
            evento="RECIBIR_COMPROBANTE",
            origen="CLIENTE",
            cliente_id=cliente_id,
        )
    )
    await session.flush()
    return comprobante


async def revisar_comprobante_pago(
    session: AsyncSession,
    *,
    comprobante_id: int,
    administrador_id: int,
    aprobado: bool,
    observacion: str | None,
) -> Pedido:
    """Aprueba o rechaza una revisión pendiente mediante un administrador."""
    comprobante = await session.get(ComprobantePago, comprobante_id)
    if comprobante is None:
        raise RecursoNoEncontrado("El comprobante solicitado no existe.")
    if comprobante.estado_revision != "PENDIENTE":
        raise ConflictoServicio("El comprobante ya fue revisado.")

    administrador = await session.get(Administrador, administrador_id)
    if administrador is None or not administrador.activo:
        raise ConflictoServicio("El administrador no está habilitado.")
    pedido = await obtener_pedido(session, comprobante.pedido_id)
    if pedido.estado_actual != ESTADO_PAGO_EN_REVISION:
        raise ConflictoServicio("El pedido no admite revisar el pago.")

    estado_nuevo = (
        ESTADO_PAGO_CONFIRMADO
        if aprobado
        else ESTADO_PENDIENTE_COMPROBANTE
    )
    comprobante.administrador_id = administrador_id
    comprobante.estado_revision = "APROBADO" if aprobado else "RECHAZADO"
    comprobante.observacion = observacion.strip() if observacion else None
    comprobante.fecha_revision = datetime.now(timezone.utc)
    pedido.estado_actual = estado_nuevo
    session.add(
        _historial(
            pedido,
            estado_anterior=ESTADO_PAGO_EN_REVISION,
            estado_nuevo=estado_nuevo,
            evento=(
                "APROBAR_COMPROBANTE"
                if aprobado
                else "RECHAZAR_COMPROBANTE"
            ),
            origen="ADMINISTRADOR",
            administrador_id=administrador_id,
        )
    )
    await session.flush()
    return pedido


async def cancelar_pedido(
    session: AsyncSession,
    *,
    pedido_id: int,
    motivo: str,
    origen: str,
    cliente_id: int | None = None,
    administrador_id: int | None = None,
) -> Pedido:
    """Cancela una vez y repone el stock del menú de origen."""
    pedido = await obtener_pedido(session, pedido_id)
    if pedido.estado_actual == ESTADO_CANCELADO:
        return pedido
    if pedido.estado_actual not in ESTADOS_CANCELABLES:
        raise ConflictoServicio("El pedido no puede cancelarse.")
    motivo_limpio = motivo.strip()
    if not motivo_limpio or len(motivo_limpio) > 32:
        raise ErrorValidacion("El motivo debe contener entre 1 y 32 caracteres.")
    if cliente_id is not None and administrador_id is not None:
        raise ErrorValidacion("La cancelación admite un solo actor.")
    if cliente_id is not None and pedido.cliente_id != cliente_id:
        raise ConflictoServicio("El pedido no pertenece al cliente.")
    if pedido.menu_id is None:
        raise ConflictoServicio("El pedido no conserva su menú de origen.")

    result = await session.execute(
        select(DetallePedido)
        .where(DetallePedido.pedido_id == pedido.id)
        .order_by(DetallePedido.id)
    )
    detalles = list(result.scalars().all())

    # Primero se bloquea y valida toda la oferta; luego se repone en conjunto.
    ofertas_bloqueadas: list[tuple[DetalleMenu, DetallePedido]] = []
    for detalle in detalles:
        result = await session.execute(
            select(DetalleMenu)
            .where(
                DetalleMenu.menu_id == pedido.menu_id,
                DetalleMenu.plato_id == detalle.plato_id,
            )
            .with_for_update()
        )
        oferta = result.scalar_one_or_none()
        if oferta is None:
            raise ConflictoServicio(
                f"No existe la oferta de {detalle.nombre_plato}."
            )
        ofertas_bloqueadas.append((oferta, detalle))

    for oferta, detalle in ofertas_bloqueadas:
        oferta.stock += detalle.cantidad

    estado_anterior = pedido.estado_actual
    if estado_anterior in ESTADOS_CON_ASIGNACION:
        result = await session.execute(
            select(Asignacion)
            .where(
                Asignacion.pedido_id == pedido.id,
                Asignacion.activa.is_(True),
            )
            .with_for_update()
        )
        for asignacion in result.scalars().all():
            asignacion.activa = False
            asignacion.fecha_cierre = datetime.now(timezone.utc)

    pedido.estado_actual = ESTADO_CANCELADO
    session.add(
        _historial(
            pedido,
            estado_anterior=estado_anterior,
            estado_nuevo=ESTADO_CANCELADO,
            evento=f"CANCELAR_PEDIDO:{motivo_limpio}",
            origen=origen,
            cliente_id=cliente_id,
            administrador_id=administrador_id,
        )
    )
    await session.flush()
    return pedido
