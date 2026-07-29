"""Pruebas del servicio aislado de tokens administrativos."""

from datetime import datetime, timedelta, timezone
import unittest

import jwt
from pydantic import SecretStr

from app.core.tokens import (
    JWT_AUDIENCE,
    JWT_ISSUER,
    JWT_LIFETIME,
    JWT_REQUIRED_CLAIMS,
    JWT_ROLE,
    create_access_token,
    decode_access_token,
)


TEST_SECRET = SecretStr("s" * 48)


class AccessTokenTest(unittest.TestCase):
    """Comprueba JWT sin autenticar ni consultar administradores."""

    def test_valid_token_contains_all_approved_claims(self) -> None:
        """Valida identidad, rol, emisor, audiencia y duración."""
        token = create_access_token(7, TEST_SECRET)
        claims = decode_access_token(token, TEST_SECRET)

        self.assertIsNotNone(claims)
        assert claims is not None
        self.assertTrue(set(JWT_REQUIRED_CLAIMS).issubset(claims))
        self.assertEqual(claims["sub"], "7")
        self.assertEqual(claims["role"], JWT_ROLE)
        self.assertEqual(claims["iss"], JWT_ISSUER)
        self.assertEqual(claims["aud"], JWT_AUDIENCE)
        self.assertEqual(
            claims["exp"] - claims["iat"],
            int(JWT_LIFETIME.total_seconds()),
        )

    def test_each_token_receives_a_different_jti(self) -> None:
        """Impide reutilizar un identificador entre dos sesiones."""
        first = decode_access_token(
            create_access_token(7, TEST_SECRET),
            TEST_SECRET,
        )
        second = decode_access_token(
            create_access_token(7, TEST_SECRET),
            TEST_SECRET,
        )

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        assert first is not None and second is not None
        self.assertNotEqual(first["jti"], second["jti"])

    def test_expired_token_is_rejected(self) -> None:
        """Rechaza un vencimiento que supera la tolerancia permitida."""
        old_time = datetime.now(timezone.utc) - timedelta(minutes=16)
        token = create_access_token(7, TEST_SECRET, issued_at=old_time)

        self.assertIsNone(decode_access_token(token, TEST_SECRET))

    def test_token_inside_leeway_is_accepted(self) -> None:
        """Tolera hasta 30 segundos de diferencia temporal."""
        old_time = datetime.now(timezone.utc) - timedelta(
            minutes=15,
            seconds=20,
        )
        token = create_access_token(7, TEST_SECRET, issued_at=old_time)

        self.assertIsNotNone(decode_access_token(token, TEST_SECRET))

    def test_tampered_token_is_rejected(self) -> None:
        """Detecta cambios posteriores a la firma."""
        token = create_access_token(7, TEST_SECRET)
        header, payload, signature = token.split(".")
        replacement = "a" if signature[0] != "a" else "b"
        tampered_token = (
            f"{header}.{payload}.{replacement}{signature[1:]}"
        )

        self.assertIsNone(decode_access_token(tampered_token, TEST_SECRET))

    def test_wrong_issuer_audience_or_role_is_rejected(self) -> None:
        """Aplica los tres valores fijos establecidos en DT-014."""
        for changed_claim in ("iss", "aud", "role"):
            with self.subTest(claim=changed_claim):
                payload = self._valid_payload()
                payload[changed_claim] = "valor-no-autorizado"
                token = jwt.encode(
                    payload,
                    TEST_SECRET.get_secret_value(),
                    algorithm="HS256",
                )

                self.assertIsNone(decode_access_token(token, TEST_SECRET))

    def test_missing_required_claim_is_rejected(self) -> None:
        """Exige que el token incluya todas las claims aprobadas."""
        payload = self._valid_payload()
        del payload["jti"]
        token = jwt.encode(
            payload,
            TEST_SECRET.get_secret_value(),
            algorithm="HS256",
        )

        self.assertIsNone(decode_access_token(token, TEST_SECRET))

    def test_different_algorithm_is_rejected(self) -> None:
        """No confía en el algoritmo declarado por el encabezado."""
        token = jwt.encode(
            self._valid_payload(),
            TEST_SECRET.get_secret_value(),
            algorithm="HS384",
        )

        self.assertIsNone(decode_access_token(token, TEST_SECRET))

    @staticmethod
    def _valid_payload() -> dict[str, object]:
        """Construye claims ficticias para escenarios de rechazo."""
        now = datetime.now(timezone.utc)
        return {
            "sub": "7",
            "role": JWT_ROLE,
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
            "iat": now,
            "nbf": now,
            "exp": now + JWT_LIFETIME,
            "jti": "jti-ficticio",
        }


if __name__ == "__main__":
    unittest.main()
