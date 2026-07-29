"""Carrito y confirmación atómica de pedidos."""

from collections.abc import Callable
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Cliente,
    DetalleMenu,
    DetallePedido,
    HistorialEstado,
    Menu,
    Pedido,
    Plato,
)
from app.services.errors import (
    ConflictoServicio,
    ErrorValidacion,
    RecursoNoEncontrado,
)


ESTADO_BORRADOR = "BORRADOR"
ESTADO_PENDIENTE_UBICACION = "PENDIENTE_UBICACION"


def _validar_cantidad(cantidad: int) -> int:
    """Exige unidades enteras mayores que cero."""
    if cantidad <= 0:
        raise ErrorValidacion("La cantidad debe ser mayor que cero.")
    return cantidad


def _codigo_aleatorio() -> str:
    """Genera un candidato breve que no contiene datos del cliente."""
    return f"RET-{uuid4().hex[:12].upper()}"


async def obtener_pedido(
    session: AsyncSession,
    pedido_id: int,
) -> Pedido:
    """Obtiene un pedido o informa que no existe."""
    pedido = await session.get(Pedido, pedido_id)
    if pedido is None:
        raise RecursoNoEncontrado("El pedido solicitado no existe.")
    return pedido


def _exigir_borrador(pedido: Pedido) -> None:
    """Protege el carrito después de la confirmación."""
    if pedido.estado_actual != ESTADO_BORRADOR:
        raise ConflictoServicio("El pedido ya no puede modificar su carrito.")


async def obtener_o_crear_borrador(
    session: AsyncSession,
    cliente_id: int,
) -> Pedido:
    """Recupera el borrador activo del cliente o crea uno nuevo."""
    # El bloqueo por cliente serializa dos intentos simultáneos de crear carrito.
    cliente = await session.get(
        Cliente,
        cliente_id,
        with_for_update=True,
    )
    if cliente is None:
        raise RecursoNoEncontrado("El cliente solicitado no existe.")

    result = await session.execute(
        select(Pedido)
        .where(
            Pedido.cliente_id == cliente_id,
            Pedido.estado_actual == ESTADO_BORRADOR,
        )
        .order_by(Pedido.fecha_creacion.desc())
        .limit(1)
    )
    pedido = result.scalar_one_or_none()
    if pedido is not None:
        return pedido

    pedido = Pedido(
        cliente_id=cliente_id,
        estado_actual=ESTADO_BORRADOR,
        total=Decimal("0.00"),
    )
    session.add(pedido)
    await session.flush()
    return pedido


async def _obtener_oferta(
    session: AsyncSession,
    detalle_menu_id: int,
) -> tuple[DetalleMenu, Plato]:
    """Recupera el detalle y su plato para validar el carrito."""
    result = await session.execute(
        select(DetalleMenu, Plato)
        .join(Plato, Plato.id == DetalleMenu.plato_id)
        .join(Menu, Menu.id == DetalleMenu.menu_id)
        .where(
            DetalleMenu.id == detalle_menu_id,
            Menu.activo.is_(True),
        )
    )
    row = result.tuples().one_or_none()
    if row is None:
        raise RecursoNoEncontrado("La oferta solicitada no existe.")
    detalle_menu, plato = row
    if not detalle_menu.disponible or not plato.activo:
        raise ConflictoServicio("El plato no está disponible.")
    return detalle_menu, plato


async def _listar_detalles(
    session: AsyncSession,
    pedido_id: int,
) -> list[DetallePedido]:
    """Lista el contenido actual del carrito."""
    result = await session.execute(
        select(DetallePedido)
        .where(DetallePedido.pedido_id == pedido_id)
        .order_by(DetallePedido.id)
    )
    return list(result.scalars().all())


async def _actualizar_total(
    session: AsyncSession,
    pedido: Pedido,
    detalles: list[DetallePedido] | None = None,
) -> Decimal:
    """Suma subtotales históricos y actualiza la cabecera."""
    contenido = (
        detalles
        if detalles is not None
        else await _listar_detalles(session, pedido.id)
    )
    pedido.total = sum(
        (detalle.subtotal for detalle in contenido),
        start=Decimal("0.00"),
    )
    await session.flush()
    return pedido.total


async def agregar_plato_al_carrito(
    session: AsyncSession,
    *,
    pedido_id: int,
    detalle_menu_id: int,
    cantidad: int,
) -> DetallePedido:
    """Agrega unidades o incrementa el detalle histórico existente."""
    pedido = await obtener_pedido(session, pedido_id)
    _exigir_borrador(pedido)
    cantidad = _validar_cantidad(cantidad)
    oferta, plato = await _obtener_oferta(session, detalle_menu_id)

    result = await session.execute(
        select(DetallePedido).where(
            DetallePedido.pedido_id == pedido_id,
            DetallePedido.plato_id == plato.id,
        )
    )
    detalle = result.scalar_one_or_none()
    nueva_cantidad = cantidad + (detalle.cantidad if detalle else 0)
    if nueva_cantidad > oferta.stock:
        raise ConflictoServicio("El stock disponible es insuficiente.")

    if detalle is None:
        detalle = DetallePedido(
            pedido_id=pedido_id,
            plato_id=plato.id,
            nombre_plato=plato.nombre,
            precio_unitario=plato.precio,
            cantidad=nueva_cantidad,
            subtotal=plato.precio * nueva_cantidad,
        )
        session.add(detalle)
    else:
        detalle.cantidad = nueva_cantidad
        detalle.subtotal = detalle.precio_unitario * nueva_cantidad

    await session.flush()
    await _actualizar_total(session, pedido)
    return detalle


