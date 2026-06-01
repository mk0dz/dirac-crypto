"""Chain adapters: how an account maps onto a specific blockchain.

A :class:`~dirac_wallet.chains.base.ChainAdapter` names the signature scheme a chain
verifies on-chain and knows how to turn a signing public key into that chain's address.
Today only :class:`~dirac_wallet.chains.solana.SolanaAdapter` is networked; the PQC
adapter is a stub that demonstrates the seam a future quantum-safe chain would slot into.
"""
from __future__ import annotations

from .base import ChainAdapter
from .pqc_chain import PQCChainAdapter
from .solana import SolanaAdapter

_REGISTRY: dict[str, ChainAdapter] = {}


def register(adapter: ChainAdapter) -> ChainAdapter:
    _REGISTRY[adapter.name] = adapter
    return adapter


def get_adapter(name: str) -> ChainAdapter:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(f"unknown chain {name!r}; registered: {sorted(_REGISTRY)}") from None


def list_chains() -> list[str]:
    return sorted(_REGISTRY)


register(SolanaAdapter())
register(PQCChainAdapter())

__all__ = ["ChainAdapter", "SolanaAdapter", "PQCChainAdapter",
           "register", "get_adapter", "list_chains"]
