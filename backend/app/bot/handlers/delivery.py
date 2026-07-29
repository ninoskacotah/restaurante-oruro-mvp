"""Handlers exclusivos del repartidor autenticado."""

from pathlib import Path

from aiogram import F, Router
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.bot.delivery_keyboards import delivery_keyboard
from app.bot.delivery_service import (
    active_delivery,
    authenticated_courier,
    format_delivery,
)
from app.bot.notifications import notify_client_state
from app.bot.storage import delivery_evidence_path, resolve_media_path
from app.core.config import Settings
from app.db.session import SessionFactory, session_scope
from app.services.errors import ErrorServicio
from app.services.reparto import (
    acusar_recepcion,
    confirmar_entrega,
    iniciar_trayecto,
    registrar_llegada,
    registrar_ubicacion_trayecto,
)


router = Router(name="repartidor")


async def _show_delivery(
    message: Message,
    session_factory: SessionFactory,
) -> None:
    """Autentica el chat y presenta solamente su asignación vigente."""
    async with session_scope(session_factory) as session:
        courier = await authenticated_courier(session, message.chat.id)
        if courier is None:
            await message.answer(
                "Este chat no está registrado como repartidor habilitado."
            )
            return
        summary = await active_delivery(session, courier.id)
        if summary is None:
            await message.answer("No tienes un pedido asignado actualmente.")
            return
        await message.answer(
            format_delivery(summary),
            reply_markup=delivery_keyboard(
                summary.assignment,
                summary.order,
            ),
        )
        if (
            summary.order.entrega_latitud is not None
            and summary.order.entrega_longitud is not None
        ):
            await message.answer_location(
                latitude=float(summary.order.entrega_latitud),
                longitude=float(summary.order.entrega_longitud),
            )


@router.message(Command("repartidor"))
@router.message(Command("mi_entrega"))
async def show_delivery(
    message: Message,
    session_factory: SessionFactory,
) -> None:
    """Punto de entrada diferenciado del rol repartidor."""
    await _show_delivery(message, session_factory)


async def _notify_client(
    message: Message,
    *,
    chat_id: str,
    tracking_code: str,
    state: str,
) -> None:
    """Envía la notificación fuera de la transacción de base de datos."""
    await notify_client_state(
        message.bot,
        chat_id=chat_id,
        tracking_code=tracking_code,
        state=state,
    )


@router.callback_query(F.data.startswith("delivery:"))
async def delivery_action(
    callback: CallbackQuery,
    session_factory: SessionFactory,
) -> None:
    """Ejecuta acuse, inicio o llegada con autorización persistente."""
    await callback.answer()
    if callback.message is None or callback.data is None:
        return
    _, action, assignment_text = callback.data.split(":")
    assignment_id = int(assignment_text)
    if action == "evidence":
        await callback.message.answer(
            "Envía una fotografía o usa /entrega CODIGO para confirmar."
        )
        return
    try:
        async with session_scope(session_factory) as session:
            courier = await authenticated_courier(
                session,
                callback.message.chat.id,
            )
            if courier is None:
                await callback.message.answer("Repartidor no autorizado.")
                return
            summary = await active_delivery(session, courier.id)
            if summary is None or summary.assignment.id != assignment_id:
                await callback.message.answer(
                    "La asignación ya no está activa. Usa /mi_entrega."
                )
                return
            if action == "ack":
                await acusar_recepcion(
                    session,
                    asignacion_id=assignment_id,
                    repartidor_id=courier.id,
                )
                notify_state = None
            elif action == "start":
                await iniciar_trayecto(
                    session,
                    asignacion_id=assignment_id,
                    repartidor_id=courier.id,
                )
                notify_state = "EN_CAMINO"
            elif action == "arrive":
                await registrar_llegada(
                    session,
                    asignacion_id=assignment_id,
                    repartidor_id=courier.id,
                )
                notify_state = "EN_DESTINO"
            else:
                await callback.message.answer("Acción no reconocida.")
                return
            chat_id = summary.client.chat_id
            tracking = summary.order.codigo_seguimiento or str(summary.order.id)
        if notify_state:
            await _notify_client(
                callback.message,
                chat_id=chat_id,
                tracking_code=tracking,
                state=notify_state,
            )
        await callback.message.answer("Estado actualizado correctamente.")
        await _show_delivery(callback.message, session_factory)
    except ErrorServicio as error:
        await callback.message.answer(str(error))


