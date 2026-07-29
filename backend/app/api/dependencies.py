"""Dependencias compartidas de sesión y autenticación administrativa."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import (
    DatabaseSettings,
    JwtSettings,
    get_database_settings,
    get_jwt_settings,
)
from app.core.tokens import AccessTokenClaims, decode_access_token
from app.db.session import (
    SessionFactory,
    create_database_engine,
    create_session_factory,
    session_scope,
)
from app.models import Administrador, TokenRevocado


bearer = HTTPBearer(auto_error=False)


@lru_cache
def _factory(database_url: str) -> SessionFactory:
    """Reutiliza el pool del proceso en lugar de crearlo por solicitud."""
    return create_session_factory(create_database_engine(database_url))


async def get_session(
    settings: Annotated[DatabaseSettings, Depends(get_database_settings)],
) -> AsyncIterator[AsyncSession]:
    """Entrega una unidad de trabajo que confirma o revierte la solicitud."""
    async with session_scope(_factory(str(settings.database_url))) as session:
        yield session


@dataclass(frozen=True)
class AuthContext:
    """Identidad y claims verificadas de la solicitud."""

    administrador: Administrador
    claims: AccessTokenClaims


async def get_auth_context(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer),
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[JwtSettings, Depends(get_jwt_settings)],
) -> AuthContext:
    """Rechaza de forma uniforme cualquier sesión no autorizada."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autorizado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    claims = decode_access_token(credentials.credentials, settings.jwt_secret)
    if claims is None:
        raise unauthorized
    try:
        administrator_id = int(claims["sub"])
    except ValueError as error:
        raise unauthorized from error

    revoked = await session.execute(
        select(TokenRevocado.id).where(
            TokenRevocado.jti == claims["jti"],
        )
    )
    if revoked.scalar_one_or_none() is not None:
        raise unauthorized
    administrator = await session.get(Administrador, administrator_id)
    if administrator is None or not administrator.activo:
        raise unauthorized
    return AuthContext(administrador=administrator, claims=claims)


SessionDependency = Annotated[AsyncSession, Depends(get_session)]
AuthDependency = Annotated[AuthContext, Depends(get_auth_context)]
JwtDependency = Annotated[JwtSettings, Depends(get_jwt_settings)]
