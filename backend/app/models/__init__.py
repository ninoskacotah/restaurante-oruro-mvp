"""Modelos de persistencia registrados en los metadatos compartidos."""

from app.models.administrador import Administrador
from app.models.cliente import Cliente
from app.models.detalle_menu import DetalleMenu
from app.models.detalle_pedido import DetallePedido
from app.models.menu import Menu
from app.models.pedido import Pedido
from app.models.plato import Plato
from app.models.repartidor import Repartidor
from app.models.token_revocado import TokenRevocado


__all__ = [
    "Administrador",
    "Cliente",
    "DetalleMenu",
    "DetallePedido",
    "Menu",
    "Pedido",
    "Plato",
    "Repartidor",
    "TokenRevocado",
]
