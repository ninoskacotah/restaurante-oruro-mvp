"""Punto de entrada del bot para ejecución mediante long polling."""

import asyncio

from aiogram import Bot

from app.bot.application import create_dispatcher
from app.core.config import get_settings
from app.db.session import (
    create_database_engine,
    create_session_factory,
    dispose_database_engine,
)


async def main() -> None:
    """Inicia Telegram y libera el motor al terminar."""
    settings = get_settings()
    engine = create_database_engine(str(settings.database_url))
    session_factory = create_session_factory(engine)
    bot = Bot(token=settings.telegram_bot_token.get_secret_value())
    dispatcher = create_dispatcher()
    try:
        await dispatcher.start_polling(
            bot,
            session_factory=session_factory,
            settings=settings,
        )
    finally:
        await bot.session.close()
        await dispose_database_engine(engine)


if __name__ == "__main__":
    asyncio.run(main())
