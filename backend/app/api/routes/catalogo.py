"""Endpoints administrativos del catálogo y los menús."""

from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.dependencies import AuthDependency, SessionDependency
from app.models import DetalleMenu, Menu, Plato
from app.schemas import (
    DetalleMenuInput,
    DetalleMenuOutput,
    MenuCreate,
    MenuOutput,
    MenuState,
    OfertaInput,
    PlatoInput,
    PlatoOutput,
)
from app.services import (
    actualizar_estado_menu,
    actualizar_oferta,
    actualizar_plato,
    agregar_plato_al_menu,
    crear_plato,
    desactivar_plato,
    obtener_o_crear_menu,
)


router = APIRouter(tags=["catálogo"])


@router.get("/platos", response_model=list[PlatoOutput])
async def list_platos(
    session: SessionDependency,
    _auth: AuthDependency,
) -> list[Plato]:
    """Lista el catálogo completo para su administración."""
    result = await session.execute(select(Plato).order_by(Plato.nombre))
    return list(result.scalars().all())


@router.post(
    "/platos",
    response_model=PlatoOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_plato(
    data: PlatoInput,
    session: SessionDependency,
    _auth: AuthDependency,
) -> Plato:
    """Crea un plato y aplica el estado solicitado."""
    plato = await crear_plato(
        session,
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio=data.precio,
    )
    plato.activo = data.activo
    await session.flush()
    return plato


@router.put("/platos/{plato_id}", response_model=PlatoOutput)
async def update_plato(
    plato_id: int,
    data: PlatoInput,
    session: SessionDependency,
    _auth: AuthDependency,
) -> Plato:
    """Reemplaza los datos administrables de un plato."""
    return await actualizar_plato(
        session,
        plato_id,
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio=data.precio,
        activo=data.activo,
    )


@router.delete(
    "/platos/{plato_id}",
    response_model=PlatoOutput,
)
async def disable_plato(
    plato_id: int,
    session: SessionDependency,
    _auth: AuthDependency,
) -> Plato:
    """Realiza la baja lógica del plato."""
    return await desactivar_plato(session, plato_id)


@router.get("/menus", response_model=list[MenuOutput])
async def list_menus(
    session: SessionDependency,
    _auth: AuthDependency,
) -> list[Menu]:
    """Lista ofertas programadas de la más reciente a la más antigua."""
    result = await session.execute(select(Menu).order_by(Menu.fecha.desc()))
    return list(result.scalars().all())


@router.post(
    "/menus",
    response_model=MenuOutput,
    status_code=status.HTTP_201_CREATED,
)
async def create_menu(
    data: MenuCreate,
    session: SessionDependency,
    _auth: AuthDependency,
) -> Menu:
    """Crea o recupera la oferta correspondiente a una fecha."""
    return await obtener_o_crear_menu(session, data.fecha)


@router.get(
    "/menus/{menu_id}/detalles",
    response_model=list[DetalleMenuOutput],
)
async def list_menu_details(
    menu_id: int,
    session: SessionDependency,
    _auth: AuthDependency,
) -> list[DetalleMenu]:
    """Lista stock y disponibilidad del menú seleccionado."""
    result = await session.execute(
        select(DetalleMenu)
        .where(DetalleMenu.menu_id == menu_id)
        .order_by(DetalleMenu.id)
    )
    return list(result.scalars().all())


@router.patch("/menus/{menu_id}", response_model=MenuOutput)
async def change_menu_state(
    menu_id: int,
    data: MenuState,
    session: SessionDependency,
    _auth: AuthDependency,
) -> Menu:
    """Activa o desactiva una oferta diaria."""
    return await actualizar_estado_menu(
        session,
        menu_id,
        activo=data.activo,
    )


@router.post(
    "/menus/{menu_id}/detalles",
    response_model=DetalleMenuOutput,
    status_code=status.HTTP_201_CREATED,
)
async def add_menu_detail(
    menu_id: int,
    data: DetalleMenuInput,
    session: SessionDependency,
    _auth: AuthDependency,
) -> DetalleMenu:
    """Incorpora un plato con stock a la oferta."""
    return await agregar_plato_al_menu(
        session,
        menu_id=menu_id,
        plato_id=data.plato_id,
        stock=data.stock,
        disponible=data.disponible,
    )


@router.patch(
    "/menus/detalles/{detalle_id}",
    response_model=DetalleMenuOutput,
)
async def update_menu_detail(
    detalle_id: int,
    data: OfertaInput,
    session: SessionDependency,
    _auth: AuthDependency,
) -> DetalleMenu:
    """Actualiza stock y disponibilidad de una oferta."""
    return await actualizar_oferta(
        session,
        detalle_id,
        stock=data.stock,
        disponible=data.disponible,
    )
