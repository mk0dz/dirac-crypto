# Dirac-Wallet Project Structure

```
dirac-wallet/
├── .gitignore
├── README.md
├── requirements.txt
├── setup.py
├── config/
│   └── config.yaml
├── dirac_wallet/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── wallet.py
│   │   ├── keys.py
│   │   ├── transactions.py
│   │   └── storage.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── commands.py
│   ├── network/
│   │   ├── __init__.py
│   │   └── solana_client.py
│   └── utils/
│       ├── __init__.py
│       ├── crypto.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   ├── test_keys.py
│   ├── test_transactions.py
│   └── test_wallet.py
└── examples/
    └── usage_example.py
```