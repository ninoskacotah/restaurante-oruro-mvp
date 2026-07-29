"""Construcción del dispatcher sin abrir conexiones externas."""

from aiogram import Dispatcher

from app.bot.handlers.client import router as client_router
from app.bot.handlers.delivery import router as delivery_router


def create_dispatcher() -> Dispatcher:
    """Registra los routers del MVP en un dispatcher comprobable."""
    dispatcher = Dispatcher()
    # El rol repartidor se evalúa primero para que sus fotos y ubicaciones no
    # sean interpretadas como entradas del flujo del cliente.
    dispatcher.include_router(delivery_router)
    dispatcher.include_router(client_router)
    return dispatcher
