"""Crea o actualiza el administrador inicial sin recibir secretos por argumentos."""

import argparse
import asyncio
import sys
from getpass import getpass

from sqlalchemy import select

from app.core.config import get_database_settings
from app.core.security import hash_password
from app.db.session import (
    create_database_engine,
    create_session_factory,
    dispose_database_engine,
    session_scope,
)
from app.models import Administrador


def _password_confirmation() -> str:
    """Solicita dos veces una contraseña sin mostrarla."""
    password = getpass("Contraseña del administrador: ")
    confirmation = getpass("Repite la contraseña: ")
    if password != confirmation:
        raise ValueError("Las contraseñas no coinciden.")
    if len(password) < 10:
        raise ValueError("La contraseña debe contener al menos 10 caracteres.")
    return password


async def upsert_administrator(username: str, password: str) -> str:
    """Crea la cuenta o renueva su credencial de manera idempotente."""
    settings = get_database_settings()
    engine = create_database_engine(str(settings.database_url))
    factory = create_session_factory(engine)
    try:
        async with session_scope(factory) as session:
            result = await session.execute(
                select(Administrador).where(
                    Administrador.nombre_usuario == username
                )
            )
            administrator = result.scalar_one_or_none()
            action = "actualizado"
            if administrator is None:
                administrator = Administrador(nombre_usuario=username)
                session.add(administrator)
                action = "creado"
            administrator.credencial_hash = hash_password(password)
            administrator.activo = True
            await session.flush()
        return action
    finally:
        await dispose_database_engine(engine)


def run_upsert_administrator(username: str, password: str) -> str:
    """Ejecuta el acceso asíncrono con un bucle compatible con Psycopg."""
    if sys.platform == "win32":
        with asyncio.Runner(
            loop_factory=asyncio.SelectorEventLoop,
        ) as runner:
            return runner.run(upsert_administrator(username, password))
    return asyncio.run(upsert_administrator(username, password))


def main() -> None:
    """Interpreta solo el usuario; la contraseña nunca viaja en la línea."""
    parser = argparse.ArgumentParser(
        description="Crear o actualizar un administrador local.",
    )
    parser.add_argument(
        "--username",
        default="admin_prueba",
        help="Nombre de usuario; por defecto admin_prueba.",
    )
    arguments = parser.parse_args()
    username = arguments.username.strip()
    if not username:
        raise SystemExit("El nombre de usuario no puede estar vacío.")
    try:
        password = _password_confirmation()
        action = run_upsert_administrator(username, password)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    print(f"Administrador '{username}' {action} y habilitado.")


if __name__ == "__main__":
    main()
