"""Modelo persistente de la asignación de un pedido."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Asignacion(Base):
    """Vínculo histórico entre un pedido y un repartidor."""

    __tablename__ = "asignaciones"
    __table_args__ = (
        # PostgreSQL aplica la unicidad solo a las filas aún activas.
        Index(
            "uq_asignaciones_pedido_activa",
            "pedido_id",
            unique=True,
            postgresql_where=text("activa"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id"),
        nullable=False,
    )
    repartidor_id: Mapped[int] = mapped_column(
        ForeignKey("repartidores.id"),
        nullable=False,
    )
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False)
    fecha_asignacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    # Estas fechas se completarán mediante eventos de Issues posteriores.
    fecha_acuse: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    fecha_cierre: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
