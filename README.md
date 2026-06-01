# Dirac-Wallet

A Solana wallet with a **post-quantum (ML-DSA) identity** and a chain-agnostic signing
architecture.

> **Honest scope.** Solana validators verify **ed25519** on-chain, so funds on Solana are
> protected by ed25519 — *not* quantum-safe against a future quantum computer, and no
> client wallet can change that. What Dirac-Wallet adds is a real, NIST-validated
> **ML-DSA-65** (FIPS 204) quantum identity per account that signs an off-chain
> *attestation* binding it to the on-chain address, plus a chain-adapter abstraction so
> the same wallet runs with genuine on-chain PQC on a future quantum-safe chain. The PQC
> comes from the `dirac-hashes` library (validated against NIST ACVP vectors;
> pure-Python, research-grade — not constant-time, not for securing real funds yet).

![Dirac Logo](https://raw.githubusercontent.com/mk0dz/assest-store/8de6c656c32a6aacd0a3b1f1533d10f298f58248/solana/Group%2014.svg)

## Features

- **Quantum-Resistant Cryptography**: Uses CRYSTALS-Dilithium for signatures, providing protection against quantum computing attacks
- **Solana Blockchain Support**: Compatible with Solana devnet, testnet, and mainnet
- **Secure Key Storage**: Encrypted wallet files with strong password protection
- **Transaction History**: Track and view your transaction history
- **Interactive CLI**: Easy-to-use command line interface
- **Airdrop Support**: Request test SOL on devnet and testnet with simple commands
- **Multi-Wallet Management**: Create and manage multiple wallets easily

## Comparison with Traditional Wallets

| Feature | Traditional Solana Wallets | Dirac-Wallet |
|---------|---------------------------|--------------|
| **On-chain signing (Solana)** | ed25519 | ed25519 (same — chain requirement) |
| **On-chain quantum safety** | None | None on Solana (chain-level limitation) |
| **Post-quantum identity** | None | Real ML-DSA-65 (FIPS 204), off-chain attestation |
| **Quantum-safe encryption/auth** | None | Off-chain via the ML-DSA identity |
| **Chain-agnostic signing** | No | Yes — adapter for a future on-chain-PQC chain |
| **Compatibility** | Solana ecosystem | Fully compatible with Solana |

Dirac-Wallet does **not** claim to make on-chain Solana funds quantum-safe — that is impossible from a client while Solana verifies only ed25519. It adds a real, NIST-validated post-quantum identity (used off-chain today) and an architecture ready for a chain that verifies PQC on-chain. See the `dirac-hashes` project for the validated ML-KEM/ML-DSA/SLH-DSA implementations and benchmarks.

## Installation

### From PyPI

```bash
pip install dirac-wallet
```

### From Source

```bash
# Clone the repository
git clone https://github.com/dirac-labs/dirac-wallet.git
cd dirac-wallet

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies and package
pip install -e .
```

## Quick Start

```bash
# Create a new wallet named "mywallet"
dirac-wallet create mywallet

# Get test SOL from devnet (default network)
dirac-wallet airdrop mywallet

# Check your balance
dirac-wallet balance mywallet

# Send SOL to another address
dirac-wallet send mywallet <recipient_address> <amount>

# View transaction history
dirac-wallet history mywallet

# View wallet information
dirac-wallet info mywallet

# List all your wallets
dirac-wallet list-wallets
```

## Command Reference

| Command | Description |
|---------|-------------|
| `create <name>` | Create a new wallet |
| `balance <name>` | Check wallet balance |
| `send <name> <recipient> <amount>` | Send SOL to another address |
| `airdrop <name> [amount]` | Request SOL airdrop (devnet/testnet only) |
| `info <name>` | Show wallet information |
| `history <name>` | Show transaction history |
| `list-wallets` | List all wallets in the default directory |

### Global Options

* `--network` or `-n`: Specify network (devnet, testnet, mainnet). Default is `devnet`.
* `--path` or `-p`: Specify custom wallet file path.

## Networks

Dirac-Wallet supports three Solana networks:

- `devnet` (default): Development network with test tokens
- `testnet`: Test network with test tokens
- `mainnet`: Production network with real SOL (use with caution)

Example usage with network specification:
```bash
dirac-wallet create mywallet --network mainnet
```

## Security Notes

- Your keys are encrypted at rest with your password (AES-256-GCM); there is **no** recovery if forgotten
- Always back up your wallet files (stored in `~/.dirac_wallet/` by default)
- **On-chain Solana transactions are signed with ed25519** — quantum-safe *only* once Solana itself supports a post-quantum scheme. The ML-DSA quantum identity is an off-chain attestation/auth layer, not on-chain protection
- The post-quantum code is **research-grade** (pure-Python, not constant-time); do not rely on it to protect mainnet funds
- Pre-v2 wallet files (older toy-Dilithium format) are intentionally rejected — create a fresh wallet

## Development Status

Dirac-Wallet is currently in beta. Use on mainnet with caution.

- ✅ Key generation and storage
- ✅ Transaction signing and verification
- ✅ Network connectivity and transaction submission
- ✅ Command line interface
- ✅ Transaction history
- ✅ Multi-wallet support
- ✅ Quantum-resistant cryptography

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Acknowledgments

- Solana Foundation for blockchain infrastructure
- NIST for post-quantum cryptography standardization
