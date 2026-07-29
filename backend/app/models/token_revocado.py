"""Modelo persistente de identificadores JWT revocados."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TokenRevocado(Base):
    """Conserva un jti invalidado hasta el vencimiento de su token."""

    __tablename__ = "tokens_revocados"

    id: Mapped[int] = mapped_column(primary_key=True)
    administrador_id: Mapped[int] = mapped_column(
        ForeignKey("administradores.id"),
        nullable=False,
    )
    # El JWT completo nunca se persiste; solo su identificador único.
    jti: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    fecha_revocacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    fecha_expiracion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
