# Dirac-Wallet Quick Start Guide

## What is Dirac-Wallet?

Dirac-Wallet is a quantum-resistant cryptocurrency wallet for Solana. It uses quantum-resistant cryptography (Dilithium) to protect your assets from future quantum computing threats.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd dirac-wallet
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## First Steps

### 1. Create Your First Wallet

```bash
dirac-wallet create
```

You'll be prompted to create a password. **Save this password securely - it cannot be recovered!**

### 2. Get Some Test SOL

Request an airdrop (works on devnet/testnet only):

```bash
dirac-wallet airdrop
```

### 3. Check Your Balance

```bash
dirac-wallet balance
```

### 4. Send SOL to Someone

```bash
dirac-wallet send <recipient-address> <amount>
```

Example:
```bash
dirac-wallet send GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE 0.1
```

## Network Options

Dirac-Wallet supports three networks:
- `testnet` (default) - Real network, test tokens
- `devnet` - Development network
- `mainnet` - Production network (use with caution)

Specify network when creating or using wallet:
```bash
dirac-wallet create --network devnet
```

## Getting Help

```bash
dirac-wallet --help
dirac-wallet create --help
dirac-wallet send --help
```

## Security Notes

1. **Never share your wallet password**
2. **Always verify recipient addresses before sending**
3. **Start with test networks before using mainnet**
4. **Your wallet uses quantum-resistant cryptography by default**

## Troubleshooting

- **Connection errors**: Check your internet connection
- **Permission errors**: Ensure wallet directory is writable
- **Transaction errors**: Ensure sufficient balance and valid recipient address

For more detailed documentation, see [README.md](README.md).