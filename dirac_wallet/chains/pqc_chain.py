"""Stub adapter for a hypothetical PQC-capable chain.

This is intentionally not networked. Its purpose is to demonstrate that the wallet's
abstractions are genuinely chain-agnostic: on a chain whose validators verify ML-DSA
on-chain, the *same* account/wallet code signs transactions with the post-quantum
scheme and ``on_chain_quantum_resistant`` is ``True`` - no wallet changes required, only
a new adapter. The address here is a base58 SHA3-256 digest of the ML-DSA public key
(a placeholder address format).
"""
from __future__ import annotations

import hashlib

import base58

from .base import ChainAdapter


class PQCChainAdapter(ChainAdapter):
    name = "pqc-preview"
    signing_scheme_id = "ml-dsa-65"
    on_chain_quantum_resistant = True

    def derive_address(self, signing_public_key: bytes) -> str:
        digest = hashlib.sha3_256(signing_public_key).digest()
        return base58.b58encode(digest).decode("ascii")
