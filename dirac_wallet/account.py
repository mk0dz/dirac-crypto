"""Wallet accounts: a chain signing key bound to an ML-DSA quantum identity.

An account holds two independent keypairs:

* the **signing key** for the chain's on-chain scheme (ed25519 for Solana) - this is
  what actually controls funds on that chain;
* the **quantum identity** (ML-DSA) - a durable post-quantum key that signs an
  *attestation* binding the quantum identity to the chain account.

The two are generated independently (fixing the old design, which derived the spend key
from a *public* key) and linked by the attestation, so possession of the quantum key
can be proven against the on-chain address off-chain today, and the very same identity
can sign on-chain on a future PQC-capable chain.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone

from .chains import get_adapter
from .crypto import get_scheme

ATTESTATION_CONTEXT = b"dirac-wallet/account-attestation/v1"


def attestation_message(chain: str, address: str, signing_scheme_id: str,
                        signing_public: bytes) -> bytes:
    """Canonical message the quantum identity signs to claim an account."""
    return b"\n".join([
        ATTESTATION_CONTEXT,
        chain.encode("utf-8"),
        address.encode("utf-8"),
        signing_scheme_id.encode("utf-8"),
        signing_public,
    ])


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.b64decode(text)


@dataclass
class Account:
    chain: str
    address: str
    signing_scheme_id: str
    signing_public: bytes
    signing_secret: bytes
    quantum_scheme_id: str
    quantum_public: bytes
    quantum_secret: bytes
    attestation: bytes
    created_at: str

    # --- signing ------------------------------------------------------------
    def sign_transaction(self, message: bytes) -> bytes:
        """Sign a chain transaction message with the on-chain signing key."""
        return get_scheme(self.signing_scheme_id).sign(self.signing_secret, message)

    def quantum_sign(self, message: bytes) -> bytes:
        """Sign with the post-quantum identity (off-chain attestation/auth)."""
        return get_scheme(self.quantum_scheme_id).sign(self.quantum_secret, message)

    def verify_attestation(self) -> bool:
        """Check that the quantum identity validly claims this account."""
        msg = attestation_message(self.chain, self.address,
                                  self.signing_scheme_id, self.signing_public)
        return get_scheme(self.quantum_scheme_id).verify(
            self.quantum_public, msg, self.attestation)

    @property
    def on_chain_quantum_resistant(self) -> bool:
        return get_adapter(self.chain).on_chain_quantum_resistant

    # --- serialization (secrets included; encrypt at rest) ------------------
    def to_dict(self) -> dict:
        return {
            "chain": self.chain,
            "address": self.address,
            "signing": {
                "scheme": self.signing_scheme_id,
                "public": _b64(self.signing_public),
                "secret": _b64(self.signing_secret),
            },
            "quantum": {
                "scheme": self.quantum_scheme_id,
                "public": _b64(self.quantum_public),
                "secret": _b64(self.quantum_secret),
            },
            "attestation": _b64(self.attestation),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        s, q = data["signing"], data["quantum"]
        return cls(
            chain=data["chain"],
            address=data["address"],
            signing_scheme_id=s["scheme"],
            signing_public=_unb64(s["public"]),
            signing_secret=_unb64(s["secret"]),
            quantum_scheme_id=q["scheme"],
            quantum_public=_unb64(q["public"]),
            quantum_secret=_unb64(q["secret"]),
            attestation=_unb64(data["attestation"]),
            created_at=data["created_at"],
        )

    def public_view(self) -> dict:
        """Non-sensitive summary (no secret keys)."""
        return {
            "chain": self.chain,
            "address": self.address,
            "signing_scheme": self.signing_scheme_id,
            "quantum_scheme": self.quantum_scheme_id,
            "quantum_public_fingerprint": _b64(
                __import__("hashlib").sha256(self.quantum_public).digest()[:8]),
            "on_chain_quantum_resistant": self.on_chain_quantum_resistant,
            "created_at": self.created_at,
        }


def create_account(chain: str = "solana", quantum_level: str = "ml-dsa-65",
                   created_at: str | None = None) -> Account:
    """Generate a fresh account for ``chain`` with an ML-DSA quantum identity."""
    adapter = get_adapter(chain)
    signing = adapter.signing_scheme
    signing_public, signing_secret = signing.generate()
    address = adapter.derive_address(signing_public)

    quantum = get_scheme(quantum_level)
    quantum_public, quantum_secret = quantum.generate()

    attestation = quantum.sign(
        quantum_secret,
        attestation_message(chain, address, signing.scheme_id, signing_public),
    )
    return Account(
        chain=chain,
        address=address,
        signing_scheme_id=signing.scheme_id,
        signing_public=signing_public,
        signing_secret=signing_secret,
        quantum_scheme_id=quantum.scheme_id,
        quantum_public=quantum_public,
        quantum_secret=quantum_secret,
        attestation=attestation,
        created_at=created_at or datetime.now(timezone.utc).isoformat(),
    )
