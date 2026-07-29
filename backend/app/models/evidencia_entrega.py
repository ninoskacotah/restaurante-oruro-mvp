"""Modelo persistente de la evidencia que confirma una entrega."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EvidenciaEntrega(Base):
    """Referencia a una fotografía o código asociado con la asignación."""

    __tablename__ = "evidencias_entrega"
    __table_args__ = (
        CheckConstraint(
            "tamanio_bytes IS NULL OR tamanio_bytes >= 0",
            name="ck_evidencias_entrega_tamanio_bytes",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asignacion_id: Mapped[int] = mapped_column(
        ForeignKey("asignaciones.id"),
        nullable=False,
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    valor_referencia: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    # MIME y tamaño solo corresponden cuando la evidencia es un archivo.
    tipo_mime: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    tamanio_bytes: Mapped[int | None] = mapped_column(nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
