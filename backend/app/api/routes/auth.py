"""Endpoints de sesión administrativa."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import (
    AuthDependency,
    JwtDependency,
    SessionDependency,
)
from app.core.security import verify_password
from app.core.tokens import create_access_token
from app.models import Administrador, TokenRevocado
from app.schemas import (
    AdministradorOutput,
    LoginInput,
    TokenOutput,
)


router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/login", response_model=TokenOutput)
async def login(
    data: LoginInput,
    session: SessionDependency,
    settings: JwtDependency,
) -> TokenOutput:
    """Valida credenciales con una respuesta uniforme de rechazo."""
    result = await session.execute(
        select(Administrador).where(
            Administrador.nombre_usuario == data.nombre_usuario.strip()
        )
    )
    administrador = result.scalar_one_or_none()
    if (
        administrador is None
        or not administrador.activo
        or not verify_password(data.contrasena, administrador.credencial_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
        )
    token = create_access_token(
        administrador.id,
        settings.jwt_secret,
    )
    return TokenOutput(access_token=token)


@router.get("/me", response_model=AdministradorOutput)
async def current_session(auth: AuthDependency) -> Administrador:
    """Devuelve únicamente la identidad pública autenticada."""
    return auth.administrador


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    auth: AuthDependency,
    session: SessionDependency,
) -> None:
    """Revoca el jti hasta su vencimiento sin conservar el JWT."""
    session.add(
        TokenRevocado(
            administrador_id=auth.administrador.id,
            jti=auth.claims["jti"],
            fecha_expiracion=datetime.fromtimestamp(
                auth.claims["exp"],
                tz=timezone.utc,
            ),
        )
    )
    await session.flush()
