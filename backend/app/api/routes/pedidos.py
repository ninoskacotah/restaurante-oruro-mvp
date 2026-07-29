"""Endpoints administrativos de pedidos, pagos y seguimiento."""

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.dependencies import AuthDependency, SessionDependency
from app.models import (
    Asignacion,
    ComprobantePago,
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
    session: SessionDependency,
    auth: AuthDependency,
) -> Pedido:
    """Aprueba o rechaza un comprobante mediante el actor autenticado."""
    return await revisar_comprobante_pago(
        session,
        comprobante_id=comprobante_id,
        administrador_id=auth.administrador.id,
        aprobado=data.aprobado,
        observacion=data.observacion,
    )


@router.post(
    "/pedidos/{pedido_id}/asignaciones",
    response_model=AsignacionOutput,
    status_code=status.HTTP_201_CREATED,
)
async def assign_delivery(
    pedido_id: int,
    data: AsignacionInput,
    session: SessionDependency,
    auth: AuthDependency,
) -> Asignacion:
    """Asigna o reasigna un repartidor desde el panel."""
    return await asignar_repartidor(
        session,
        pedido_id=pedido_id,
        repartidor_id=data.repartidor_id,
        administrador_id=auth.administrador.id,
    )


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
