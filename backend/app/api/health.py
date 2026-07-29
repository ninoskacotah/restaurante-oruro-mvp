"""Endpoint técnico para comprobar la disponibilidad de la API."""

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Confirma que la aplicación puede atender solicitudes."""
    return {"status": "ok"}
