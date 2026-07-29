"""Modelo persistente de los comprobantes enviados para un pedido."""

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ComprobantePago(Base):
    """Referencia y metadatos de un comprobante sujeto a revisión."""

    __tablename__ = "comprobantes_pago"
    __table_args__ = (
        CheckConstraint(
            "tamanio_bytes >= 0",
            name="ck_comprobantes_pago_tamanio_bytes",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id"),
        nullable=False,
    )
    # Solo se asigna un administrador cuando comienza la revisión.
    administrador_id: Mapped[int | None] = mapped_column(
        ForeignKey("administradores.id"),
        nullable=True,
    )
    # PostgreSQL conserva referencias y metadatos, no el archivo binario.
    archivo_referencia: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    nombre_generado: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    tipo_mime: Mapped[str] = mapped_column(String(100), nullable=False)
    tamanio_bytes: Mapped[int] = mapped_column(nullable=False)
    estado_revision: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'PENDIENTE'"),
    )
    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_envio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    fecha_revision: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
