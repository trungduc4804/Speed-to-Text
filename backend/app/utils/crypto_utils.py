"""RSA keypair generation, sign/verify helpers (stub)."""


def generate_keypair() -> tuple[str, str]:
    """Return (private_pem, public_pem) placeholders."""
    return ("private-key", "public-key")


def sign_digest(private_key: str, digest: bytes) -> str:
    """Return signature placeholder."""
    _ = (private_key, digest)
    return "signature"

