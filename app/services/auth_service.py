import hashlib
import hmac
import os
from typing import Optional

from app.config import AUTH_PASSWORD, AUTH_PASSWORD_HASH, AUTH_USERNAME


class AuthService:
    """Simple credential validation with PBKDF2 support (no database)."""

    @staticmethod
    def _pbkdf2_sha256(password: str, salt: bytes, iterations: int = 390000) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    @staticmethod
    def verify_password(password: str) -> bool:
        """Verify against AUTH_PASSWORD_HASH or fallback AUTH_PASSWORD."""
        if AUTH_PASSWORD_HASH:
            # Expected format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
            parts = AUTH_PASSWORD_HASH.split("$")
            if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
                return False

            try:
                iterations = int(parts[1])
                salt = bytes.fromhex(parts[2])
                expected_hash = bytes.fromhex(parts[3])
            except Exception:
                return False

            candidate_hash = AuthService._pbkdf2_sha256(password, salt, iterations)
            return hmac.compare_digest(candidate_hash, expected_hash)

        # Fallback only when hash is not configured.
        if AUTH_PASSWORD is not None:
            return hmac.compare_digest(password, AUTH_PASSWORD)

        return False

    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        if not hmac.compare_digest(username, AUTH_USERNAME):
            return False
        return AuthService.verify_password(password)

    @staticmethod
    def build_password_hash(password: str, iterations: int = 390000) -> str:
        """Utility to generate AUTH_PASSWORD_HASH value."""
        salt = os.urandom(16)
        digest = AuthService._pbkdf2_sha256(password, salt, iterations)
        return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"
