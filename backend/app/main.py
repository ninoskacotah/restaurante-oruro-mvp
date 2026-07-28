"""Punto de entrada ASGI del backend."""

from fastapi import FastAPI

from app.api.health import router as health_router


def create_app() -> FastAPI:
    """Construye la aplicación y registra sus routers."""
    application = FastAPI(
        title="Restaurant Las Retamas API",
        version="0.1.0",
    )
    application.include_router(health_router, prefix="/api")
    return application


app = create_app()
