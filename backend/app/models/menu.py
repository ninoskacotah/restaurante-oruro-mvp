"""Modelo persistente del menú programado por fecha."""

from datetime import date

from sqlalchemy import Boolean, Date, false
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Menu(Base):
    """Oferta diaria que posteriormente agrupará platos y stock."""

    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false(),
    )
