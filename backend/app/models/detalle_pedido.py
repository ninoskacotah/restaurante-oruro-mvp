"""Modelo persistente de los platos incluidos en un pedido."""

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DetallePedido(Base):
    """Copia histórica de un plato y su importe dentro del pedido."""

    __tablename__ = "detalles_pedido"
    __table_args__ = (
        CheckConstraint(
            "precio_unitario >= 0",
            name="ck_detalles_pedido_precio_unitario",
        ),
        CheckConstraint(
            "cantidad > 0",
            name="ck_detalles_pedido_cantidad",
        ),
        CheckConstraint(
            "subtotal >= 0",
            name="ck_detalles_pedido_subtotal",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id"),
        nullable=False,
    )
    plato_id: Mapped[int] = mapped_column(
        ForeignKey("platos.id"),
        nullable=False,
    )
    # El nombre y el precio se copian para preservar el pedido confirmado.
    nombre_plato: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
