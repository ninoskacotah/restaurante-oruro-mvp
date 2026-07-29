"""Emisión y validación aisladas de tokens administrativos."""

from datetime import datetime, timedelta, timezone
from typing import TypedDict, cast
from uuid import uuid4

import jwt
from jwt import InvalidTokenError
from pydantic import SecretStr


JWT_ALGORITHM = "HS256"
JWT_ISSUER = "restaurant-las-retamas-api"
JWT_AUDIENCE = "restaurant-las-retamas-panel"
JWT_ROLE = "admin"
JWT_LIFETIME = timedelta(minutes=15)
JWT_LEEWAY = timedelta(seconds=30)
JWT_REQUIRED_CLAIMS = (
    "sub",
    "role",
    "iss",
    "aud",
    "iat",
    "nbf",
    "exp",
    "jti",
)


class AccessTokenClaims(TypedDict):
    """Claims verificadas que identifican una sesión administrativa."""

    sub: str
    role: str
    iss: str
    aud: str
    iat: int
    nbf: int
    exp: int
    jti: str


def create_access_token(
    administrator_id: int,
    secret: SecretStr,
    *,
    issued_at: datetime | None = None,
) -> str:
    """Emite un token HS256 de corta duración para un administrador."""
    now = issued_at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("issued_at debe incluir zona horaria")

    payload = {
        "sub": str(administrator_id),
        "role": JWT_ROLE,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + JWT_LIFETIME,
        "jti": str(uuid4()),
    }
    return jwt.encode(
        payload,
        secret.get_secret_value(),
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
    secret: SecretStr,
) -> AccessTokenClaims | None:
    """Valida firma y claims o devuelve un único resultado de rechazo."""
    try:
        claims = jwt.decode(
            token,
            secret.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            leeway=JWT_LEEWAY,
            options={"require": list(JWT_REQUIRED_CLAIMS)},
        )
    except InvalidTokenError:
        return None

    if claims.get("role") != JWT_ROLE:
        return None
    if not _is_non_empty_string(claims.get("sub")):
        return None
    if not _is_non_empty_string(claims.get("jti")):
        return None

    return cast(AccessTokenClaims, claims)


def _is_non_empty_string(value: object) -> bool:
    """Comprueba identificadores obligatorios sin convertir tipos."""
    return isinstance(value, str) and bool(value.strip())
