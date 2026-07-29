"""Modelo persistente de la cabecera de un pedido."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Pedido(Base):
    """Pedido asociado a un cliente antes de incorporar sus detalles."""

    __tablename__ = "pedidos"
    __table_args__ = (
        CheckConstraint("total >= 0", name="ck_pedidos_total"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id"),
        nullable=False,
    )
    # El menú de origen permite reponer exactamente el stock descontado.
    menu_id: Mapped[int | None] = mapped_column(
        ForeignKey("menus.id"),
        nullable=True,
    )
    # El código se asignará al confirmar; por eso puede faltar en el borrador.
    codigo_seguimiento: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        unique=True,
    )
    estado_actual: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'BORRADOR'"),
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        server_default=text("0"),
    )
    # Estas coordenadas representan el destino fijo, no el recorrido.
    entrega_latitud: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6),
        nullable=True,
    )
    entrega_longitud: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 6),
        nullable=True,
    )
    referencia_entrega: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
