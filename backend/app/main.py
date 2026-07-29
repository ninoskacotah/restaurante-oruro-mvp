"""Punto de entrada ASGI del backend."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.catalogo import router as catalog_router
from app.api.routes.pedidos import router as orders_router
from app.api.routes.panel import router as panel_router
from app.services.errors import (
    ConflictoServicio,
    ErrorValidacion,
    RecursoNoEncontrado,
)


def create_app() -> FastAPI:
    """Construye la aplicación y registra sus routers."""
    application = FastAPI(
        title="Restaurant Las Retamas API",
        version="0.1.0",
    )
    application.include_router(health_router, prefix="/api")
    application.include_router(auth_router, prefix="/api")
    application.include_router(catalog_router, prefix="/api")
    application.include_router(orders_router, prefix="/api")
    application.include_router(panel_router, prefix="/api")

    @application.exception_handler(ErrorValidacion)
    async def validation_error(
        _request: Request,
        error: ErrorValidacion,
    ) -> JSONResponse:
        """Traduce reglas inválidas sin exponer una traza interna."""
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @application.exception_handler(RecursoNoEncontrado)
    async def not_found_error(
        _request: Request,
        error: RecursoNoEncontrado,
    ) -> JSONResponse:
        """Traduce una ausencia controlada a HTTP 404."""
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @application.exception_handler(ConflictoServicio)
    async def conflict_error(
        _request: Request,
        error: ConflictoServicio,
    ) -> JSONResponse:
        """Traduce conflictos de estado a HTTP 409."""
        return JSONResponse(status_code=409, content={"detail": str(error)})

    return application


app = create_app()
