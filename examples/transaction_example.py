#!/usr/bin/env python3
"""
Demonstrate quantum-resistant transaction signing
"""
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.core.transactions import QuantumTransaction
from dirac_wallet.utils.logger import logger
from decimal import Decimal


def display_transaction_info(tx_info):
    """Display transaction information"""
    print("\n=== Transaction Information ===")
    print(f"Status: {tx_info.status}")
    print(f"Amount: {tx_info.amount} lamports ({Decimal(tx_info.amount) / 10**9:.6f} SOL)")
    print(f"Recipient: {tx_info.recipient}")
    print(f"Blockhash: {tx_info.blockhash}")
    
    # Signature information
    print("\n=== Quantum Signature Information ===")
    print(f"Algorithm: dilithium")
    print(f"Signature Type: {type(tx_info.signature)}")
    print(f"Raw Transaction Size: {len(tx_info.raw_transaction)} bytes")


def demonstrate_transaction_signing():
    """Demonstrate the complete transaction process"""
    
    print("=== Dirac-Wallet Transaction Demo ===\n")
    
    # Setup
    wallet_path = Path.home() / ".dirac_wallet" / "demo_wallet.dwf"
    recipient_address = "GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE"  # Example address
    amount_sol = Decimal("0.1")  # 0.1 SOL
    amount_lamports = int(amount_sol * 10**9)  # Convert to lamports
    
    # Create or load wallet
    print("1. Setting up wallet...")
    wallet = DiracWallet(str(wallet_path))
    
    # Check if wallet exists
    if wallet_path.exists():
        password = "demo_password_123"  # In real app, use getpass
        wallet.unlock(password)
        print(f"✓ Wallet unlocked: {wallet.solana_address}\n")
    else:
        password = "demo_password_123"
        result = wallet.create(password)
        print(f"✓ New wallet created: {result['address']}\n")
    
    # Create transaction
    print("2. Creating transfer transaction...")
    tx = QuantumTransaction(wallet)
    tx.create_transfer(recipient_address, amount_lamports)
    print(f"✓ Transfer created: {amount_sol} SOL to {recipient_address[:8]}...\n")
    
    # Mock blockhash (in real app, get from RPC)
    mock_blockhash = "7ZQ2mKUBkEwtw9hZiZEzFZDJb9Y4VLXTRoHRKHv8CKQ"
    
    # Sign transaction
    print("3. Signing transaction with quantum signature...")
    tx_info = tx.sign_transaction(mock_blockhash)
    print("✓ Transaction signed successfully\n")
    
    # Display transaction details
    display_transaction_info(tx_info)
    
    # Prepare for broadcast
    print("\n4. Preparing for broadcast...")
    raw_tx, metadata = tx.prepare_for_broadcast(mock_blockhash)
    print(f"✓ Transaction ready for broadcast")
    print(f"  Raw transaction size: {len(raw_tx)} bytes")
    print(f"  Metadata fields: {list(metadata.keys())}")
    
    # Verify quantum signature independently
    print("\n5. Verifying quantum signature...")
    is_valid = QuantumTransaction.verify_quantum_signature(raw_tx, metadata, wallet)
    print(f"✓ Signature verification: {'VALID' if is_valid else 'INVALID'}")
    
    print("\n=== Demo Complete ===")
    print("Note: This is a demo transaction. To actually send on Solana,")
    print("integrate with a Solana client to broadcast the raw transaction.")


if __name__ == "__main__":
    demonstrate_transaction_signing()