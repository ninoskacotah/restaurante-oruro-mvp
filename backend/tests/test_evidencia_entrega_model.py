"""Pruebas del modelo persistente de evidencia de entrega."""

import unittest

from sqlalchemy import CheckConstraint, ForeignKeyConstraint

from app.models import EvidenciaEntrega


class EvidenciaEntregaModelTest(unittest.TestCase):
    """Verifica referencias sin almacenar fotografías ni validar códigos."""

    def test_fields_and_optional_file_metadata(self) -> None:
        """Comprueba los siete campos para fotografía o código."""
        columns = EvidenciaEntrega.__table__.columns
        self.assertEqual(
            list(columns.keys()),
            [
                "id",
                "asignacion_id",
                "tipo",
                "valor_referencia",
                "tipo_mime",
                "tamanio_bytes",
                "fecha_registro",
            ],
        )
        self.assertTrue(columns.tipo_mime.nullable)
        self.assertTrue(columns.tamanio_bytes.nullable)
        self.assertFalse(columns.valor_referencia.nullable)

    def test_relation_and_size_constraint(self) -> None:
        """Valida la asignación y el tamaño opcional no negativo."""
        constraints = list(EvidenciaEntrega.__table__.constraints)
        foreign_keys = {
            next(iter(item.elements)).target_fullname
            for item in constraints
            if isinstance(item, ForeignKeyConstraint)
        }
        checks = {
            item.name
            for item in constraints
            if isinstance(item, CheckConstraint)
        }

        self.assertEqual(foreign_keys, {"asignaciones.id"})
        self.assertEqual(
            checks,
            {"ck_evidencias_entrega_tamanio_bytes"},
        )


if __name__ == "__main__":
    unittest.main()
