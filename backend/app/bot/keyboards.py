"""Teclados inline del flujo del cliente."""

from decimal import Decimal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import DetalleMenu, DetallePedido, Plato


def menu_keyboard(
    offers: list[tuple[DetalleMenu, Plato]],
) -> InlineKeyboardMarkup:
    """Construye el menú exclusivamente desde ofertas persistidas."""
    rows = [
        [
            InlineKeyboardButton(
                text=f"{plato.nombre} — Bs {Decimal(plato.precio):.2f}",
                callback_data=f"client:add:{detail.id}:{detail.menu_id}",
            )
        ]
        for detail, plato in offers
    ]
    rows.append(
        [
            InlineKeyboardButton(
                text="Ver carrito",
                callback_data="client:cart",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cart_keyboard(lines: list[DetallePedido]) -> InlineKeyboardMarkup:
    """Ofrece editar líneas, continuar comprando o confirmar."""
    line_rows = [
        [
            InlineKeyboardButton(
                text=f"Modificar {line.nombre_plato}",
                callback_data=f"client:edit:{line.id}",
            ),
            InlineKeyboardButton(
                text="Eliminar",
                callback_data=f"client:remove:{line.id}",
            ),
        ]
        for line in lines
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=line_rows
        + [
            [
                InlineKeyboardButton(
                    text="Seguir comprando",
                    callback_data="client:menu",
                ),
                InlineKeyboardButton(
                    text="Confirmar pedido",
                    callback_data="client:confirm",
                ),
            ]
        ]
    )
