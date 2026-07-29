"""Modelos de persistencia registrados en los metadatos compartidos."""

from app.models.administrador import Administrador
from app.models.asignacion import Asignacion
from app.models.cliente import Cliente
from app.models.comprobante_pago import ComprobantePago
from app.models.detalle_menu import DetalleMenu
from app.models.detalle_pedido import DetallePedido
from app.models.evidencia_entrega import EvidenciaEntrega
from app.models.historial_estado import HistorialEstado
from app.models.menu import Menu
from app.models.pedido import Pedido
from app.models.plato import Plato
from app.models.repartidor import Repartidor
from app.models.token_revocado import TokenRevocado
from app.models.ubicacion_trayecto import UbicacionTrayecto


__all__ = [
    "Administrador",
    "Asignacion",
    "Cliente",
    "ComprobantePago",
    "DetalleMenu",
    "DetallePedido",
    "EvidenciaEntrega",
    "HistorialEstado",
    "Menu",
    "Pedido",
    "Plato",
    "Repartidor",
    "TokenRevocado",
    "UbicacionTrayecto",
]
