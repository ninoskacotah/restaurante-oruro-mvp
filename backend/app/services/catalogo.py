"""Operaciones asíncronas para administrar el catálogo de platos."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Plato
from app.services.errors import ErrorValidacion, RecursoNoEncontrado


def _validar_nombre(nombre: str) -> str:
    """Normaliza un nombre y rechaza valores formados solo por espacios."""
    nombre_limpio = nombre.strip()
    if not nombre_limpio:
        raise ErrorValidacion("El nombre del plato es obligatorio.")
    return nombre_limpio


def _validar_precio(precio: Decimal) -> Decimal:
    """Evita que un precio negativo llegue a la capa de persistencia."""
    if precio < 0:
        raise ErrorValidacion("El precio del plato no puede ser negativo.")
    return precio


async def crear_plato(
    session: AsyncSession,
    *,
    nombre: str,
    descripcion: str | None,
    precio: Decimal,
) -> Plato:
    """Crea un plato inactivo sin confirmar la transacción."""
    plato = Plato(
        nombre=_validar_nombre(nombre),
        descripcion=descripcion.strip() if descripcion else None,
        precio=_validar_precio(precio),
        activo=False,
    )
    session.add(plato)
    await session.flush()
    return plato


async def obtener_plato(session: AsyncSession, plato_id: int) -> Plato:
    """Obtiene un plato por identificador o informa que no existe."""
    plato = await session.get(Plato, plato_id)
    if plato is None:
        raise RecursoNoEncontrado("El plato solicitado no existe.")
    return plato


async def actualizar_plato(
    session: AsyncSession,
    plato_id: int,
    *,
    nombre: str,
    descripcion: str | None,
    precio: Decimal,
    activo: bool,
) -> Plato:
    """Reemplaza los datos editables de un plato existente."""
    plato = await obtener_plato(session, plato_id)
    plato.nombre = _validar_nombre(nombre)
    plato.descripcion = descripcion.strip() if descripcion else None
    plato.precio = _validar_precio(precio)
    plato.activo = activo
    await session.flush()
    return plato


async def desactivar_plato(
    session: AsyncSession,
    plato_id: int,
) -> Plato:
    """Desactiva el plato sin eliminar su información histórica."""
    plato = await obtener_plato(session, plato_id)
    plato.activo = False
    await session.flush()
    return plato
