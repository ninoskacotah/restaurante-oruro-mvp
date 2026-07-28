"""Pruebas del endpoint técnico de salud."""

import unittest

from fastapi.testclient import TestClient

from app.main import app


class HealthEndpointTest(unittest.TestCase):
    """Comprueba la respuesta pública del estado de la API."""

    def test_health_endpoint_returns_ok(self) -> None:
        """Verifica el código HTTP y el cuerpo exacto de la respuesta."""
        with TestClient(app) as client:
            response = client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
