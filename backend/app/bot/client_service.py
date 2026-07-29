"""Consultas y formato compartidos por los handlers del cliente."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Cliente, DetalleMenu, DetallePedido, Pedido
from app.services.menus import consultar_oferta_disponible


async def get_or_create_client(
    session: AsyncSession,
    *,
    chat_id: int,
    name: str | None,
) -> Cliente:
    """Reconoce al cliente por chat o persiste su perfil mínimo."""
    result = await session.execute(
        select(Cliente).where(Cliente.chat_id == str(chat_id))
    )
    client = result.scalar_one_or_none()
    clean_name = name.strip() if name else None
    if client is None:
        client = Cliente(chat_id=str(chat_id), nombre=clean_name)
        session.add(client)
        await session.flush()
    elif clean_name and client.nombre != clean_name:
        client.nombre = clean_name
        await session.flush()
    return client


async def current_menu(session: AsyncSession, today: date):
    """Devuelve la oferta filtrada y el menú al que pertenece."""
    offers = await consultar_oferta_disponible(session, today)
    menu_id = offers[0][0].menu_id if offers else None
    return menu_id, offers


async def client_order(
    session: AsyncSession,
    *,
    client_id: int,
    states: set[str],
) -> Pedido | None:
    """Recupera el pedido más reciente del cliente en uno de los estados."""
    result = await session.execute(
        select(Pedido)
        .where(
            Pedido.cliente_id == client_id,
            Pedido.estado_actual.in_(states),
        )
        .order_by(Pedido.fecha_creacion.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def cart_lines(
    session: AsyncSession,
    pedido_id: int,
) -> list[DetallePedido]:
    """Lista las líneas persistidas del carrito."""
    result = await session.execute(
        select(DetallePedido)
        .where(DetallePedido.pedido_id == pedido_id)
        .order_by(DetallePedido.id)
    )
    return list(result.scalars().all())


async def menu_detail_for_line(
    session: AsyncSession,
    line: DetallePedido,
    menu_id: int,
) -> DetalleMenu | None:
    """Localiza la oferta necesaria para validar una modificación."""
    result = await session.execute(
        select(DetalleMenu).where(
            DetalleMenu.menu_id == menu_id,
            DetalleMenu.plato_id == line.plato_id,
        )
    )
    return result.scalar_one_or_none()


def format_cart(lines: list[DetallePedido], total: Decimal) -> str:
    """Presenta cantidades e importes sin recalcular reglas del negocio."""
    if not lines:
        return "Tu carrito está vacío."
    detail = "\n".join(
        f"• {line.cantidad} × {line.nombre_plato}: Bs {line.subtotal:.2f}"
        for line in lines
    )
    return f"Tu carrito:\n{detail}\n\nTotal: Bs {total:.2f}"
