"""Handlers del flujo completo del cliente."""

from datetime import date
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.client_service import (
    cart_lines,
    client_order,
    current_menu,
    format_cart,
    get_or_create_client,
    menu_detail_for_line,
)
from app.bot.keyboards import cart_keyboard, menu_keyboard
from app.bot.states import ClientOrderStates
from app.bot.storage import payment_receipt_path, resolve_media_path
from app.core.config import Settings
from app.db.session import SessionFactory, session_scope
from app.models import DetallePedido
from app.services.ciclo_pedido import (
    ESTADO_PENDIENTE_COMPROBANTE,
    ESTADO_PENDIENTE_UBICACION,
    cancelar_pedido,
    registrar_comprobante_pago,
    registrar_ubicacion_entrega,
)
from app.services.errors import ErrorServicio
from app.services.pedidos import (
    ESTADO_BORRADOR,
    agregar_plato_al_carrito,
    confirmar_pedido,
    modificar_cantidad_carrito,
    obtener_o_crear_borrador,
    retirar_detalle_carrito,
)


router = Router(name="cliente")
ACTIVE_STATES = {
    ESTADO_BORRADOR,
    ESTADO_PENDIENTE_UBICACION,
    ESTADO_PENDIENTE_COMPROBANTE,
    "PAGO_EN_REVISION",
    "PAGO_CONFIRMADO",
    "ASIGNADO",
    "ACEPTADO_REPARTIDOR",
    "EN_CAMINO",
    "EN_DESTINO",
}


async def _client(session: AsyncSession, message: Message):
    """Obtiene el actor a partir de los datos nativos de Telegram."""
    user = message.from_user
    return await get_or_create_client(
        session,
        chat_id=message.chat.id,
        name=user.full_name if user else None,
    )


async def _show_menu(message: Message, session: AsyncSession) -> None:
    """Presenta la oferta vigente o una respuesta controlada."""
    _, offers = await current_menu(session, date.today())
    if not offers:
        await message.answer(
            "Hoy no existe un menú habilitado con stock disponible."
        )
        return
    await message.answer(
        "Menú disponible de Restaurant Las Retamas:",
        reply_markup=menu_keyboard(offers),
    )


@router.message(CommandStart())
@router.message(Command("reiniciar"))
async def start_or_restart(
    message: Message,
    state: FSMContext,
    session_factory: SessionFactory,
) -> None:
    """Registra al cliente y reinicia solo el contexto conversacional."""
    await state.clear()
    async with session_scope(session_factory) as session:
        await _client(session, message)
        await _show_menu(message, session)


@router.callback_query(F.data == "client:menu")
async def show_menu_callback(
    callback: CallbackQuery,
    session_factory: SessionFactory,
) -> None:
    """Actualiza el menú cuando el cliente decide seguir comprando."""
    await callback.answer()
    if callback.message is None:
        return
    async with session_scope(session_factory) as session:
        await _show_menu(callback.message, session)


@router.callback_query(F.data.startswith("client:add:"))
async def select_offer(callback: CallbackQuery, state: FSMContext) -> None:
    """Conserva la oferta seleccionada hasta recibir una cantidad."""
    await callback.answer()
    if callback.message is None or callback.data is None:
        return
    _, _, offer_id, menu_id = callback.data.split(":")
    await state.set_state(ClientOrderStates.waiting_quantity)
    await state.update_data(
        action="add",
        offer_id=int(offer_id),
        menu_id=int(menu_id),
    )
    await callback.message.answer("Escribe la cantidad que deseas agregar.")


