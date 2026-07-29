"""Operaciones aisladas para proteger contraseñas administrativas."""

from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError


# Los valores corresponden a la decisión DT-015 y se medirán luego en el VPS.
PASSWORD_HASHER = PasswordHasher(
    memory_cost=19456,
    time_cost=2,
    parallelism=1,
    type=Type.ID,
)


def hash_password(password: str) -> str:
    """Genera una cadena PHC Argon2id con una sal aleatoria."""
    return PASSWORD_HASHER.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Comprueba una contraseña sin exponer el motivo de un fallo."""
    try:
        return PASSWORD_HASHER.verify(password_hash, password)
    except (InvalidHashError, VerificationError):
        return False


def password_hash_needs_update(password_hash: str) -> bool:
    """Indica si un hash válido debe regenerarse con parámetros vigentes."""
    try:
        return PASSWORD_HASHER.check_needs_rehash(password_hash)
    except InvalidHashError:
        # Un valor ilegible nunca debe considerarse una credencial vigente.
        return True
