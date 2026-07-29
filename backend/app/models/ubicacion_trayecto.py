"""Modelo persistente de un punto enviado durante el trayecto."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UbicacionTrayecto(Base):
    """Coordenada ordenable vinculada con una asignación concreta."""

    __tablename__ = "ubicaciones_trayecto"

    id: Mapped[int] = mapped_column(primary_key=True)
    # La asignación evita mezclar recorridos después de una reasignación.
    asignacion_id: Mapped[int] = mapped_column(
        ForeignKey("asignaciones.id"),
        nullable=False,
    )
    latitud: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )
    longitud: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
