"""Pruebas de la base declarativa compartida."""

import unittest

from sqlalchemy.orm import DeclarativeBase

from app.db.base import Base, NAMING_CONVENTION, metadata
from app.models import Administrador, Cliente, Repartidor, TokenRevocado


class DatabaseBaseTest(unittest.TestCase):
    """Comprueba la base y los metadatos compartidos."""

    def test_naming_convention_contains_expected_patterns(self) -> None:
        """Verifica exactamente las cinco convenciones aprobadas."""
        self.assertEqual(
            NAMING_CONVENTION,
            {
                "ix": "ix_%(table_name)s_%(column_0_name)s",
                "uq": "uq_%(table_name)s_%(column_0_name)s",
                "ck": "ck_%(table_name)s_%(column_0_name)s",
                "fk": (
                    "fk_%(table_name)s_%(column_0_name)s_"
                    "%(referred_table_name)s"
                ),
                "pk": "pk_%(table_name)s",
            },
        )

    def test_base_uses_shared_metadata(self) -> None:
        """Confirma que todos los modelos compartirán los metadatos."""
        self.assertTrue(issubclass(Base, DeclarativeBase))
        self.assertIs(Base.metadata, metadata)

    def test_metadata_contains_only_authorized_tables(self) -> None:
        """Evita anticipar entidades fuera del alcance del Issue."""
        self.assertEqual(
            set(metadata.tables),
            {
                "administradores",
                "clientes",
                "repartidores",
                "tokens_revocados",
            },
        )
        self.assertIs(
            metadata.tables["administradores"],
            Administrador.__table__,
        )
        self.assertIs(metadata.tables["clientes"], Cliente.__table__)
        self.assertIs(
            metadata.tables["repartidores"],
            Repartidor.__table__,
        )
        self.assertIs(
            metadata.tables["tokens_revocados"],
            TokenRevocado.__table__,
        )


if __name__ == "__main__":
    unittest.main()
