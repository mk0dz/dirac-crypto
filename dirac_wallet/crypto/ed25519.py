"""Classical ed25519 backend (what Solana verifies on-chain today)."""
from __future__ import annotations

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature

from .base import SignatureScheme


class Ed25519Scheme(SignatureScheme):
    scheme_id = "ed25519"
    quantum_resistant = False

    def generate(self) -> tuple[bytes, bytes]:
        kp = Keypair()
        return bytes(kp.pubkey()), bytes(kp)

    def from_seed(self, seed: bytes) -> tuple[bytes, bytes]:
        """Deterministically derive a keypair from a 32-byte seed."""
        kp = Keypair.from_seed(seed)
        return bytes(kp.pubkey()), bytes(kp)

    def sign(self, secret_key: bytes, message: bytes) -> bytes:
        return bytes(Keypair.from_bytes(secret_key).sign_message(message))

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        try:
            return Signature.from_bytes(signature).verify(
                Pubkey.from_bytes(public_key), message)
        except Exception:
            return False
