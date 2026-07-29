"""Pruebas del modelo persistente de comprobante de pago."""

import unittest

from sqlalchemy import CheckConstraint, ForeignKeyConstraint

from app.models import ComprobantePago


class ComprobantePagoModelTest(unittest.TestCase):
    """Verifica metadatos sin recibir archivos ni revisar pagos."""

    def test_columns_and_pending_fields(self) -> None:
        """Comprueba los once campos y la nulabilidad de la revisión."""
        columns = ComprobantePago.__table__.columns
        self.assertEqual(
            list(columns.keys()),
            [
                "id",
                "pedido_id",
                "administrador_id",
                "archivo_referencia",
                "nombre_generado",
                "tipo_mime",
                "tamanio_bytes",
                "estado_revision",
                "observacion",
                "fecha_envio",
                "fecha_revision",
            ],
        )
        self.assertTrue(columns.id.primary_key)
        self.assertFalse(columns.pedido_id.nullable)
        self.assertTrue(columns.administrador_id.nullable)
        self.assertTrue(columns.observacion.nullable)
        self.assertTrue(columns.fecha_revision.nullable)
        self.assertEqual(
            str(columns.estado_revision.server_default.arg),
            "'PENDIENTE'",
        )

    def test_constraints_match_design(self) -> None:
        """Valida relaciones y protección del tamaño del archivo."""
        constraints = list(ComprobantePago.__table__.constraints)
        foreign_keys = {
            next(iter(item.elements)).target_fullname
            for item in constraints
            if isinstance(item, ForeignKeyConstraint)
        }
        check_names = {
            item.name
            for item in constraints
            if isinstance(item, CheckConstraint)
        }

        self.assertEqual(
            foreign_keys,
            {"pedidos.id", "administradores.id"},
        )
        self.assertEqual(
            check_names,
            {"ck_comprobantes_pago_tamanio_bytes"},
        )


if __name__ == "__main__":
    unittest.main()
