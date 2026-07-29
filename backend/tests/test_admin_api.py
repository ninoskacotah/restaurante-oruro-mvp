"""Pruebas HTTP de la API administrativa sin servicios externos."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import (
    AuthContext,
    get_auth_context,
    get_session,
)
from app.core.config import JwtSettings, get_jwt_settings
from app.core.tokens import decode_access_token
from app.main import app
from app.models import Administrador, Plato, TokenRevocado
from app.services import ConflictoServicio


TEST_SETTINGS = JwtSettings(
    jwt_secret=SecretStr("s" * 48),
    _env_file=None,
)


def scalar_result(value: object) -> MagicMock:
    """Simula un resultado con cero o una fila escalar."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def list_result(values: list[object]) -> MagicMock:
    """Simula un resultado con una lista de escalares."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


class AdminApiTest(unittest.TestCase):
    """Comprueba contratos, seguridad y traducción HTTP."""

    def setUp(self) -> None:
        """Prepara dependencias reemplazables por prueba."""
        self.session = MagicMock(spec=AsyncSession)
        self.session.get = AsyncMock()
        self.session.execute = AsyncMock()
        self.session.flush = AsyncMock()
        self.admin = Administrador(
            id=7,
            nombre_usuario="admin",
            credencial_hash="hash-no-expuesto",
            activo=True,
        )
        now = datetime.now(timezone.utc)
        self.claims = {
            "sub": "7",
            "role": "admin",
            "iss": "restaurant-las-retamas-api",
            "aud": "restaurant-las-retamas-panel",
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "jti": "jti-prueba",
        }

        async def session_override():
            yield self.session

        async def auth_override() -> AuthContext:
            return AuthContext(self.admin, self.claims)

        app.dependency_overrides[get_session] = session_override
        app.dependency_overrides[get_auth_context] = auth_override
        app.dependency_overrides[get_jwt_settings] = lambda: TEST_SETTINGS

    def tearDown(self) -> None:
        """Evita que un reemplazo se filtre a otra prueba."""
        app.dependency_overrides.clear()

    def test_openapi_registers_grouped_admin_routes(self) -> None:
        """Confirma los contratos principales bajo /api."""
        paths = app.openapi()["paths"]

        self.assertIn("/api/auth/login", paths)
        self.assertIn("/api/platos", paths)
        self.assertIn("/api/menus", paths)
        self.assertIn("/api/pedidos", paths)
        self.assertIn(
            "/api/comprobantes/{comprobante_id}/revision",
            paths,
        )
        self.assertIn(
            "/api/pedidos/{pedido_id}/seguimiento",
            paths,
        )

    def test_login_returns_valid_bearer_without_hash(self) -> None:
        """Emite JWT y no serializa la credencial persistida."""
        self.session.execute.return_value = scalar_result(self.admin)

        with patch(
            "app.api.routes.auth.verify_password",
            return_value=True,
        ):
            with TestClient(app) as client:
                response = client.post(
                    "/api/auth/login",
                    json={
                        "nombre_usuario": "admin",
                        "contrasena": "correcta",
                    },
                )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["token_type"], "bearer")
        self.assertNotIn("credencial_hash", body)
        claims = decode_access_token(
            body["access_token"],
            TEST_SETTINGS.jwt_secret,
        )
        self.assertIsNotNone(claims)

    def test_login_rejects_credentials_uniformly(self) -> None:
        """No revela si el nombre de usuario estaba registrado."""
        self.session.execute.return_value = scalar_result(None)

        with TestClient(app) as client:
            response = client.post(
                "/api/auth/login",
                json={
                    "nombre_usuario": "desconocido",
                    "contrasena": "incorrecta",
                },
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Credenciales incorrectas."})

    def test_logout_persists_only_jti_and_expiration(self) -> None:
        """Registra la revocación sin copiar el Bearer token."""
        with TestClient(app) as client:
            response = client.post(
                "/api/auth/logout",
                headers={"Authorization": "Bearer valor-no-persistido"},
            )

        self.assertEqual(response.status_code, 204)
        revoked = self.session.add.call_args.args[0]
        self.assertIsInstance(revoked, TokenRevocado)
        self.assertEqual(revoked.jti, "jti-prueba")
        self.assertFalse(hasattr(revoked, "token"))

    def test_plato_contract_rejects_negative_price(self) -> None:
        """Detiene la entrada inválida antes de llamar al servicio."""
        with TestClient(app) as client:
            response = client.post(
                "/api/platos",
                json={
                    "nombre": "Plato",
                    "descripcion": None,
                    "precio": "-1.00",
                    "activo": True,
                },
            )

        self.assertEqual(response.status_code, 422)
        self.session.add.assert_not_called()

    def test_list_platos_returns_safe_contract(self) -> None:
        """Serializa el catálogo sin atributos internos."""
        plato = Plato(
            id=1,
            nombre="Sopa",
            descripcion="Del día",
            precio=Decimal("12.00"),
            activo=True,
        )
        self.session.execute.return_value = list_result([plato])

        with TestClient(app) as client:
            response = client.get("/api/platos")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["nombre"], "Sopa")

    def test_service_conflict_is_translated_to_http_409(self) -> None:
        """Evita exponer una traza ante reglas de estado."""
        with patch(
            "app.api.routes.catalogo.crear_plato",
            new=AsyncMock(side_effect=ConflictoServicio("Duplicado.")),
        ):
            with TestClient(app) as client:
                response = client.post(
                    "/api/platos",
                    json={
                        "nombre": "Sopa",
                        "descripcion": None,
                        "precio": "12.00",
                        "activo": True,
                    },
                )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {"detail": "Duplicado."})


class AuthDependencyTest(unittest.IsolatedAsyncioTestCase):
    """Comprueba revocación e identidad fuera del transporte HTTP."""

    async def test_valid_bearer_requires_active_non_revoked_admin(self) -> None:
        """Acepta únicamente la combinación completa de controles."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock(return_value=scalar_result(None))
        session.get = AsyncMock(
            return_value=Administrador(
                id=7,
                nombre_usuario="admin",
                credencial_hash="hash",
                activo=True,
            )
        )
        from app.core.tokens import create_access_token

        token = create_access_token(7, TEST_SETTINGS.jwt_secret)
        context = await get_auth_context(
            HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=token,
            ),
            session,
            TEST_SETTINGS,
        )

        self.assertEqual(context.administrador.id, 7)

    async def test_revoked_bearer_is_rejected(self) -> None:
        """Rechaza el token antes de cargar el administrador."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock(return_value=scalar_result(1))
        session.get = AsyncMock()
        from app.core.tokens import create_access_token

        token = create_access_token(7, TEST_SETTINGS.jwt_secret)
        with self.assertRaises(HTTPException) as captured:
            await get_auth_context(
                HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=token,
                ),
                session,
                TEST_SETTINGS,
            )

        self.assertEqual(captured.exception.status_code, 401)
        session.get.assert_not_awaited()

    async def test_missing_or_invalid_bearer_is_rejected(self) -> None:
        """Aplica la misma respuesta a ausencia y token ilegible."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.get = AsyncMock()

        for credentials in (
            None,
            HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="token-invalido",
            ),
        ):
            with self.subTest(credentials=credentials):
                with self.assertRaises(HTTPException) as captured:
                    await get_auth_context(
                        credentials,
                        session,
                        TEST_SETTINGS,
                    )
                self.assertEqual(captured.exception.status_code, 401)

    async def test_inactive_administrator_is_rejected(self) -> None:
        """Invalida una sesión si la identidad fue deshabilitada."""
        session = MagicMock(spec=AsyncSession)
        session.execute = AsyncMock(return_value=scalar_result(None))
        session.get = AsyncMock(
            return_value=Administrador(
                id=7,
                nombre_usuario="admin",
                credencial_hash="hash",
                activo=False,
            )
        )
        from app.core.tokens import create_access_token

        token = create_access_token(7, TEST_SETTINGS.jwt_secret)
        with self.assertRaises(HTTPException) as captured:
            await get_auth_context(
                HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials=token,
                ),
                session,
                TEST_SETTINGS,
            )

        self.assertEqual(captured.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