@router.message(F.location)
@router.edited_message(F.location)
async def receive_live_location(
    message: Message,
    session_factory: SessionFactory,
) -> None:
    """Persiste cada actualización de live location de la asignación activa."""
    assert message.location is not None
    if message.location.live_period is None:
        await message.answer(
            "Comparte una ubicación en vivo para iniciar el seguimiento."
        )
        return
    async with session_scope(session_factory) as session:
        courier = await authenticated_courier(session, message.chat.id)
        if courier is None:
            raise SkipHandler
        summary = await active_delivery(session, courier.id)
        if summary is None or summary.order.estado_actual != "EN_CAMINO":
            await message.answer("No tienes un trayecto activo.")
            return
        try:
            await registrar_ubicacion_trayecto(
                session,
                asignacion_id=summary.assignment.id,
                repartidor_id=courier.id,
                latitud=message.location.latitude,
                longitud=message.location.longitude,
            )
        except ErrorServicio as error:
            await message.answer(str(error))
            return
    await message.answer(
        "Ubicación actualizada. Telegram seguirá enviando cambios mientras "
        "la ubicación en vivo permanezca activa."
    )


@router.message(F.photo)
async def receive_delivery_photo(
    message: Message,
    session_factory: SessionFactory,
    settings: Settings,
) -> None:
    """Conserva una fotografía como evidencia y completa la entrega."""
    assert message.photo
    async with session_scope(session_factory) as session:
        courier = await authenticated_courier(session, message.chat.id)
        if courier is None:
            raise SkipHandler
        summary = await active_delivery(session, courier.id)
        if summary is None or summary.order.estado_actual != "EN_DESTINO":
            raise SkipHandler
        assignment_id = summary.assignment.id
        courier_id = courier.id
        client_chat = summary.client.chat_id
        tracking = summary.order.codigo_seguimiento or str(summary.order.id)

    photo = message.photo[-1]
    relative = delivery_evidence_path(settings.media_root, "image/jpeg")
    target = resolve_media_path(settings.media_root, relative)
    await message.bot.download(photo, destination=target)
    try:
        async with session_scope(session_factory) as session:
            await confirmar_entrega(
                session,
                asignacion_id=assignment_id,
                repartidor_id=courier_id,
                tipo="FOTOGRAFIA",
                valor_referencia=relative.as_posix(),
                tipo_mime="image/jpeg",
                tamanio_bytes=photo.file_size or target.stat().st_size,
            )
        await _notify_client(
            message,
            chat_id=client_chat,
            tracking_code=tracking,
            state="ENTREGADO",
        )
        await message.answer("Entrega confirmada con fotografía.")
    except Exception:
        target.unlink(missing_ok=True)
        raise


@router.message(Command("entrega"))
async def receive_delivery_code(
    message: Message,
    session_factory: SessionFactory,
) -> None:
    """Admite el código proporcionado por el cliente como evidencia."""
    code = (message.text or "").partition(" ")[2].strip()
    if not code:
        await message.answer("Usa /entrega seguido del código recibido.")
        return
    try:
        async with session_scope(session_factory) as session:
            courier = await authenticated_courier(session, message.chat.id)
            if courier is None:
                await message.answer("Repartidor no autorizado.")
                return
            summary = await active_delivery(session, courier.id)
            if summary is None:
                await message.answer("No tienes una asignación activa.")
                return
            await confirmar_entrega(
                session,
                asignacion_id=summary.assignment.id,
                repartidor_id=courier.id,
                tipo="CODIGO",
                valor_referencia=code,
            )
            client_chat = summary.client.chat_id
            tracking = summary.order.codigo_seguimiento or str(summary.order.id)
        await _notify_client(
            message,
            chat_id=client_chat,
            tracking_code=tracking,
            state="ENTREGADO",
        )
        await message.answer("Entrega confirmada con código.")
    except ErrorServicio as error:
        await message.answer(str(error))
