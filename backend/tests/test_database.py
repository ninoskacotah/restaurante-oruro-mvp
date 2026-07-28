"""Pruebas de la capa asíncrona de acceso a PostgreSQL."""

import asyncio
import unittest
from unittest.mock import AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import (
    create_database_engine,
    create_session_factory,
    dispose_database_engine,
    session_scope,
)


class DatabaseSessionTest(unittest.TestCase):
    """Comprueba el motor y el ciclo de las sesiones sin PostgreSQL."""

    def test_engine_uses_postgresql_psycopg_without_connecting(self) -> None:
        """Construye el motor y verifica el dialecto sin abrir conexiones."""
        engine = create_database_engine(
            "postgresql+psycopg://test_user:test_password@localhost/test_db"
        )

        self.assertEqual(engine.dialect.name, "postgresql")
        self.assertEqual(engine.dialect.driver, "psycopg")

        asyncio.run(dispose_database_engine(engine))

    def test_session_factory_disables_expiration_after_commit(self) -> None:
        """Conserva disponibles los atributos después de confirmar."""
        engine = create_database_engine(
            "postgresql+psycopg://test_user:test_password@localhost/test_db"
        )
        session_factory = create_session_factory(engine)
        session = session_factory()

        self.assertIsInstance(session, AsyncSession)
        self.assertFalse(session.sync_session.expire_on_commit)

        asyncio.run(session.close())
        asyncio.run(dispose_database_engine(engine))

    def test_successful_scope_commits_and_closes(self) -> None:
        """Confirma y cierra una unidad de trabajo correcta."""
        session = AsyncMock(spec=AsyncSession)
        session_factory = Mock(return_value=session)

        async def exercise_scope() -> None:
            async with session_scope(session_factory) as active_session:
                self.assertIs(active_session, session)

        asyncio.run(exercise_scope())

        session.commit.assert_awaited_once_with()
        session.rollback.assert_not_awaited()
        session.close.assert_awaited_once_with()

    def test_failed_scope_rolls_back_closes_and_preserves_error(self) -> None:
        """Revierte, cierra y propaga el error original."""
        session = AsyncMock(spec=AsyncSession)
        session_factory = Mock(return_value=session)

        async def exercise_scope() -> None:
            async with session_scope(session_factory):
                raise RuntimeError("fallo de prueba")

        with self.assertRaisesRegex(RuntimeError, "fallo de prueba"):
            asyncio.run(exercise_scope())

        session.commit.assert_not_awaited()
        session.rollback.assert_awaited_once_with()
        session.close.assert_awaited_once_with()


if __name__ == "__main__":
    unittest.main()
