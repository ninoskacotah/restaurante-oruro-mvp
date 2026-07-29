"""Endpoints administrativos de pedidos, pagos y seguimiento."""

from fastapi import APIRouter, BackgroundTasks, status
from sqlalchemy import select

from app.api.dependencies import AuthDependency, SessionDependency
from app.bot.delivery_service import active_delivery, format_delivery
from app.core.config import get_settings
from app.models import (
    Asignacion,
    ComprobantePago,
    Cliente,
    DetallePedido,
    HistorialEstado,
    Pedido,
    Repartidor,
    UbicacionTrayecto,
)
from app.schemas import (
    AsignacionInput,
    AsignacionOutput,
    HistorialOutput,
    PedidoOutput,
    PedidoDetailOutput,
    RepartidorOutput,
    RevisionComprobanteInput,
    SeguimientoOutput,
)
from app.services import (
    asignar_repartidor,
    obtener_pedido,
    revisar_comprobante_pago,
)


router = APIRouter(tags=["pedidos"])


async def _send_client_notification(
    *,
    chat_id: str,
    tracking_code: str,
    state: str,
) -> None:
    """Notifica al cliente después de confirmar la operación administrativa."""
    from aiogram import Bot

    from app.bot.notifications import notify_client_state

    settings = get_settings()
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())
    try:
        await notify_client_state(
            bot,
            chat_id=chat_id,
            tracking_code=tracking_code,
            state=state,
        )
    finally:
        await bot.session.close()


async def _send_assignment_notification(
    *,
    chat_id: str,
    text: str,
    latitude: float | None,
    longitude: float | None,
) -> None:
    """Envía la asignación después de responder la solicitud administrativa."""
    # La importación diferida mantiene la API comprobable sin abrir Telegram.
    from aiogram import Bot

    settings = get_settings()
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=f"Nueva asignación:\n\n{text}\n\nUsa /mi_entrega para operar.",
        )
        if latitude is not None and longitude is not None:
            await bot.send_location(
                chat_id=chat_id,
                latitude=latitude,
                longitude=longitude,
            )
    finally:
        await bot.session.close()


@router.get("/pedidos", response_model=list[PedidoOutput])
async def list_pedidos(
    session: SessionDependency,
    _auth: AuthDependency,
) -> list[Pedido]:
    """Lista pedidos recientes para el tablero administrativo."""
    result = await session.execute(
        select(Pedido).order_by(Pedido.fecha_creacion.desc())
    )
    return list(result.scalars().all())


@router.get("/pedidos/{pedido_id}", response_model=PedidoDetailOutput)
async def get_pedido(
    pedido_id: int,
    session: SessionDependency,
    _auth: AuthDependency,
) -> PedidoDetailOutput:
    """Obtiene cabecera, líneas, comprobantes y asignaciones."""
    pedido = await obtener_pedido(session, pedido_id)
    details_result = await session.execute(
        select(DetallePedido)
        .where(DetallePedido.pedido_id == pedido_id)
        .order_by(DetallePedido.id)
    )
    receipts_result = await session.execute(
        select(ComprobantePago)
        .where(ComprobantePago.pedido_id == pedido_id)
        .order_by(ComprobantePago.fecha_envio)
    )
    assignments_result = await session.execute(
        select(Asignacion)
        .where(Asignacion.pedido_id == pedido_id)
        .order_by(Asignacion.fecha_asignacion)
    )
    return PedidoDetailOutput(
        pedido=pedido,
        detalles=list(details_result.scalars().all()),
        comprobantes=list(receipts_result.scalars().all()),
        asignaciones=list(assignments_result.scalars().all()),
    )


@router.get("/repartidores", response_model=list[RepartidorOutput])
async def list_repartidores(
    session: SessionDependency,
    _auth: AuthDependency,
) -> list[Repartidor]:
    """Lista perfiles para el selector de asignación."""
    result = await session.execute(
        select(Repartidor).order_by(Repartidor.nombre, Repartidor.id)
    )
    return list(result.scalars().all())


@router.get(
    "/pedidos/{pedido_id}/historial",
    response_model=list[HistorialOutput],
)
async def get_history(
    pedido_id: int,
    session: SessionDependency,
    _auth: AuthDependency,
) -> list[HistorialEstado]:
    """Devuelve eventos acumulativos en orden cronológico."""
    await obtener_pedido(session, pedido_id)
    result = await session.execute(
        select(HistorialEstado)
        .where(HistorialEstado.pedido_id == pedido_id)
        .order_by(HistorialEstado.fecha_registro)
    )
    return list(result.scalars().all())


