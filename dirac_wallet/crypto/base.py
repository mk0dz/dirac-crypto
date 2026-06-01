"""The signature-scheme interface used throughout the wallet."""
from __future__ import annotations

from abc import ABC, abstractmethod


class SignatureScheme(ABC):
    """A byte-oriented signing algorithm.

    All keys and signatures are raw ``bytes`` so schemes are interchangeable and the
    wallet never has to know which algorithm a given chain uses.
    """

    #: Stable identifier persisted in wallet files, e.g. ``"ed25519"`` / ``"ml-dsa-65"``.
    scheme_id: str = ""
    #: Whether this scheme resists a cryptographically-relevant quantum computer.
    quantum_resistant: bool = False

    @abstractmethod
    def generate(self) -> tuple[bytes, bytes]:
        """Return a fresh ``(public_key, secret_key)`` pair."""

    @abstractmethod
    def sign(self, secret_key: bytes, message: bytes) -> bytes:
        """Sign ``message`` with ``secret_key``."""

    @abstractmethod
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verify ``signature`` over ``message`` under ``public_key``."""

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<SignatureScheme {self.scheme_id}>"
