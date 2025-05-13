# Dirac-Wallet CLI Usage Examples

## Creating a Wallet

```bash
# Create a wallet on testnet
dirac-wallet create 'name'

# Create a wallet on devnet
dirac-wallet create --network devnet

# Create a wallet with a specific name
dirac-wallet create my_wallet
```

## Checking Balance

```bash
# Check balance of default wallet
dirac-wallet balance

# Check balance on specific network
dirac-wallet balance --network devnet

# Check specific wallet balance
dirac-wallet balance my_wallet
```

## Sending Transactions

```bash
# Send 0.1 SOL to an address
dirac-wallet send GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE 0.1

# Send from specific wallet
dirac-wallet send --network devnet my_wallet RecipientAddress 0.5
```

## Requesting Airdrop (devnet/testnet only)

```bash
# Request 1 SOL airdrop
dirac-wallet airdrop

# Request specific amount
dirac-wallet airdrop default 2.0
```

## Wallet Management

```bash
# Show wallet information
dirac-wallet info

# List all wallets
dirac-wallet list-wallets

# Show help
dirac-wallet --help
```

## Complete Workflow Example

1. Create wallet:
```bash
dirac-wallet create --network devnet my_devnet_wallet
```

2. Request airdrop:
```bash
dirac-wallet airdrop my_devnet_wallet 1.0
```

3. Check balance:
```bash
dirac-wallet balance my_devnet_wallet
```

4. Send transaction:
```bash
dirac-wallet send my_devnet_wallet GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE 0.1
```

5. Check transaction history:
```bash
dirac-wallet info my_devnet_wallet
```