"""Mensajes salientes derivados de estados persistentes."""

from aiogram import Bot


STATE_MESSAGES = {
    "PAGO_CONFIRMADO": "Tu pago fue confirmado.",
    "PAGO_RECHAZADO": (
        "Tu comprobante fue rechazado. "
        "Envía una nueva fotografía para revisión."
    ),
    "ASIGNADO": "Tu pedido fue asignado a un repartidor.",
    "EN_CAMINO": "Tu pedido está en camino.",
    "EN_DESTINO": "El repartidor llegó al destino.",
    "ENTREGADO": "Tu pedido fue entregado. ¡Gracias por elegirnos!",
    "CANCELADO": "Tu pedido fue cancelado.",
}


async def notify_client_state(
    bot: Bot,
    *,
    chat_id: str,
    tracking_code: str,
    state: str,
) -> bool:
    """Notifica únicamente estados que tienen un mensaje para el cliente."""
    message = STATE_MESSAGES.get(state)
    if message is None:
        return False
    await bot.send_message(
        chat_id=chat_id,
        text=f"Pedido {tracking_code}: {message}",
    )
    return True
