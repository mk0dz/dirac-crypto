"""
Test wallet functionality
"""
import asyncio
from pathlib import Path
import sys
import time

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.core.transactions import QuantumTransaction
from dirac_wallet.network.solana_client import QuantumSolanaClient

async def main():
    try:
        # Create and unlock wallet
        wallet = DiracWallet("test_wallet.dwf", network="devnet")
        wallet.create("test123")
        print(f"\nCreated wallet with address: {wallet.solana_address}")
        
        # Initialize Solana client
        client = QuantumSolanaClient(network="devnet")
        connected = await client.connect()
        if not connected:
            print("Failed to connect to Solana network")
            return
        print("Connected to Solana devnet")
        
        # Request airdrop
        print("\nRequesting airdrop...")
        try:
            airdrop_amount = 1.0  # 1 SOL
            tx_id = await client.request_airdrop(wallet.solana_address, airdrop_amount)
            if tx_id:
                print(f"Airdrop requested: {tx_id}")
                # Wait for airdrop to confirm
                print("Waiting for airdrop confirmation...")
                await asyncio.sleep(5)
                
                # Check balance
                balance = await client.get_balance(wallet.solana_address)
                print(f"Current balance: {balance} SOL")
                
                if balance > 0:
                    print("\nAirdrop successful!")
                else:
                    print("\nAirdrop may have failed. Please try alternative methods.")
            else:
                print("\nAirdrop request failed. Here are alternative methods to get SOL:")
                alternatives = await client.get_airdrop_alternatives(wallet.solana_address)
                
                if "web_faucets" in alternatives:
                    print("\nWeb Faucets:")
                    for faucet in alternatives["web_faucets"]:
                        print(f"  - {faucet}")
                
                if "cli_commands" in alternatives:
                    print("\nCLI Commands:")
                    for cmd in alternatives["cli_commands"]:
                        print(f"  - {cmd}")
                
                if "discord_faucets" in alternatives:
                    print("\nDiscord Faucets:")
                    for discord in alternatives["discord_faucets"]:
                        print(f"  - {discord}")
                
                if "note" in alternatives:
                    print(f"\nNote: {alternatives['note']}")
                
                print("\nPlease fund your wallet using one of these methods and run this script again.")
                return
                
        except Exception as e:
            print(f"\nAirdrop error: {str(e)}")
            print("\nPlease try funding your wallet manually and run this script again.")
            return
        
        # Check balance
        balance = await client.get_balance(wallet.solana_address)
        print(f"\nCurrent balance: {balance} SOL")
        
        if balance == 0:
            print("No balance available. Please fund the wallet using one of the alternative methods.")
            return
        
        # Create and send transaction
        recipient = "GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE"
        amount = 0.1  # 0.1 SOL
        amount_lamports = int(amount * 10**9)
        
        print(f"\nSending {amount} SOL to {recipient}")
        
        tx = QuantumTransaction(wallet)
        tx.create_transfer(recipient, amount_lamports)
        
        # Get recent blockhash
        blockhash = await client.get_recent_blockhash()
        if not blockhash:
            print("Failed to get recent blockhash")
            return
        
        # Prepare and send transaction
        try:
            raw_tx, metadata = tx.prepare_for_broadcast(str(blockhash))
            result = await client.submit_quantum_transaction(
                raw_tx,
                metadata["signature"],
                metadata
            )
            
            print(f"Transaction sent: {result['transaction_id']}")
            
            # Wait for confirmation
            print("Waiting for confirmation...")
            confirmed = False
            for _ in range(5):  # Try for 5 attempts
                status = await client.get_transaction_status(result["transaction_id"])
                if status.get("confirmed"):
                    print("Transaction confirmed!")
                    confirmed = True
                    break
                elif status.get("error"):
                    print(f"Transaction failed: {status['error']}")
                    break
                await asyncio.sleep(2)
            
            if not confirmed:
                print("Transaction confirmation timed out")
            
            # Check final balance
            balance = await client.get_balance(wallet.solana_address)
            print(f"Final balance: {balance} SOL")
            
        except Exception as e:
            print(f"Transaction error: {str(e)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 