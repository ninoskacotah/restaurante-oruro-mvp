"""Modelo persistente del repartidor registrado en el sistema."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, false, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Repartidor(Base):
    """Perfil mínimo del repartidor y su habilitación operativa."""

    __tablename__ = "repartidores"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    nombre: Mapped[str | None] = mapped_column(String, nullable=True)
    telefono: Mapped[str | None] = mapped_column(String, nullable=True)
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
