"""Chain-agnostic signature schemes for Dirac-Wallet.

A ``SignatureScheme`` is a uniform, byte-oriented interface over a concrete signing
algorithm. Two backends are provided:

* :class:`~dirac_wallet.crypto.ed25519.Ed25519Scheme` - classical ed25519 (what the
  Solana chain verifies on-chain today).
* :class:`~dirac_wallet.crypto.mldsa.MLDSAScheme` - post-quantum ML-DSA (FIPS 204),
  used as the wallet's durable quantum identity now and as an on-chain signing scheme
  on a future PQC-capable chain.

Keeping signing behind this interface is what makes the wallet chain-agnostic: a chain
adapter just names the ``scheme_id`` it verifies, and the same wallet code works whether
that is ed25519 or ML-DSA.
"""
from __future__ import annotations

from .base import SignatureScheme
from .ed25519 import Ed25519Scheme
from .mldsa import MLDSAScheme

_REGISTRY: dict[str, SignatureScheme] = {}


def register(scheme: SignatureScheme) -> SignatureScheme:
    _REGISTRY[scheme.scheme_id] = scheme
    return scheme


def get_scheme(scheme_id: str) -> SignatureScheme:
    try:
        return _REGISTRY[scheme_id]
    except KeyError:
        raise KeyError(f"unknown signature scheme {scheme_id!r}; "
                       f"registered: {sorted(_REGISTRY)}") from None


def list_schemes() -> list[str]:
    return sorted(_REGISTRY)


# Default registrations. ML-DSA-65 is the wallet's quantum identity scheme, chosen by
# the dirac-hashes benchmark (best category-3 signature for on-chain use).
register(Ed25519Scheme())
register(MLDSAScheme("ML-DSA-65"))
register(MLDSAScheme("ML-DSA-44"))
register(MLDSAScheme("ML-DSA-87"))

__all__ = ["SignatureScheme", "Ed25519Scheme", "MLDSAScheme",
           "register", "get_scheme", "list_schemes"]