@router.callback_query(F.data.startswith("client:edit:"))
async def select_line_to_edit(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    """Solicita la nueva cantidad de una línea existente."""
    await callback.answer()
    if callback.message is None or callback.data is None:
        return
    line_id = int(callback.data.rsplit(":", 1)[1])
    await state.set_state(ClientOrderStates.waiting_quantity)
    await state.update_data(action="edit", line_id=line_id)
    await callback.message.answer("Escribe la nueva cantidad.")


@router.message(ClientOrderStates.waiting_quantity)
async def receive_quantity(
    message: Message,
    state: FSMContext,
    session_factory: SessionFactory,
) -> None:
    """Valida la entrada y delega stock, total e idempotencia al dominio."""
    try:
        quantity = int(message.text or "")
        if quantity <= 0:
            raise ValueError
    except ValueError:
        await message.answer("La cantidad debe ser un número entero mayor a cero.")
        return

    data = await state.get_data()
    try:
        async with session_scope(session_factory) as session:
            client = await _client(session, message)
            order = await obtener_o_crear_borrador(session, client.id)
            if data.get("action") == "add":
                await agregar_plato_al_carrito(
                    session,
                    pedido_id=order.id,
                    detalle_menu_id=int(data["offer_id"]),
                    cantidad=quantity,
                )
            else:
                line = await session.get(DetallePedido, int(data["line_id"]))
                if line is None or line.pedido_id != order.id:
                    await message.answer("La línea del carrito ya no existe.")
                    return
                offer = await menu_detail_for_line(
                    session,
                    line,
                    int(order.menu_id or data.get("menu_id") or 0),
                )
                if offer is None:
                    _, offers = await current_menu(session, date.today())
                    offer = next(
                        (
                            detail
                            for detail, _ in offers
                            if detail.plato_id == line.plato_id
                        ),
                        None,
                    )
                if offer is None:
                    await message.answer("El plato ya no está disponible.")
                    return
                await modificar_cantidad_carrito(
                    session,
                    detalle_pedido_id=line.id,
                    detalle_menu_id=offer.id,
                    cantidad=quantity,
                )
        await state.clear()
        await message.answer("Carrito actualizado.")
    except ErrorServicio as error:
        await message.answer(str(error))


@router.callback_query(F.data == "client:cart")
async def show_cart(
    callback: CallbackQuery,
    session_factory: SessionFactory,
) -> None:
    """Muestra el carrito persistente con su total."""
    await callback.answer()
    if callback.message is None:
        return
    async with session_scope(session_factory) as session:
        client = await _client(session, callback.message)
        order = await obtener_o_crear_borrador(session, client.id)
        lines = await cart_lines(session, order.id)
        await callback.message.answer(
            format_cart(lines, order.total),
            reply_markup=cart_keyboard(lines),
        )


@router.callback_query(F.data.startswith("client:remove:"))
async def remove_line(
    callback: CallbackQuery,
    session_factory: SessionFactory,
) -> None:
    """Elimina una línea solo si pertenece al borrador del chat."""
    await callback.answer()
    if callback.message is None or callback.data is None:
        return
    line_id = int(callback.data.rsplit(":", 1)[1])
    try:
        async with session_scope(session_factory) as session:
            client = await _client(session, callback.message)
            order = await obtener_o_crear_borrador(session, client.id)
            line = await session.get(DetallePedido, line_id)
            if line is None or line.pedido_id != order.id:
                await callback.message.answer("La línea ya no existe.")
                return
            await retirar_detalle_carrito(session, line_id)
        await callback.message.answer("Plato eliminado del carrito.")
    except ErrorServicio as error:
        await callback.message.answer(str(error))


@router.callback_query(F.data == "client:confirm")
async def confirm_order(
    callback: CallbackQuery,
    session_factory: SessionFactory,
) -> None:
    """Confirma una sola vez y solicita el objeto Location."""
    await callback.answer()
    if callback.message is None:
        return
    try:
        async with session_scope(session_factory) as session:
            client = await _client(session, callback.message)
            order = await obtener_o_crear_borrador(session, client.id)
            menu_id, _ = await current_menu(session, date.today())
            if menu_id is None:
                await callback.message.answer("El menú ya no está disponible.")
                return
            order = await confirmar_pedido(
                session,
                pedido_id=order.id,
                menu_id=menu_id,
            )
        location_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="Compartir ubicación",
                        request_location=True,
                    )
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await callback.message.answer(
            f"Pedido {order.codigo_seguimiento} confirmado. "
            "Comparte la ubicación de entrega.",
            reply_markup=location_keyboard,
        )
    except ErrorServicio as error:
        await callback.message.answer(str(error))


