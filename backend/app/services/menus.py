"""Operaciones asíncronas para programar menús y su disponibilidad."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DetalleMenu, Menu, Plato
from app.services.catalogo import obtener_plato
from app.services.errors import (
    ConflictoServicio,
    ErrorValidacion,
    RecursoNoEncontrado,
)


def _validar_stock(stock: int) -> int:
    """Rechaza existencias negativas antes de ejecutar SQL."""
    if stock < 0:
        raise ErrorValidacion("El stock no puede ser negativo.")
    return stock


async def obtener_menu(session: AsyncSession, menu_id: int) -> Menu:
    """Obtiene un menú por identificador o informa que no existe."""
    menu = await session.get(Menu, menu_id)
    if menu is None:
        raise RecursoNoEncontrado("El menú solicitado no existe.")
    return menu


async def obtener_o_crear_menu(
    session: AsyncSession,
    fecha: date,
) -> Menu:
    """Recupera la oferta de una fecha o crea una inactiva."""
    result = await session.execute(select(Menu).where(Menu.fecha == fecha))
    menu = result.scalar_one_or_none()
    if menu is not None:
        return menu

    menu = Menu(fecha=fecha, activo=False)
    session.add(menu)
    await session.flush()
    return menu


async def actualizar_estado_menu(
    session: AsyncSession,
    menu_id: int,
    *,
    activo: bool,
) -> Menu:
    """Activa o desactiva una oferta diaria sin eliminarla."""
    menu = await obtener_menu(session, menu_id)
    menu.activo = activo
    await session.flush()
    return menu


async def agregar_plato_al_menu(
    session: AsyncSession,
    *,
    menu_id: int,
    plato_id: int,
    stock: int,
    disponible: bool = False,
) -> DetalleMenu:
    """Incorpora un plato una sola vez dentro de un menú."""
    await obtener_menu(session, menu_id)
    await obtener_plato(session, plato_id)
    result = await session.execute(
        select(DetalleMenu).where(
            DetalleMenu.menu_id == menu_id,
            DetalleMenu.plato_id == plato_id,
        )
    )
    if result.scalar_one_or_none() is not None:
        raise ConflictoServicio("El plato ya pertenece al menú.")

    detalle = DetalleMenu(
        menu_id=menu_id,
        plato_id=plato_id,
        stock=_validar_stock(stock),
        disponible=disponible,
    )
    session.add(detalle)
    await session.flush()
    return detalle


async def actualizar_oferta(
    session: AsyncSession,
    detalle_id: int,
    *,
    stock: int,
    disponible: bool,
) -> DetalleMenu:
    """Actualiza existencias y visibilidad sin confirmar la transacción."""
    detalle = await session.get(DetalleMenu, detalle_id)
    if detalle is None:
        raise RecursoNoEncontrado("El detalle del menú no existe.")
    detalle.stock = _validar_stock(stock)
    detalle.disponible = disponible
    await session.flush()
    return detalle


async def retirar_plato_del_menu(
    session: AsyncSession,
    detalle_id: int,
) -> DetalleMenu:
    """Oculta una oferta sin borrar el detalle ni su stock."""
    detalle = await session.get(DetalleMenu, detalle_id)
    if detalle is None:
        raise RecursoNoEncontrado("El detalle del menú no existe.")
    detalle.disponible = False
    await session.flush()
    return detalle


async def consultar_oferta_disponible(
    session: AsyncSession,
    fecha: date,
) -> list[tuple[DetalleMenu, Plato]]:
    """Lista platos activos, visibles y con stock para una fecha."""
    statement = (
        select(DetalleMenu, Plato)
        .join(Menu, Menu.id == DetalleMenu.menu_id)
        .join(Plato, Plato.id == DetalleMenu.plato_id)
        .where(
            Menu.fecha == fecha,
            Menu.activo.is_(True),
            DetalleMenu.disponible.is_(True),
            DetalleMenu.stock > 0,
            Plato.activo.is_(True),
        )
        .order_by(Plato.nombre)
    )
    result = await session.execute(statement)
    return list(result.tuples().all())
