"""Modelo persistente de la identidad administrativa."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, false, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Administrador(Base):
    """Identidad protegida que posteriormente accederá al panel."""

    __tablename__ = "administradores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_usuario: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    # Este campo recibirá solamente el resultado del algoritmo de hashing.
    credencial_hash: Mapped[str] = mapped_column(String, nullable=False)
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