@router.message(F.location)
async def receive_location(
    message: Message,
    session_factory: SessionFactory,
    settings: Settings,
) -> None:
    """Registra el destino y envía el QR como fotografía."""
    assert message.location is not None
    try:
        async with session_scope(session_factory) as session:
            client = await _client(session, message)
            order = await client_order(
                session,
                client_id=client.id,
                states={ESTADO_PENDIENTE_UBICACION},
            )
            if order is None:
                await message.answer("No existe un pedido esperando ubicación.")
                return
            await registrar_ubicacion_entrega(
                session,
                pedido_id=order.id,
                latitud=message.location.latitude,
                longitud=message.location.longitude,
                referencia=None,
                cliente_id=client.id,
            )
        qr_path = settings.payment_qr_path
        if not qr_path.is_file():
            await message.answer(
                "La ubicación fue registrada, pero el QR todavía no está "
                "configurado. Contacta al restaurante."
            )
            return
        await message.answer_photo(
            FSInputFile(qr_path),
            caption=(
                "Realiza el pago y envía aquí una fotografía del comprobante. "
                "La verificación será manual."
            ),
        )
    except ErrorServicio as error:
        await message.answer(str(error))


@router.message(F.photo)
async def receive_receipt(
    message: Message,
    session_factory: SessionFactory,
    settings: Settings,
) -> None:
    """Descarga la mejor fotografía y registra sus metadatos."""
    assert message.photo
    photo = message.photo[-1]
    relative = payment_receipt_path(settings.media_root, "image/jpeg")
    target = resolve_media_path(settings.media_root, relative)
    await message.bot.download(photo, destination=target)
    try:
        async with session_scope(session_factory) as session:
            client = await _client(session, message)
            order = await client_order(
                session,
                client_id=client.id,
                states={ESTADO_PENDIENTE_COMPROBANTE},
            )
            if order is None:
                target.unlink(missing_ok=True)
                await message.answer("No existe un pedido esperando comprobante.")
                return
            await registrar_comprobante_pago(
                session,
                pedido_id=order.id,
                cliente_id=client.id,
                archivo_referencia=relative.as_posix(),
                nombre_generado=Path(target).name,
                tipo_mime="image/jpeg",
                tamanio_bytes=photo.file_size or target.stat().st_size,
            )
        await message.answer(
            "Comprobante recibido. El pago será verificado manualmente "
            "por el restaurante."
        )
    except Exception:
        target.unlink(missing_ok=True)
        raise


@router.message(Command("cancelar"))
async def cancel_flow(
    message: Message,
    state: FSMContext,
    session_factory: SessionFactory,
) -> None:
    """Cancela el pedido confirmado o reinicia un borrador sin duplicar stock."""
    await state.clear()
    try:
        async with session_scope(session_factory) as session:
            client = await _client(session, message)
            order = await client_order(
                session,
                client_id=client.id,
                states=ACTIVE_STATES,
            )
            if order is None or order.estado_actual == ESTADO_BORRADOR:
                await message.answer(
                    "Flujo reiniciado. Tu carrito permanece disponible."
                )
                return
            await cancelar_pedido(
                session,
                pedido_id=order.id,
                motivo="SOLICITUD_CLIENTE",
                origen="CLIENTE",
                cliente_id=client.id,
            )
        await message.answer("Pedido cancelado correctamente.")
    except ErrorServicio as error:
        await message.answer(str(error))


@router.message()
async def unexpected_message(message: Message) -> None:
    """Responde con sentido cuando la entrada no corresponde al paso actual."""
    await message.answer(
        "No puedo usar ese mensaje en este momento. "
        "Usa /reiniciar para ver el menú o /cancelar para detener el flujo."
    )
