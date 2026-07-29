"""Acciones inline disponibles según el estado del reparto."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import Asignacion, Pedido


def delivery_keyboard(
    assignment: Asignacion,
    order: Pedido,
) -> InlineKeyboardMarkup:
    """Muestra únicamente la siguiente acción válida del repartidor."""
    actions = {
        "ASIGNADO": ("Confirmar recepción", "ack"),
        "ACEPTADO_REPARTIDOR": ("Iniciar trayecto", "start"),
        "EN_CAMINO": ("Registrar llegada", "arrive"),
    }
    action = actions.get(order.estado_actual)
    rows = []
    if action is not None:
        text, code = action
        rows.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"delivery:{code}:{assignment.id}",
                )
            ]
        )
    if order.estado_actual == "EN_DESTINO":
        rows.append(
            [
                InlineKeyboardButton(
                    text="Cómo confirmar entrega",
                    callback_data=f"delivery:evidence:{assignment.id}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)
