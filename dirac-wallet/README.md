# Dirac Quantum-Resistant Solana Wallet

A post-quantum cryptographic wallet for Solana with quantum-resistant cryptographic implementations.

## Features

- Quantum-resistant key generation using multiple post-quantum algorithms
- Support for SPHINCS+, Dilithium, and Lamport signatures
- Multiple DiracHash variants for enhanced quantum security
- Solana blockchain integration (testnet)
- CLI interface for wallet management
- Performance benchmarking tools
- Proper conversion between quantum addresses and Solana pubkeys

## Installation

1. Make sure you have Python 3.8+ installed
2. Clone this repository:
   ```bash
   git clone https://github.com/your-username/dirac-crypto.git
   cd dirac-crypto/dirac-wallet
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

We provide a simple bash script for easy wallet management:

```bash
# Make the script executable
chmod +x dirac-wallet.sh

# Create a wallet
./dirac-wallet.sh create my_wallet --sig sphincs --hash dirac_improved

# Check balance
./dirac-wallet.sh balance my_wallet

# Send SOL
./dirac-wallet.sh send my_wallet RECIPIENT_ADDRESS 0.01

# Run the guided demo
./demo.sh
```

## Usage

### Creating a Wallet

Create a new quantum-resistant wallet:

```bash
python -m src.cli create my_wallet --sig-algo sphincs --hash-algo dirac_improved
```

Options:
- `--sig-algo`: Signature algorithm (sphincs, dilithium, lamport)
- `--hash-algo`: Hash algorithm (dirac_standard, dirac_improved, dirac_grover, dirac_shor, quantum_enhanced)
- `--security`: Security level (1-5, higher is more secure)
- `--backup/--no-backup`: Whether to generate backup keys with alternative algorithms
- `--force`: Overwrite existing wallet

### Checking Wallet Balance

```bash
python -m src.cli balance my_wallet
```

### Sending SOL

```bash
python -m src.cli send --wallet my_wallet recipient_address 0.1
```

### Listing Wallets

```bash
python -m src.cli list
```

### Exporting a Wallet

```bash
python -m src.cli export my_wallet --output /path/to/export
```

### Importing a Wallet

```bash
python -m src.cli import /path/to/wallet.json --name new_name
```

### Running Benchmarks

```bash
python -m src.cli benchmark run-all
```

## Architecture

The wallet implements several components:

1. **Quantum Keyring**: Manages quantum-resistant keys and cryptographic operations
   - Implements multiple signature algorithms: SPHINCS+, Dilithium, Lamport
   - Provides encryption/decryption via Kyber KEM
   - Handles address derivation and transaction signing

2. **Wallet Core**: Manages wallet data and blockchain operations
   - Creates and loads wallet files
   - Manages Solana transactions
   - Handles SOL transfers and balance queries

3. **CLI Interface**: User-friendly command-line interface
   - Full wallet management capabilities
   - Rich text output with status indicators
   - Comprehensive command help

4. **Solana Integration**: Connects with the Solana blockchain
   - Proper conversion between quantum addresses and Solana pubkeys
   - Transaction creation and sending
   - Balance checking and account management

## Troubleshooting

If you encounter JSON serialization errors, ensure you're using the latest version which includes fixes for handling binary data in cryptographic keys.

The wallet currently uses testnet for all operations. To use on mainnet, modify the RPC URL in the wallet initialization.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request. 