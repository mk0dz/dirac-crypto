# Dirac-Wallet

A quantum-resistant Solana wallet using post-quantum cryptography signatures and key generation algorithms.

![Dirac Logo](https://raw.githubusercontent.com/mk0dz/assest-store/8de6c656c32a6aacd0a3b1f1533d10f298f58248/solana/Group%2014.svg)

## Features

- **Quantum-Resistant Cryptography**: Uses CRYSTALS-Dilithium for signatures, providing protection against quantum computing attacks
- **Solana Blockchain Support**: Compatible with Solana devnet, testnet, and mainnet
- **Secure Key Storage**: Encrypted wallet files with strong password protection
- **Transaction History**: Track and view your transaction history
- **Interactive CLI**: Easy-to-use command line interface
- **Airdrop Support**: Request test SOL on devnet and testnet with simple commands
- **Multi-Wallet Management**: Create and manage multiple wallets easily

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

- Your private keys are encrypted with your password
- Always back up your wallet files (stored in `~/.dirac_wallet/` by default)
- Keep your password secure - there is no recovery option if forgotten
- Transaction signatures use quantum-resistant algorithms by default
- The wallet is resistant to future quantum computing attacks

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
