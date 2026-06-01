"""The chain-adapter interface."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..crypto import SignatureScheme, get_scheme


class ChainAdapter(ABC):
    """Maps a wallet account onto a specific blockchain.

    The adapter declares which signature scheme the chain verifies *on-chain* and how
    an address is derived from that scheme's public key. ``on_chain_quantum_resistant``
    is the honesty flag: it is ``False`` for Solana (ed25519) and would be ``True`` for
    a chain that verifies a post-quantum scheme on-chain.
    """

    name: str = ""
    signing_scheme_id: str = ""
    on_chain_quantum_resistant: bool = False

    @property
    def signing_scheme(self) -> SignatureScheme:
        return get_scheme(self.signing_scheme_id)

    @abstractmethod
    def derive_address(self, signing_public_key: bytes) -> str:
        """Derive this chain's account address from the signing public key."""

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<ChainAdapter {self.name} ({self.signing_scheme_id})>"
