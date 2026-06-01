"""Post-quantum ML-DSA backend, wrapping the dirac-hashes FIPS 204 implementation.

This is the wallet's durable quantum identity. On Solana it signs off-chain
attestations (binding the quantum identity to the on-chain account); on a future
PQC-capable chain the same scheme would sign transactions verified on-chain.
"""
from __future__ import annotations

import quantum_hash.pqc as pqc

from .base import SignatureScheme


class MLDSAScheme(SignatureScheme):
    quantum_resistant = True

    def __init__(self, level: str = "ML-DSA-65"):
        self._scheme = pqc.get_scheme(level)
        self.level = level
        self.scheme_id = level.lower()  # e.g. "ml-dsa-65"

    def generate(self) -> tuple[bytes, bytes]:
        return self._scheme.keygen()

    def sign(self, secret_key: bytes, message: bytes, context: bytes = b"") -> bytes:
        return self._scheme.sign(secret_key, message, context=context)

    def verify(self, public_key: bytes, message: bytes, signature: bytes,
               context: bytes = b"") -> bool:
        return self._scheme.verify(public_key, message, signature, context=context)
