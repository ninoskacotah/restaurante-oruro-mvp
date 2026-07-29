"""Consultas y presentación de la operación del repartidor."""

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Asignacion, Cliente, DetallePedido, Pedido, Repartidor


@dataclass(frozen=True)
class DeliverySummary:
    """Datos necesarios para atender una asignación sin exponer secretos."""

    assignment: Asignacion
    order: Pedido
    client: Cliente
    lines: list[DetallePedido]


async def authenticated_courier(
    session: AsyncSession,
    chat_id: int,
) -> Repartidor | None:
    """Autentica por la lista de chats registrada desde el panel."""
    result = await session.execute(
        select(Repartidor).where(
            Repartidor.chat_id == str(chat_id),
            Repartidor.activo.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def active_delivery(
    session: AsyncSession,
    courier_id: int,
) -> DeliverySummary | None:
    """Obtiene solo la asignación activa del repartidor autenticado."""
    result = await session.execute(
        select(Asignacion, Pedido, Cliente)
        .join(Pedido, Pedido.id == Asignacion.pedido_id)
        .join(Cliente, Cliente.id == Pedido.cliente_id)
        .where(
            Asignacion.repartidor_id == courier_id,
            Asignacion.activa.is_(True),
        )
        .order_by(Asignacion.fecha_asignacion.desc())
        .limit(1)
    )
    row = result.tuples().one_or_none()
    if row is None:
        return None
    assignment, order, client = row
    line_result = await session.execute(
        select(DetallePedido)
        .where(DetallePedido.pedido_id == order.id)
        .order_by(DetallePedido.id)
    )
    return DeliverySummary(
        assignment=assignment,
        order=order,
        client=client,
        lines=list(line_result.scalars().all()),
    )


def format_delivery(summary: DeliverySummary) -> str:
    """Construye el detalle operativo solicitado para la entrega."""
    dishes = "\n".join(
        f"• {line.cantidad} × {line.nombre_plato}"
        for line in summary.lines
    )
    client_name = summary.client.nombre or "Sin nombre registrado"
    phone = summary.client.telefono or "Sin teléfono registrado"
    reference = summary.order.referencia_entrega or "Sin referencia"
    payment = (
        "Confirmado"
        if summary.order.estado_actual
        not in {"PAGO_EN_REVISION", "PENDIENTE_COMPROBANTE"}
        else "Pendiente"
    )
    return (
        f"Pedido {summary.order.codigo_seguimiento}\n"
        f"{dishes}\n\n"
        f"Total: Bs {Decimal(summary.order.total):.2f}\n"
        f"Pago: {payment}\n"
        f"Cliente: {client_name}\n"
        f"Contacto: {phone}\n"
        f"Referencia: {reference}\n"
        f"Estado: {summary.order.estado_actual}"
    )
