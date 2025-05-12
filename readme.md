# Dirac-Wallet

A quantum-resistant Solana wallet using quantum-inspired hash functions and key generation algorithms.

## Features

- Quantum-resistant signatures using Dilithium
- Secure encrypted key storage
- Testnet/Devnet support
- Simple CLI interface
- Ready for post-quantum threats

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the wallet
pip install -e .
```

## Quick Start

```bash
# Create a new wallet
dirac-wallet create

# Check balance
dirac-wallet balance

# Send SOL
dirac-wallet send <recipient_address> <amount>

# Show help
dirac-wallet --help
```

## Security Note

This wallet prioritizes security over performance. Transaction operations may be slower than standard wallets, but your assets are protected against quantum computing threats.

## Development Status

Currently in development. Features:
- ✅ Project setup
- ✅ Key generation
- ✅ Address derivation
- ✅ Transaction signing
- ✅ Network connectivity
- ✅ CLI interface

## License

MIT License
