# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Solana wallet (`dirac-wallet`) with a **chain-agnostic signing architecture** and a real post-quantum (ML-DSA) identity — a Python CLI package plus a separate Next.js marketing/docs site under `web/`.

Honest security model (this is the crux — read it before touching crypto):
- **On-chain, Solana verifies ed25519 only.** Funds on Solana are controlled by an ordinary ed25519 key. Nothing the wallet does makes the on-chain account quantum-safe; that is a chain-level property the wallet cannot change.
- Each account *also* holds a **post-quantum ML-DSA-65 identity** (FIPS 204, from the `dirac-hashes` library) that signs an **attestation** binding the quantum identity to the chain account. This is real PQC used off-chain (ownership proof, quantum-safe auth), not theater.
- The `crypto/` + `chains/` abstractions mean the same wallet code runs on a future PQC-capable chain where the signing scheme *is* ML-DSA and on-chain verification is genuinely quantum-safe (`ChainAdapter.on_chain_quantum_resistant`).

The PQC comes from the sibling `dirac-hashes` project, which now provides **NIST-ACVP-validated** ML-KEM/ML-DSA/SLH-DSA (pure Python, research-grade / not constant-time). Earlier versions of both repos used fake/"simplified" Dilithium and derived the ed25519 spend key from a *public* key; that is gone.

## Commands

```bash
# Install the package in editable mode (pulls quantum_hash via the dirac-hashes dependency)
pip install -e .

# Run the CLI (entry point: dirac_wallet.cli.commands:cli)
dirac-wallet create mywallet
dirac-wallet --help

# Tests (pytest is configured but tests are written as unittest.TestCase)
pytest                                          # all tests
pytest tests/test_wallet.py                     # one file
pytest tests/test_wallet.py::TestWallet::test_create_wallet   # one test

# Formatting (line length 88, isort uses the black profile)
black .
isort .

# Web site (separate Node project)
cd web && npm install
npm run dev      # next dev --turbopack
npm run build
npm run lint
```

Note: `tests/test_network.py` and parts of `test_transactions.py` hit **live Solana RPC endpoints** and will be slow or fail offline. Async tests drive the event loop themselves with `asyncio.run(...)` inside synchronous `unittest` methods — there is no `pytest-asyncio` marker usage despite the dependency being listed.

## Architecture

The current (v2) wallet is built around two small abstraction layers. The legacy
`core/` modules (`wallet.py`/`keys.py`/`address.py`/`transactions.py`, the old
`DiracWallet`) still exist but are **superseded** — new work goes through the layers
below.

### `crypto/` — signature schemes (chain-agnostic)
`crypto/base.py::SignatureScheme` is a byte-oriented `generate/sign/verify` interface
with two backends:
- `crypto/ed25519.py::Ed25519Scheme` (`scheme_id="ed25519"`) — wraps solders; what Solana verifies on-chain.
- `crypto/mldsa.py::MLDSAScheme` (`scheme_id="ml-dsa-65"`) — wraps `quantum_hash.pqc` ML-DSA (FIPS 204).
Schemes self-register in `crypto/__init__.py`; look them up with `crypto.get_scheme(id)`.

### `chains/` — chain adapters
`chains/base.py::ChainAdapter` names the `signing_scheme_id` a chain verifies on-chain,
exposes `derive_address(public_key)`, and carries the honesty flag
`on_chain_quantum_resistant`. `chains/solana.py::SolanaAdapter` (ed25519, flag **False**,
plus `build_signed_transfer(...)`) is the live one; `chains/pqc_chain.py::PQCChainAdapter`
(ml-dsa-65, flag **True**) is a non-networked stub proving the seam — the same wallet
code would do real on-chain PQC there. Look up via `chains.get_adapter(name)`.

### `account.py` — the account model
`create_account(chain)` generates an **independent** ed25519 spend key and an ML-DSA
quantum identity, then signs an **attestation** (`attestation_message(...)`) binding the
quantum identity to the chain address. `Account.sign_transaction` uses the on-chain
scheme; `Account.quantum_sign`/`verify_attestation` use the PQC identity. The spend key
is **not** derived from any public key (the old bug). `to_dict`/`from_dict` round-trip
all keys (secrets included → encrypt at rest); `public_view()` is the secret-free summary.

### `vault.py` — encrypted `.dwf` storage (format v2)
`Vault.save/load` wrap a v2 JSON doc (`{version:2, account, transaction_history}`) in
AES-256-GCM via `core/storage.py::SecureStorage` (on-disk: `salt[16]+nonce[12]+tag[16]+ct`).
Files live at `~/.dirac_wallet/{name}_{network}.dwf`. Pre-v2 files are detected and
**rejected** with `LegacyWalletError` (their crypto was broken) — there is no silent migration.

### Network + CLI
`network/solana_client.py::QuantumSolanaClient` (unchanged) wraps `AsyncClient` with a
per-network endpoint list + fallback, plus airdrop/faucet/history helpers; all async.
`cli/commands.py` is the `click` group (`create/info/balance/send/airdrop/history/list-wallets`),
rewired onto `Vault`+`Account`+`SolanaAdapter`, bridging async with `asyncio.run(...)`.
`send` builds the transfer via `SolanaAdapter.build_signed_transfer` (ed25519) and submits
through the client. Default network is **`devnet`**.

## Gotchas

- **Two PQC namespaces in `dirac-hashes`:** the real, NIST-validated code is `quantum_hash.pqc` (ML-KEM/ML-DSA/SLH-DSA). The old `quantum_hash.signatures`/`quantum_hash.kem` toy modules still exist and are imported transitively by the legacy `core/` files — do not use them. `DiracHash` is a separate hash offering, never a PQC primitive.
- **dirac-hashes install:** the wallet needs the local `dirac-hashes` (branch `feat/real-pqc`) installed: `DIRAC_PURE_PYTHON=1 pip install -e ../dirac-hashes --no-build-isolation --no-deps` (the `DIRAC_PURE_PYTHON` flag skips the optional legacy C extensions).
- **`config/config.yml` is dead config.** `utils/logger.py` looks for `config/config.yaml` (wrong extension) and falls back to defaults; nothing loads the YAML. Defaults are hardcoded (CLI `devnet`, quantum identity `ML-DSA-65`).
- Live devnet **airdrop is frequently rate-limited** ("Internal error"); the CLI prints a faucet fallback. A full live `send` needs a funded account.
- There is **no key/password recovery**. Losing the password makes a `.dwf` permanently undecryptable.
- The `core/` legacy modules and `tests/test_wallet.py|test_transactions.py|test_network.py` target the old `DiracWallet`; the new layer is covered by `tests/test_pqc_wallet.py`.
