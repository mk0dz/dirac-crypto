#!/usr/bin/env python3
"""
Demonstrate network connectivity and transaction submission
"""
import sys
import os
import asyncio
from pathlib import Path
from decimal import Decimal

# Add the parent directory to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.core.transactions import QuantumTransaction
from dirac_wallet.network.solana_client import QuantumSolanaClient
from dirac_wallet.utils.logger import logger


async def demonstrate_network_operations():
    """Demonstrate complete network operations"""
    
    print("=== Dirac-Wallet Network Operations Demo ===\n")
    
    # Setup wallet
    wallet_path = Path.home() / ".dirac_wallet" / "demo_wallet.dwf"
    print("1. Setting up wallet...")
    
    wallet = DiracWallet(str(wallet_path))
    
    # Check if wallet exists or create new one
    if wallet_path.exists():
        password = "demo_password_123"
        wallet.unlock(password)
        print(f"✓ Wallet unlocked: {wallet.solana_address}\n")
    else:
        password = "demo_password_123"
        result = wallet.create(password)
        print(f"✓ New wallet created: {result['address']}\n")
    
    # Initialize Solana client
    print("2. Connecting to Solana devnet...")
    client = QuantumSolanaClient(network="devnet")
    
    try:
        connected = await client.connect()
        print(f"✓ Connected to Solana devnet: {connected}\n")
        
        # Get wallet balance
        print("3. Checking wallet balance...")
        try:
            balance = await client.get_balance(wallet.solana_address)
            print(f"✓ Current balance: {balance} SOL\n")
            
            # Request airdrop if balance is low
            if balance < 0.1:
                print("4. Requesting airdrop...")
                airdrop_tx = await client.request_airdrop(wallet.solana_address, 0.5)
                print(f"✓ Airdrop requested: {airdrop_tx}")
                
                # Wait for airdrop confirmation
                print("   Waiting for airdrop confirmation...")
                status = await client.get_transaction_status(airdrop_tx)
                if status.get("confirmed"):
                    print("   ✓ Airdrop confirmed!\n")
                else:
                    print(f"   ⚠ Airdrop status: {status}\n")
                    
        except Exception as e:
            print(f"   ⚠ Balance check failed: {e}\n")
        
        # Prepare transaction
        print("5. Preparing transfer transaction...")
        recipient = "GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE"
        amount_sol = 0.01  # 0.01 SOL
        amount_lamports = int(amount_sol * 10**9)
        
        # Create transaction
        tx = QuantumTransaction(wallet)
        tx.create_transfer(recipient, amount_lamports)
        
        # Get recent blockhash
        blockhash = await client.get_recent_blockhash()
        print(f"✓ Got recent blockhash: {blockhash}\n")
        
        # Sign transaction
        print("6. Signing transaction with quantum signature...")
        raw_tx, metadata = tx.prepare_for_broadcast(str(blockhash))
        print(f"✓ Transaction signed (size: {len(raw_tx)} bytes)\n")
        
        # Submit transaction (uncomment to actually send)
        print("7. Transaction ready for submission")
        print("   (Transaction not actually submitted in demo mode)")
        print(f"   Raw transaction size: {len(raw_tx)} bytes")
        print(f"   Quantum signature algorithm: {metadata.get('signature_algorithm')}")
        print(f"   Security level: {metadata.get('security_level')}")
        
        # Uncomment the following to actually submit the transaction:
        # result = await client.submit_quantum_transaction(raw_tx, metadata["signature"], metadata)
        # print(f"   Transaction submitted: {result['transaction_id']}")
        # print(f"   Status: {result['status']}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect
        print("\n8. Disconnecting from network...")
        await client.disconnect()
        print("✓ Disconnected\n")
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_network_operations())
