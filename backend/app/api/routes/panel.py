"""Consultas administrativas de clientes, archivos y reportes."""

from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select

from app.api.dependencies import AuthDependency, SessionDependency
from app.core.config import Settings, get_settings
from app.models import Cliente, ComprobantePago, Pedido
from app.schemas import (
    ClienteDetailOutput,
    ClienteOutput,
    PlatoPopularOutput,
    ReportesOutput,
)
from app.services import (
    average_delivery_minutes,
    daily_sales,
    popular_dishes,
)


router = APIRouter(tags=["panel"])


@router.get("/clientes", response_model=list[ClienteOutput])
async def list_clients(
    session: SessionDependency,
    _auth: AuthDependency,
) -> list[Cliente]:
    """Lista clientes registrados sin incorporar datos no persistidos."""
    result = await session.execute(
        select(Cliente).order_by(Cliente.fecha_registro.desc())
    )
    return list(result.scalars().all())


@router.get(
    "/clientes/{cliente_id}",
    response_model=ClienteDetailOutput,
)
async def client_detail(
    cliente_id: int,
    session: SessionDependency,
    _auth: AuthDependency,
) -> ClienteDetailOutput:
    """Devuelve perfil, historial y frecuencia calculada."""
    client = await session.get(Cliente, cliente_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El cliente solicitado no existe.",
        )
    result = await session.execute(
        select(Pedido)
        .where(Pedido.cliente_id == cliente_id)
        .order_by(Pedido.fecha_creacion.desc())
    )
    orders = list(result.scalars().all())
    frequency_result = await session.execute(
        select(func.count(Pedido.id)).where(
            Pedido.cliente_id == cliente_id,
            Pedido.estado_actual.not_in({"BORRADOR", "CANCELADO"}),
        )
    )
    return ClienteDetailOutput(
        cliente=ClienteOutput.model_validate(client),
        pedidos=orders,
        frecuencia_pedidos=int(frequency_result.scalar_one()),
    )


def _safe_media_file(media_root: Path, reference: str) -> Path:
    """Impide leer archivos fuera del directorio privado configurado."""
    root = media_root.resolve()
    target = (root / Path(reference)).resolve()
    if root not in target.parents or not target.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El comprobante no está disponible.",
        )
    return target


@router.get("/comprobantes/{comprobante_id}/archivo")
async def receipt_file(
    comprobante_id: int,
    session: SessionDependency,
    _auth: AuthDependency,
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """Entrega una fotografía únicamente tras autenticar al administrador."""
    receipt = await session.get(ComprobantePago, comprobante_id)
    if receipt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El comprobante solicitado no existe.",
        )
    path = _safe_media_file(settings.media_root, receipt.archivo_referencia)
    return FileResponse(
        path,
        media_type=receipt.tipo_mime,
        filename=receipt.nombre_generado,
    )


@router.get("/reportes", response_model=ReportesOutput)
async def reports(
    session: SessionDependency,
    _auth: AuthDependency,
    fecha: date = Query(default_factory=date.today),
) -> ReportesOutput:
    """Calcula los tres reportes requeridos para una fecha."""
    sales, order_count = await daily_sales(session, fecha)
    dishes = await popular_dishes(session, fecha)
    average = await average_delivery_minutes(session, fecha)
    return ReportesOutput(
        fecha=fecha,
        ventas_dia=sales,
        pedidos_contabilizados=order_count,
        platos_mas_pedidos=[
            PlatoPopularOutput(
                plato_id=plato_id,
                nombre=name,
                cantidad=quantity,
            )
            for plato_id, name, quantity in dishes
        ],
        tiempo_promedio_entrega_minutos=average,
    )
