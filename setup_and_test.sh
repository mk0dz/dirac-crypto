#!/bin/bash

# Exit on any error
set -e

echo "===== Setting up Dirac Quantum-Resistant Wallet ====="

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Check if quantum_hash is available
if python -c "import quantum_hash" 2>/dev/null; then
    echo "quantum_hash package is installed correctly."
else
    echo "Error: quantum_hash package is missing."
    echo "Installing from PyPI..."
    pip install quantum_hash>=0.5.0
fi

echo ""
echo "===== Testing wallet functionality ====="

# Create a test wallet
echo "Creating a test wallet with quantum algorithms..."
python -m dirac create test-wallet --sig-algo sphincs --hash-algo grover --security 3 --force

# Check balance
echo ""
echo "Checking wallet balance..."
python -m dirac balance test-wallet

# Try airdrop
echo ""
echo "Testing airdrop functionality..."
python -m dirac airdrop test-wallet --amount 1.0

# Check balance again
echo ""
echo "Checking updated balance..."
python -m dirac balance test-wallet

echo ""
echo "Setup and testing complete!" 