"""Relación persistente entre menús y platos."""
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    UniqueConstraint,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class DetalleMenu(Base):
    """Oferta de un plato con stock para un menú concreto."""
    __tablename__ = "detalles_menu"
    __table_args__ = (
        UniqueConstraint("menu_id", "plato_id"),
        CheckConstraint("stock >= 0", name="ck_detalles_menu_stock"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    menu_id: Mapped[int] = mapped_column(
        ForeignKey("menus.id"),
        nullable=False,
    )
    plato_id: Mapped[int] = mapped_column(
        ForeignKey("platos.id"),
        nullable=False,
    )
    stock: Mapped[int] = mapped_column(nullable=False)
    disponible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )
