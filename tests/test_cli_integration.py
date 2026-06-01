"""Offline CLI integration tests (no network) using click's test runner."""
from click.testing import CliRunner

from dirac_wallet.cli.commands import cli


def _create(runner, name="w", path="w.dwf", pw="pw123"):
    return runner.invoke(cli, ["create", name, "--path", path], input=f"{pw}\n{pw}\n")


def test_create_then_info_roundtrip():
    runner = CliRunner()
    with runner.isolated_filesystem():
        r = _create(runner)
        assert r.exit_code == 0, r.output
        assert "Wallet created successfully" in r.output
        assert "ML-DSA-65" in r.output
        assert "attestation valid: True" in r.output

        info = runner.invoke(cli, ["info", "w", "--path", "w.dwf"], input="pw123\n")
        assert info.exit_code == 0
        assert "ed25519" in info.output
        assert "ml-dsa-65" in info.output
        assert "Attestation Valid" in info.output


def test_wrong_password_rejected():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _create(runner)
        bad = runner.invoke(cli, ["info", "w", "--path", "w.dwf"], input="nope\n")
        assert "Invalid password" in bad.output


def test_duplicate_create_rejected():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _create(runner)
        dup = runner.invoke(cli, ["create", "w", "--path", "w.dwf"], input="x\nx\n")
        assert "already exists" in dup.output


def test_password_mismatch_then_retry():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # First pair mismatches, second pair matches.
        r = runner.invoke(cli, ["create", "w", "--path", "w.dwf"],
                          input="a\nb\nsecret\nsecret\n")
        assert r.exit_code == 0
        assert "do not match" in r.output
        assert "Wallet created successfully" in r.output


def test_empty_history():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _create(runner)
        h = runner.invoke(cli, ["history", "w", "--path", "w.dwf"], input="pw123\n")
        assert "No transaction history" in h.output


def test_send_builds_valid_signed_transaction(tmp_path):
    """The Solana adapter produces a real, validly-signed ed25519 transaction."""
    from solders.hash import Hash
    from solders.keypair import Keypair

    from dirac_wallet.account import create_account
    from dirac_wallet.chains import get_adapter

    account = create_account("solana")
    adapter = get_adapter("solana")
    recipient = str(Keypair().pubkey())
    blockhash = str(Hash.default())

    tx = adapter.build_signed_transfer(account, recipient, 1_000_000, blockhash)
    # One signature, present, and the transaction serializes.
    assert len(tx.signatures) == 1
    raw = bytes(tx)
    assert len(raw) > 64
    # The signature verifies against the account's on-chain (ed25519) public key.
    from solders.pubkey import Pubkey
    sig = tx.signatures[0]
    assert sig.verify(Pubkey.from_string(account.address), bytes(tx.message))
