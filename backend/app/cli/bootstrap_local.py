"""Prepara PostgreSQL y el entorno local mediante entradas no versionadas."""

from getpass import getpass
from pathlib import Path
from secrets import token_urlsafe
from urllib.parse import quote_plus

import psycopg
from alembic.config import main as alembic_main
from psycopg import sql


def _confirmed_secret(prompt: str) -> str:
    """Solicita dos veces un secreto para evitar errores de escritura."""
    value = getpass(prompt)
    confirmation = getpass("Repite el valor: ")
    if value != confirmation:
        raise ValueError("Los valores no coinciden.")
    if not value:
        raise ValueError("El valor no puede estar vacío.")
    return value


def prepare_database(
    *,
    postgres_password: str,
    application_user: str,
    application_password: str,
    database_name: str,
) -> None:
    """Crea o actualiza rol y base usando composición SQL segura."""
    with psycopg.connect(
        host="localhost",
        port=5432,
        dbname="postgres",
        user="postgres",
        password=postgres_password,
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %s",
                (application_user,),
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                        sql.Identifier(application_user),
                        sql.Literal(application_password),
                    )
                )
            else:
                cursor.execute(
                    sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD {}").format(
                        sql.Identifier(application_user),
                        sql.Literal(application_password),
                    )
                )
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (database_name,),
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(database_name),
                        sql.Identifier(application_user),
                    )
                )


def write_environment(
    *,
    destination: Path,
    application_user: str,
    application_password: str,
    database_name: str,
    telegram_token: str,
) -> None:
    """Escribe el archivo local ignorado sin imprimir sus secretos."""
    encoded_user = quote_plus(application_user)
    encoded_password = quote_plus(application_password)
    lines = [
        "APP_ENV=development",
        (
            "DATABASE_URL=postgresql+psycopg://"
            f"{encoded_user}:{encoded_password}@localhost:5432/{database_name}"
        ),
        f"TELEGRAM_BOT_TOKEN={telegram_token}",
        f"JWT_SECRET={token_urlsafe(48)}",
        "MEDIA_ROOT=var/media",
        "PAYMENT_QR_PATH=var/payment-qr.png",
    ]
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Coordina base, `.env` y migraciones desde la carpeta backend."""
    destination = Path(".env")
    if destination.exists():
        confirmation = input(
            "Ya existe backend/.env. ¿Deseas reemplazarlo? [s/N]: "
        )
        if confirmation.strip().lower() != "s":
            raise SystemExit("Preparación cancelada sin modificar el entorno.")
    try:
        postgres_password = getpass("Contraseña local del usuario postgres: ")
        application_password = _confirmed_secret(
            "Nueva contraseña para restaurant_user: "
        )
        telegram_token = getpass(
            "Token de BotFather (Enter si todavía no existe): "
        ).strip() or "replace-after-botfather"
        prepare_database(
            postgres_password=postgres_password,
            application_user="restaurant_user",
            application_password=application_password,
            database_name="restaurant_las_retamas",
        )
        write_environment(
            destination=destination,
            application_user="restaurant_user",
            application_password=application_password,
            database_name="restaurant_las_retamas",
            telegram_token=telegram_token,
        )
        alembic_main(argv=["upgrade", "head"])
    except (ValueError, psycopg.Error) as error:
        raise SystemExit(f"No fue posible preparar el entorno: {error}") from error
    print("Base, variables y migraciones locales preparadas correctamente.")
    print("Siguiente paso: python -m app.cli.create_admin")


if __name__ == "__main__":
    main()
