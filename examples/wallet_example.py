#!/usr/bin/env python3
"""
Demonstrate basic wallet operations
"""
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.utils.logger import logger


def demo_wallet_lifecycle():
    """Demonstrate complete wallet lifecycle"""
    
    # Create a test wallet path
    wallet_path = Path.home() / ".dirac_wallet" / "demo_wallet.dwf"
    
    print("=== Dirac-Wallet Basic Operations Demo ===\n")
    
    # Step 1: Create new wallet
    print("1. Creating new quantum-resistant wallet...")
    wallet = DiracWallet(str(wallet_path))
    
    # Create with password (in real use, this would be from getpass)
    password = "demo_password_123"
    result = wallet.create(password)
    
    print(f"   ✓ Wallet created")
    print(f"   Address: {result['address']}")
    print(f"   Network: {result['network']}")
    print(f"   Path: {result['path']}\n")
    
    # Step 2: Get wallet information
    print("2. Getting wallet information...")
    info = wallet.get_info()
    print(f"   Algorithm: {info['algorithm']}")
    print(f"   Security Level: {info['security_level']}")
    print(f"   Created: {info['created_at']}")
    print(f"   Locked: {not info['is_unlocked']}\n")
    
    # Step 3: Sign a message
    print("3. Signing a message...")
    message = "Hello from Dirac-Wallet!"
    signature = wallet.sign_message(message)
    print(f"   ✓ Message signed (signature size: {len(str(signature))} bytes)")
    
    # Verify signature
    is_valid = wallet.verify_signature(message, signature)
    print(f"   ✓ Signature valid: {is_valid}\n")
    
    # Step 4: Lock wallet
    print("4. Locking wallet...")
    wallet.lock()
    print("   ✓ Wallet locked\n")
    
    # Step 5: Unlock wallet
    print("5. Unlocking wallet...")
    unlock_success = wallet.unlock(password)
    print(f"   ✓ Wallet unlocked: {unlock_success}")
    
    if unlock_success:
        # Test signing again
        new_signature = wallet.sign_message("Test after unlock")
        print("   ✓ Can sign messages again\n")
    
    # Step 6: Create wallet on different network
    print("6. Creating devnet wallet...")
    devnet_path = Path.home() / ".dirac_wallet" / "demo_devnet.dwf"
    devnet_wallet = DiracWallet(str(devnet_path), network="devnet")
    devnet_result = devnet_wallet.create(password)
    print(f"   ✓ Devnet wallet created")
    print(f"   Address: {devnet_result['address']}\n")
    
    print("Demo completed successfully!")


if __name__ == "__main__":
    demo_wallet_lifecycle()