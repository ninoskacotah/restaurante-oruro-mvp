"""Futuros servicios y reglas de aplicación del backend."""
"""Servicios de aplicación independientes de los transportes externos."""

from app.services.catalogo import (
    actualizar_plato,
    crear_plato,
    desactivar_plato,
    obtener_plato,
)
from app.services.ciclo_pedido import (
    cancelar_pedido,
    registrar_comprobante_pago,
    registrar_ubicacion_entrega,
    revisar_comprobante_pago,
)
from app.services.errors import (
    ConflictoServicio,
    ErrorServicio,
    ErrorValidacion,
    RecursoNoEncontrado,
)
from app.services.menus import (
    actualizar_estado_menu,
    actualizar_oferta,
    agregar_plato_al_menu,
    consultar_oferta_disponible,
    obtener_menu,
    obtener_o_crear_menu,
    retirar_plato_del_menu,
)
from app.services.pedidos import (
    agregar_plato_al_carrito,
    confirmar_pedido,
    modificar_cantidad_carrito,
    obtener_o_crear_borrador,
    obtener_pedido,
    retirar_detalle_carrito,
)
from app.services.reparto import (
    acusar_recepcion,
    asignar_repartidor,
    confirmar_entrega,
    iniciar_trayecto,
    registrar_llegada,
    registrar_ubicacion_trayecto,
)
from app.services.reportes import (
    average_delivery_minutes,
    daily_sales,
    popular_dishes,
)


__all__ = [
    "ConflictoServicio",
    "ErrorServicio",
    "ErrorValidacion",
    "RecursoNoEncontrado",
    "actualizar_oferta",
    "actualizar_estado_menu",
    "actualizar_plato",
    "agregar_plato_al_menu",
    "cancelar_pedido",
    "agregar_plato_al_carrito",
    "acusar_recepcion",
    "asignar_repartidor",
    "consultar_oferta_disponible",
    "crear_plato",
    "confirmar_pedido",
    "confirmar_entrega",
    "desactivar_plato",
    "obtener_menu",
    "obtener_o_crear_menu",
    "obtener_o_crear_borrador",
    "obtener_pedido",
    "iniciar_trayecto",
    "obtener_plato",
    "retirar_plato_del_menu",
    "retirar_detalle_carrito",
    "registrar_comprobante_pago",
    "registrar_ubicacion_entrega",
    "registrar_ubicacion_trayecto",
    "registrar_llegada",
    "revisar_comprobante_pago",
    "modificar_cantidad_carrito",
    "average_delivery_minutes",
    "daily_sales",
    "popular_dishes",
]