async def modificar_cantidad_carrito(
    session: AsyncSession,
    *,
    detalle_pedido_id: int,
    detalle_menu_id: int,
    cantidad: int,
) -> DetallePedido:
    """Reemplaza la cantidad de un detalle mientras sigue en borrador."""
    cantidad = _validar_cantidad(cantidad)
    detalle = await session.get(DetallePedido, detalle_pedido_id)
    if detalle is None:
        raise RecursoNoEncontrado("El detalle del pedido no existe.")
    pedido = await obtener_pedido(session, detalle.pedido_id)
    _exigir_borrador(pedido)
    oferta, plato = await _obtener_oferta(session, detalle_menu_id)
    if plato.id != detalle.plato_id:
        raise ConflictoServicio("La oferta no corresponde al detalle.")
    if cantidad > oferta.stock:
        raise ConflictoServicio("El stock disponible es insuficiente.")

    detalle.cantidad = cantidad
    detalle.subtotal = detalle.precio_unitario * cantidad
    await session.flush()
    await _actualizar_total(session, pedido)
    return detalle


async def retirar_detalle_carrito(
    session: AsyncSession,
    detalle_pedido_id: int,
) -> Pedido:
    """Elimina una línea del borrador y recalcula su total."""
    detalle = await session.get(DetallePedido, detalle_pedido_id)
    if detalle is None:
        raise RecursoNoEncontrado("El detalle del pedido no existe.")
    pedido = await obtener_pedido(session, detalle.pedido_id)
    _exigir_borrador(pedido)
    await session.delete(detalle)
    await session.flush()
    await _actualizar_total(session, pedido)
    return pedido


async def _generar_codigo_unico(
    session: AsyncSession,
    generador: Callable[[], str],
) -> str:
    """Comprueba candidatos para respetar la unicidad persistente."""
    for _ in range(5):
        candidato = generador()
        result = await session.execute(
            select(Pedido.id).where(
                Pedido.codigo_seguimiento == candidato,
            )
        )
        if result.scalar_one_or_none() is None:
            return candidato
    raise ConflictoServicio("No fue posible generar un código único.")


async def confirmar_pedido(
    session: AsyncSession,
    *,
    pedido_id: int,
    menu_id: int,
    generador_codigo: Callable[[], str] = _codigo_aleatorio,
) -> Pedido:
    """Confirma una vez el carrito y descuenta stock de forma atómica."""
    pedido = await obtener_pedido(session, pedido_id)
    if pedido.estado_actual != ESTADO_BORRADOR:
        if pedido.codigo_seguimiento:
            return pedido
        raise ConflictoServicio("El pedido no admite confirmación.")

    detalles = await _listar_detalles(session, pedido_id)
    if not detalles:
        raise ErrorValidacion("No se puede confirmar un carrito vacío.")

    # Primera fase: bloquear y validar todas las filas sin modificar ninguna.
    ofertas_bloqueadas: list[tuple[DetalleMenu, DetallePedido]] = []
    for detalle in detalles:
        result = await session.execute(
            select(DetalleMenu)
            .join(Menu, Menu.id == DetalleMenu.menu_id)
            .where(
                Menu.id == menu_id,
                Menu.activo.is_(True),
                DetalleMenu.plato_id == detalle.plato_id,
            )
            .with_for_update(of=DetalleMenu)
        )
        oferta = result.scalar_one_or_none()
        if (
            oferta is None
            or not oferta.disponible
            or oferta.stock < detalle.cantidad
        ):
            raise ConflictoServicio(
                f"Stock insuficiente para {detalle.nombre_plato}."
            )
        ofertas_bloqueadas.append((oferta, detalle))

    codigo = await _generar_codigo_unico(session, generador_codigo)

    # Segunda fase: solo se descuenta después de validar el carrito completo.
    for oferta, detalle in ofertas_bloqueadas:
        oferta.stock -= detalle.cantidad
        if oferta.stock == 0:
            oferta.disponible = False

    await _actualizar_total(session, pedido, detalles)
    pedido.codigo_seguimiento = codigo
    pedido.estado_actual = ESTADO_PENDIENTE_UBICACION
    session.add(
        HistorialEstado(
            pedido_id=pedido.id,
            estado_anterior=ESTADO_BORRADOR,
            estado_nuevo=ESTADO_PENDIENTE_UBICACION,
            evento="CONFIRMAR_PEDIDO",
            origen="SISTEMA",
        )
    )
    await session.flush()
    return pedido
