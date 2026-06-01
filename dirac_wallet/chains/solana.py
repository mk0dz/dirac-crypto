"""Solana chain adapter.

Solana validators verify **ed25519** on-chain, so that is the signing scheme here and
``on_chain_quantum_resistant`` is ``False``. The wallet's post-quantum protection on
Solana is the ML-DSA quantum identity that attests to ownership off-chain - it does not
and cannot make the on-chain account quantum-safe. The address is the base58 ed25519
public key, exactly as Solana expects.
"""
from __future__ import annotations

from solders.hash import Hash
from solders.keypair import Keypair
from solders.message import Message
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction

from .base import ChainAdapter


class SolanaAdapter(ChainAdapter):
    name = "solana"
    signing_scheme_id = "ed25519"
    on_chain_quantum_resistant = False

    def derive_address(self, signing_public_key: bytes) -> str:
        return str(Pubkey.from_bytes(signing_public_key))

    def build_signed_transfer(self, account, recipient: str, lamports: int,
                              recent_blockhash: str) -> Transaction:
        """Build and ed25519-sign a SOL transfer from ``account``.

        Signs with the account's on-chain key (ed25519) - the same key Solana
        validators verify. Returns a fully-signed solders ``Transaction``.
        """
        sender = Pubkey.from_string(account.address)
        instruction = transfer(TransferParams(
            from_pubkey=sender,
            to_pubkey=Pubkey.from_string(recipient),
            lamports=lamports,
        ))
        blockhash = Hash.from_string(recent_blockhash)
        message = Message.new_with_blockhash([instruction], sender, blockhash)
        keypair = Keypair.from_bytes(account.signing_secret)
        return Transaction([keypair], message, blockhash)
