"""Asignación, seguimiento y confirmación operativa de entregas."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
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
from app.services.errors import (
    ConflictoServicio,
    ErrorValidacion,
    RecursoNoEncontrado,
)
from app.services.pedidos import obtener_pedido


ESTADOS_REASIGNABLES = {
    "ASIGNADO",
    "ACEPTADO_REPARTIDOR",
    "EN_CAMINO",
}


def _ahora() -> datetime:
    """Obtiene una fecha consciente de zona para eventos operativos."""
    return datetime.now(timezone.utc)


def _historial(
    pedido: Pedido,
    *,
    anterior: str,
    nuevo: str,
    evento: str,
    origen: str,
    repartidor_id: int | None = None,
    administrador_id: int | None = None,
) -> HistorialEstado:
    """Construye un evento con un solo actor identificado."""
    return HistorialEstado(
        pedido_id=pedido.id,
        repartidor_id=repartidor_id,
        administrador_id=administrador_id,
        estado_anterior=anterior,
        estado_nuevo=nuevo,
        evento=evento,
        origen=origen,
    )


async def _repartidor_activo(
    session: AsyncSession,
    repartidor_id: int,
) -> Repartidor:
    """Exige una identidad de reparto existente y habilitada."""
    repartidor = await session.get(Repartidor, repartidor_id)
    if repartidor is None or not repartidor.activo:
        raise ConflictoServicio("El repartidor no está habilitado.")
    return repartidor


async def _asignacion(
    session: AsyncSession,
    asignacion_id: int,
) -> Asignacion:
    """Obtiene una asignación por su identificador."""
    asignacion = await session.get(Asignacion, asignacion_id)
    if asignacion is None:
        raise RecursoNoEncontrado("La asignación no existe.")
    return asignacion


async def _validar_actor_asignado(
    session: AsyncSession,
    asignacion: Asignacion,
    repartidor_id: int,
    *,
    permitir_cerrada: bool = False,
) -> Pedido:
    """Valida propiedad, habilitación y vigencia de la asignación."""
    await _repartidor_activo(session, repartidor_id)
    if asignacion.repartidor_id != repartidor_id:
        raise ConflictoServicio("La asignación pertenece a otro repartidor.")
    if not permitir_cerrada and not asignacion.activa:
        raise ConflictoServicio("La asignación ya no está activa.")
    return await obtener_pedido(session, asignacion.pedido_id)


async def asignar_repartidor(
    session: AsyncSession,
    *,
    pedido_id: int,
    repartidor_id: int,
    administrador_id: int,
) -> Asignacion:
    """Asigna o reasigna un pedido sin eliminar el historial anterior."""
    administrador = await session.get(Administrador, administrador_id)
    if administrador is None or not administrador.activo:
        raise ConflictoServicio("El administrador no está habilitado.")
    await _repartidor_activo(session, repartidor_id)
    pedido = await obtener_pedido(session, pedido_id)

    result = await session.execute(
        select(Asignacion)
        .where(
            Asignacion.pedido_id == pedido_id,
            Asignacion.activa.is_(True),
        )
        .with_for_update()
    )
    anterior = result.scalar_one_or_none()
    if anterior and anterior.repartidor_id == repartidor_id:
        if pedido.estado_actual == "ASIGNADO":
            return anterior
        raise ConflictoServicio("El repartidor ya atiende el pedido.")

    es_inicial = anterior is None
    if es_inicial and pedido.estado_actual != "PAGO_CONFIRMADO":
        raise ConflictoServicio("El pedido todavía no puede asignarse.")
    if not es_inicial and pedido.estado_actual not in ESTADOS_REASIGNABLES:
        raise ConflictoServicio("El pedido no puede reasignarse.")

    estado_anterior = pedido.estado_actual
    if anterior is not None:
        anterior.activa = False
        anterior.fecha_cierre = _ahora()

    nueva = Asignacion(
        pedido_id=pedido.id,
        repartidor_id=repartidor_id,
        activa=True,
    )
    session.add(nueva)
    pedido.estado_actual = "ASIGNADO"
    session.add(
        _historial(
            pedido,
            anterior=estado_anterior,
            nuevo="ASIGNADO",
            evento="ASIGNAR_REPARTIDOR" if es_inicial else "REASIGNAR",
            origen="ADMINISTRADOR",
            administrador_id=administrador_id,
        )
    )
    await session.flush()
    return nueva


async def acusar_recepcion(
    session: AsyncSession,
    *,
    asignacion_id: int,
    repartidor_id: int,
) -> Asignacion:
    """Registra una sola vez que el repartidor recibió el pedido."""
    asignacion = await _asignacion(session, asignacion_id)
    pedido = await _validar_actor_asignado(
        session,
        asignacion,
        repartidor_id,
    )
    if (
        pedido.estado_actual == "ACEPTADO_REPARTIDOR"
        and asignacion.fecha_acuse is not None
    ):
        return asignacion
    if pedido.estado_actual != "ASIGNADO":
        raise ConflictoServicio("El pedido no espera el acuse.")

    asignacion.fecha_acuse = _ahora()
    pedido.estado_actual = "ACEPTADO_REPARTIDOR"
    session.add(
        _historial(
            pedido,
            anterior="ASIGNADO",
            nuevo="ACEPTADO_REPARTIDOR",
            evento="ACUSAR_RECEPCION",
            origen="REPARTIDOR",
            repartidor_id=repartidor_id,
        )
    )
    await session.flush()
    return asignacion


async def iniciar_trayecto(
    session: AsyncSession,
    *,
    asignacion_id: int,
    repartidor_id: int,
) -> Pedido:
    """Inicia de forma idempotente el recorrido hacia el cliente."""
    asignacion = await _asignacion(session, asignacion_id)
    pedido = await _validar_actor_asignado(
        session,
        asignacion,
        repartidor_id,
    )
    if pedido.estado_actual == "EN_CAMINO":
        return pedido
    if pedido.estado_actual != "ACEPTADO_REPARTIDOR":
        raise ConflictoServicio("El pedido todavía no puede iniciar trayecto.")

    pedido.estado_actual = "EN_CAMINO"
    session.add(
        _historial(
            pedido,
            anterior="ACEPTADO_REPARTIDOR",
            nuevo="EN_CAMINO",
            evento="INICIAR_TRAYECTO",
            origen="REPARTIDOR",
            repartidor_id=repartidor_id,
        )
    )
    await session.flush()
    return pedido


def _coordenada(value: Decimal | float | str) -> Decimal:
    """Convierte una coordenada a Decimal o informa un dato inválido."""
    try:
        return Decimal(str(value))
    except Exception as error:
        raise ErrorValidacion("La coordenada no es válida.") from error


async def registrar_ubicacion_trayecto(
    session: AsyncSession,
    *,
    asignacion_id: int,
    repartidor_id: int,
    latitud: Decimal | float | str,
    longitud: Decimal | float | str,
) -> UbicacionTrayecto:
    """Guarda un punto nuevo o devuelve el último si es un reintento."""
    asignacion = await _asignacion(session, asignacion_id)
    pedido = await _validar_actor_asignado(
        session,
        asignacion,
        repartidor_id,
    )
    if pedido.estado_actual != "EN_CAMINO":
        raise ConflictoServicio("El pedido no está en camino.")
    latitud_decimal = _coordenada(latitud)
    longitud_decimal = _coordenada(longitud)
    if not Decimal("-90") <= latitud_decimal <= Decimal("90"):
        raise ErrorValidacion("La latitud está fuera de rango.")
    if not Decimal("-180") <= longitud_decimal <= Decimal("180"):
        raise ErrorValidacion("La longitud está fuera de rango.")

    result = await session.execute(
        select(UbicacionTrayecto)
        .where(UbicacionTrayecto.asignacion_id == asignacion.id)
        .order_by(UbicacionTrayecto.fecha_registro.desc())
        .limit(1)
    )
    ultima = result.scalar_one_or_none()
    if (
        ultima is not None
        and ultima.latitud == latitud_decimal
        and ultima.longitud == longitud_decimal
    ):
        return ultima

    ubicacion = UbicacionTrayecto(
        asignacion_id=asignacion.id,
        latitud=latitud_decimal,
        longitud=longitud_decimal,
    )
    session.add(ubicacion)
    await session.flush()
    return ubicacion


async def registrar_llegada(
    session: AsyncSession,
    *,
    asignacion_id: int,
    repartidor_id: int,
) -> Pedido:
    """Registra la llegada separada de la entrega."""
    asignacion = await _asignacion(session, asignacion_id)
    pedido = await _validar_actor_asignado(
        session,
        asignacion,
        repartidor_id,
    )
    if pedido.estado_actual == "EN_DESTINO":
        return pedido
    if pedido.estado_actual != "EN_CAMINO":
        raise ConflictoServicio("El pedido no admite registrar llegada.")

    pedido.estado_actual = "EN_DESTINO"
    session.add(
        _historial(
            pedido,
            anterior="EN_CAMINO",
            nuevo="EN_DESTINO",
            evento="REGISTRAR_LLEGADA",
            origen="REPARTIDOR",
            repartidor_id=repartidor_id,
        )
    )
    await session.flush()
    return pedido


async def confirmar_entrega(
    session: AsyncSession,
    *,
    asignacion_id: int,
    repartidor_id: int,
    tipo: str,
    valor_referencia: str,
    tipo_mime: str | None = None,
    tamanio_bytes: int | None = None,
) -> EvidenciaEntrega:
    """Conserva evidencia y completa la entrega una sola vez."""
    asignacion = await _asignacion(session, asignacion_id)
    pedido = await _validar_actor_asignado(
        session,
        asignacion,
        repartidor_id,
        permitir_cerrada=pedido_entregado(asignacion),
    )

    result = await session.execute(
        select(EvidenciaEntrega).where(
            EvidenciaEntrega.asignacion_id == asignacion.id
        )
    )
    existente = result.scalar_one_or_none()
    if pedido.estado_actual == "ENTREGADO" and existente is not None:
        return existente
    if pedido.estado_actual != "EN_DESTINO" or not asignacion.activa:
        raise ConflictoServicio("El pedido no admite confirmar entrega.")

    tipo_normalizado = tipo.strip().upper()
    referencia = valor_referencia.strip()
    if tipo_normalizado not in {"FOTOGRAFIA", "CODIGO"} or not referencia:
        raise ErrorValidacion("La evidencia no es válida.")
    if tipo_normalizado == "FOTOGRAFIA":
        if not tipo_mime or tamanio_bytes is None or tamanio_bytes < 0:
            raise ErrorValidacion("Faltan metadatos de la fotografía.")
    else:
        tipo_mime = None
        tamanio_bytes = None

    evidencia = EvidenciaEntrega(
        asignacion_id=asignacion.id,
        tipo=tipo_normalizado,
        valor_referencia=referencia,
        tipo_mime=tipo_mime.strip() if tipo_mime else None,
        tamanio_bytes=tamanio_bytes,
    )
    session.add(evidencia)
    pedido.estado_actual = "ENTREGADO"
    asignacion.activa = False
    asignacion.fecha_cierre = _ahora()
    session.add(
        _historial(
            pedido,
            anterior="EN_DESTINO",
            nuevo="ENTREGADO",
            evento="CONFIRMAR_ENTREGA",
            origen="REPARTIDOR",
            repartidor_id=repartidor_id,
        )
    )
    await session.flush()
    return evidencia


def pedido_entregado(asignacion: Asignacion) -> bool:
    """Permite consultar una entrega idempotente tras cerrar la asignación."""
    return not asignacion.activa and asignacion.fecha_cierre is not None
