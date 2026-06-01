"""End-to-end tests for the chain-agnostic PQC wallet layer."""
import json

import pytest
from solders.pubkey import Pubkey

from dirac_wallet.account import Account, create_account
from dirac_wallet.chains import get_adapter, list_chains
from dirac_wallet.crypto import get_scheme, list_schemes
from dirac_wallet.vault import LegacyWalletError, Vault


def test_registries_populated():
    assert "ed25519" in list_schemes()
    assert "ml-dsa-65" in list_schemes()
    assert {"solana", "pqc-preview"} <= set(list_chains())


def test_solana_account_is_honest():
    acct = create_account("solana")
    # Address is a real ed25519 Solana pubkey derived from the signing key.
    assert str(Pubkey.from_bytes(acct.signing_public)) == acct.address
    assert acct.signing_scheme_id == "ed25519"
    assert acct.quantum_scheme_id == "ml-dsa-65"
    # Solana stays ed25519 on-chain; the honesty flag says so.
    assert acct.on_chain_quantum_resistant is False
    # The quantum identity validly attests to the account.
    assert acct.verify_attestation()
    # Spend key is NOT derived from the quantum public key (the old bug).
    assert acct.signing_public not in (acct.quantum_public, acct.quantum_secret)


def test_transaction_signing_roundtrip():
    acct = create_account("solana")
    msg = b"transfer 1 SOL to Alice"
    sig = acct.sign_transaction(msg)
    scheme = get_scheme(acct.signing_scheme_id)
    assert scheme.verify(acct.signing_public, msg, sig)
    assert not scheme.verify(acct.signing_public, b"tampered", sig)


def test_quantum_identity_signs():
    acct = create_account("solana")
    msg = b"off-chain quantum-signed statement"
    sig = acct.quantum_sign(msg)
    q = get_scheme(acct.quantum_scheme_id)
    assert q.verify(acct.quantum_public, msg, sig)
    assert not q.verify(acct.quantum_public, msg + b"x", sig)


def test_attestation_detects_tampering():
    acct = create_account("solana")
    assert acct.verify_attestation()
    acct.address = str(Pubkey.from_bytes(create_account("solana").signing_public))
    assert not acct.verify_attestation()


def test_pqc_chain_is_quantum_resistant_on_chain():
    acct = create_account("pqc-preview")
    adapter = get_adapter("pqc-preview")
    assert adapter.on_chain_quantum_resistant is True
    assert acct.signing_scheme_id == "ml-dsa-65"  # signs with PQC on this chain
    assert acct.on_chain_quantum_resistant is True
    assert acct.verify_attestation()
    msg = b"pqc-chain transfer"
    sig = acct.sign_transaction(msg)
    assert get_scheme("ml-dsa-65").verify(acct.signing_public, msg, sig)


def test_vault_roundtrip_and_bad_password(tmp_path):
    acct = create_account("solana")
    vault = Vault(tmp_path / "alice_solana.dwf")
    vault.save(acct, "correct horse battery staple",
               transaction_history=[{"signature": "abc", "amount": 1.0}])
    assert vault.exists()

    loaded, history = vault.load("correct horse battery staple")
    assert loaded.address == acct.address
    assert loaded.signing_secret == acct.signing_secret
    assert loaded.verify_attestation()
    assert history == [{"signature": "abc", "amount": 1.0}]

    with pytest.raises(ValueError):
        vault.load("wrong password")


def test_account_dict_roundtrip():
    acct = create_account("solana")
    restored = Account.from_dict(acct.to_dict())
    assert restored.address == acct.address
    assert restored.signing_secret == acct.signing_secret
    assert restored.quantum_secret == acct.quantum_secret
    assert restored.verify_attestation()
    # public_view leaks no secrets
    view = restored.public_view()
    blob = json.dumps(view)
    import base64
    assert base64.b64encode(acct.signing_secret).decode() not in blob


def test_legacy_v1_file_rejected(tmp_path):
    from dirac_wallet.core.storage import SecureStorage
    path = tmp_path / "old_devnet.dwf"
    v1_doc = {"keypair": {"algorithm": "dilithium"}, "info": {"address": "x"},
              "transaction_history": []}
    enc = SecureStorage().encrypt(json.dumps(v1_doc).encode(), "pw")
    path.write_bytes(enc)
    with pytest.raises(LegacyWalletError):
        Vault(path).load("pw")
