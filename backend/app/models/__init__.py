"""Modelos de persistencia registrados en los metadatos compartidos."""

from app.models.administrador import Administrador
from app.models.cliente import Cliente
from app.models.menu import Menu
from app.models.plato import Plato
from app.models.repartidor import Repartidor
from app.models.token_revocado import TokenRevocado


__all__ = [
    "Administrador",
    "Cliente",
    "Menu",
    "Plato",
    "Repartidor",
    "TokenRevocado",
]
