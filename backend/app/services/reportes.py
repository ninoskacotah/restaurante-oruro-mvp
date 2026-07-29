"""Cálculos administrativos derivados exclusivamente de datos persistidos."""

from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DetallePedido, HistorialEstado, Pedido


COUNTED_SALE_STATES = {
    "PAGO_CONFIRMADO",
    "ASIGNADO",
    "ACEPTADO_REPARTIDOR",
    "EN_CAMINO",
    "EN_DESTINO",
    "ENTREGADO",
}


async def daily_sales(
    session: AsyncSession,
    target_date: date,
) -> tuple[Decimal, int]:
    """Suma pedidos válidos creados en la fecha solicitada."""
    result = await session.execute(
        select(
            func.coalesce(func.sum(Pedido.total), 0),
            func.count(Pedido.id),
        ).where(
            func.date(Pedido.fecha_creacion) == target_date,
            Pedido.estado_actual.in_(COUNTED_SALE_STATES),
        )
    )
    total, count = result.one()
    return Decimal(total).quantize(Decimal("0.01")), int(count)


async def popular_dishes(
    session: AsyncSession,
    target_date: date,
) -> list[tuple[int, str, int]]:
    """Agrupa unidades reales vendidas y ordena las más solicitadas."""
    result = await session.execute(
        select(
            DetallePedido.plato_id,
            DetallePedido.nombre_plato,
            func.sum(DetallePedido.cantidad).label("cantidad"),
        )
        .join(Pedido, Pedido.id == DetallePedido.pedido_id)
        .where(
            func.date(Pedido.fecha_creacion) == target_date,
            Pedido.estado_actual.in_(COUNTED_SALE_STATES),
        )
        .group_by(DetallePedido.plato_id, DetallePedido.nombre_plato)
        .order_by(func.sum(DetallePedido.cantidad).desc())
        .limit(10)
    )
    return [
        (int(plato_id), nombre, int(cantidad))
        for plato_id, nombre, cantidad in result.all()
    ]


async def average_delivery_minutes(
    session: AsyncSession,
    target_date: date,
) -> Decimal | None:
    """Promedia trayectos completos usando eventos en camino y entregado."""
    result = await session.execute(
        select(HistorialEstado).where(
            func.date(HistorialEstado.fecha_registro) == target_date,
            HistorialEstado.estado_nuevo.in_({"EN_CAMINO", "ENTREGADO"}),
        )
    )
    events: dict[int, dict[str, object]] = defaultdict(dict)
    for event in result.scalars().all():
        events[event.pedido_id][event.estado_nuevo] = event.fecha_registro

    durations: list[Decimal] = []
    for order_events in events.values():
        started = order_events.get("EN_CAMINO")
        delivered = order_events.get("ENTREGADO")
        if started is not None and delivered is not None and delivered >= started:
            durations.append(
                Decimal(str((delivered - started).total_seconds() / 60))
            )
    if not durations:
        return None
    average = sum(durations, Decimal("0")) / len(durations)
    return average.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
