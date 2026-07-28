"""Motor y sesiones asíncronas para PostgreSQL."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


SessionFactory = async_sessionmaker[AsyncSession]


def create_database_engine(database_url: str) -> AsyncEngine:
    """Construye un motor sin abrir una conexión inmediatamente."""
    return create_async_engine(database_url, pool_pre_ping=True)


def create_session_factory(engine: AsyncEngine) -> SessionFactory:
    """Crea sesiones que conservan sus atributos después del commit."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@asynccontextmanager
async def session_scope(
    session_factory: SessionFactory,
) -> AsyncIterator[AsyncSession]:
    """Confirma una unidad de trabajo o la revierte ante un error."""
    session = session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def dispose_database_engine(engine: AsyncEngine) -> None:
    """Libera las conexiones administradas por el motor."""
    await engine.dispose()
