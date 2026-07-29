"""Pruebas del detalle persistente del pedido."""

import unittest

from sqlalchemy import CheckConstraint, ForeignKeyConstraint

from app.models import DetallePedido


class DetallePedidoModelTest(unittest.TestCase):
    """Verifica la estructura sin calcular importes ni gestionar stock."""

    def test_columns_are_the_seven_approved_fields(self) -> None:
        """Comprueba los datos que preservan el detalle histórico."""
        columns = DetallePedido.__table__.columns
        self.assertEqual(
            list(columns.keys()),
            [
                "id",
                "pedido_id",
                "plato_id",
                "nombre_plato",
                "precio_unitario",
                "cantidad",
                "subtotal",
            ],
        )
        self.assertTrue(columns.id.primary_key)
        for column_name in list(columns.keys())[1:]:
            self.assertFalse(columns[column_name].nullable)

    def test_constraints_match_the_documented_integrity_rules(self) -> None:
        """Valida relaciones y las tres restricciones numéricas."""
        constraints = list(DetallePedido.__table__.constraints)
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

        self.assertEqual(foreign_keys, {"pedidos.id", "platos.id"})
        self.assertEqual(
            check_names,
            {
                "ck_detalles_pedido_precio_unitario",
                "ck_detalles_pedido_cantidad",
                "ck_detalles_pedido_subtotal",
            },
        )


if __name__ == "__main__":
    unittest.main()
