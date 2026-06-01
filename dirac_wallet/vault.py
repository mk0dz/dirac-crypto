"""Encrypted wallet-file storage (format v2).

A vault is the on-disk ``.dwf`` file: a v2 JSON document (account + transaction
history) encrypted with AES-256-GCM via :class:`dirac_wallet.core.storage.SecureStorage`
(password -> PBKDF2 key). The old v1 format stored a toy-Dilithium keypair and derived
its spend key from a *public* key; that scheme is insecure and cannot be safely carried
forward, so v1 files are detected and rejected with guidance rather than silently
"migrated".
"""
from __future__ import annotations

import json
from pathlib import Path

from .account import Account
from .core.storage import SecureStorage

WALLET_VERSION = 2


class LegacyWalletError(Exception):
    """Raised when a pre-v2 wallet file is opened (its crypto is not trustworthy)."""


class Vault:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.storage = SecureStorage()

    def exists(self) -> bool:
        return self.path.exists()

    def save(self, account: Account, password: str,
             transaction_history: list | None = None) -> None:
        doc = {
            "version": WALLET_VERSION,
            "account": account.to_dict(),
            "transaction_history": transaction_history or [],
        }
        encrypted = self.storage.encrypt(json.dumps(doc).encode("utf-8"), password)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(encrypted)

    def load(self, password: str) -> tuple[Account, list]:
        raw = self.path.read_bytes()
        # SecureStorage.decrypt raises ValueError on a bad password / tampering.
        data = self.storage.decrypt(raw, password)
        doc = json.loads(data.decode("utf-8"))
        if doc.get("version") != WALLET_VERSION or "account" not in doc:
            raise LegacyWalletError(
                "This wallet uses the insecure pre-v2 format (toy Dilithium with a "
                "spend key derived from a public key). It cannot be safely upgraded. "
                "Create a new wallet with `dirac-wallet create` and move any devnet "
                "funds to its address."
            )
        account = Account.from_dict(doc["account"])
        return account, doc.get("transaction_history", [])
