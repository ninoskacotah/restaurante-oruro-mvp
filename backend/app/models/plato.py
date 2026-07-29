"""Modelo persistente del catálogo de platos."""

from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Numeric, String, false
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Plato(Base):
    """Producto administrable que podrá incorporarse a los menús."""

    __tablename__ = "platos"
    __table_args__ = (
        CheckConstraint("precio >= 0", name="ck_platos_precio"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String, nullable=True)
    precio: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False,
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )
