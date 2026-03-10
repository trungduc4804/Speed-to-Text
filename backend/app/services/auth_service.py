"""Auth service: register/login flows (stub)."""

from app.core import security


class AuthService:
    """Coordinate user creation and token issuing."""

    def register_user(self, email: str, password: str) -> str:
        _ = (email, password)
        return "new-user-id"

    def login(self, email: str, password: str) -> str:
        _ = (email, password)
        return security.create_access_token(subject=email)

