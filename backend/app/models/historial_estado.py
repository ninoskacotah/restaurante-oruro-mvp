"""Modelo persistente del historial acumulativo de estados."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HistorialEstado(Base):
    """Evento de estado con origen y, como máximo, un actor identificado."""

    __tablename__ = "historial_estados"
    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(cliente_id, repartidor_id, administrador_id) <= 1",
            name="ck_historial_estados_un_actor",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id"),
        nullable=False,
    )
    cliente_id: Mapped[int | None] = mapped_column(
        ForeignKey("clientes.id"),
        nullable=True,
    )
    repartidor_id: Mapped[int | None] = mapped_column(
        ForeignKey("repartidores.id"),
        nullable=True,
    )
    administrador_id: Mapped[int | None] = mapped_column(
        ForeignKey("administradores.id"),
        nullable=True,
    )
    # El primer evento puede no tener un estado anterior.
    estado_anterior: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    estado_nuevo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    evento: Mapped[str] = mapped_column(String(50), nullable=False)
    origen: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
