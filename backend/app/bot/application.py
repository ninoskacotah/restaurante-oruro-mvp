"""Construcción del dispatcher sin abrir conexiones externas."""

from aiogram import Dispatcher

from app.bot.handlers.client import router as client_router


def create_dispatcher() -> Dispatcher:
    """Registra los routers del MVP en un dispatcher comprobable."""
    dispatcher = Dispatcher()
    dispatcher.include_router(client_router)
    return dispatcher