@router.post(
    "/comprobantes/{comprobante_id}/revision",
    response_model=PedidoOutput,
)
async def review_payment(
    comprobante_id: int,
    data: RevisionComprobanteInput,
    background_tasks: BackgroundTasks,
    session: SessionDependency,
    auth: AuthDependency,
) -> Pedido:
    """Aprueba o rechaza un comprobante mediante el actor autenticado."""
    pedido = await revisar_comprobante_pago(
        session,
        comprobante_id=comprobante_id,
        administrador_id=auth.administrador.id,
        aprobado=data.aprobado,
        observacion=data.observacion,
    )
    client = await session.get(Cliente, pedido.cliente_id)
    if data.aprobado and client is not None:
        background_tasks.add_task(
            _send_client_notification,
            chat_id=client.chat_id,
            tracking_code=pedido.codigo_seguimiento or str(pedido.id),
            state="PAGO_CONFIRMADO",
        )
    return pedido


@router.post(
    "/pedidos/{pedido_id}/asignaciones",
    response_model=AsignacionOutput,
    status_code=status.HTTP_201_CREATED,
)
async def assign_delivery(
    pedido_id: int,
    data: AsignacionInput,
    background_tasks: BackgroundTasks,
    session: SessionDependency,
    auth: AuthDependency,
) -> Asignacion:
    """Asigna o reasigna un repartidor desde el panel."""
    previous_result = await session.execute(
        select(Asignacion).where(
            Asignacion.pedido_id == pedido_id,
            Asignacion.activa.is_(True),
        )
    )
    previous = previous_result.scalar_one_or_none()
    assignment = await asignar_repartidor(
        session,
        pedido_id=pedido_id,
        repartidor_id=data.repartidor_id,
        administrador_id=auth.administrador.id,
    )
    summary = await active_delivery(session, assignment.repartidor_id)
    courier = await session.get(Repartidor, assignment.repartidor_id)
    is_new_assignment = previous is None or previous.id != assignment.id
    if summary is not None and courier is not None and is_new_assignment:
        background_tasks.add_task(
            _send_assignment_notification,
            chat_id=courier.chat_id,
            text=format_delivery(summary),
            latitude=(
                float(summary.order.entrega_latitud)
                if summary.order.entrega_latitud is not None
                else None
            ),
            longitude=(
                float(summary.order.entrega_longitud)
                if summary.order.entrega_longitud is not None
                else None
            ),
        )
        background_tasks.add_task(
            _send_client_notification,
            chat_id=summary.client.chat_id,
            tracking_code=(
                summary.order.codigo_seguimiento or str(summary.order.id)
            ),
            state="ASIGNADO",
        )
    return assignment


@router.get(
    "/pedidos/{pedido_id}/seguimiento",
    response_model=SeguimientoOutput,
)
async def get_tracking(
    pedido_id: int,
    session: SessionDependency,
    _auth: AuthDependency,
) -> SeguimientoOutput:
    """Devuelve solo la última ubicación de la asignación activa."""
    await obtener_pedido(session, pedido_id)
    assignment_result = await session.execute(
        select(Asignacion).where(
            Asignacion.pedido_id == pedido_id,
            Asignacion.activa.is_(True),
        )
    )
    asignacion = assignment_result.scalar_one_or_none()
    if asignacion is None:
        return SeguimientoOutput(
            pedido_id=pedido_id,
            asignacion_id=None,
            repartidor_id=None,
            latitud=None,
            longitud=None,
            fecha_registro=None,
        )

    location_result = await session.execute(
        select(UbicacionTrayecto)
        .where(UbicacionTrayecto.asignacion_id == asignacion.id)
        .order_by(UbicacionTrayecto.fecha_registro.desc())
        .limit(1)
    )
    ubicacion = location_result.scalar_one_or_none()
    return SeguimientoOutput(
        pedido_id=pedido_id,
        asignacion_id=asignacion.id,
        repartidor_id=asignacion.repartidor_id,
        latitud=ubicacion.latitud if ubicacion else None,
        longitud=ubicacion.longitud if ubicacion else None,
        fecha_registro=ubicacion.fecha_registro if ubicacion else None,
    )
