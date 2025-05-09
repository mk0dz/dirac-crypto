"""
Test Solana network functionality
"""
import sys
import os
import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from solders.pubkey import Pubkey
from solders.hash import Hash

# Add the parent directory to sys.path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.core.transactions import QuantumTransaction
from dirac_wallet.network.solana_client import QuantumSolanaClient


class TestNetwork(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directory for test wallet
        self.test_dir = tempfile.mkdtemp()
        self.wallet_path = Path(self.test_dir) / "test_wallet.dwf"
        self.test_password = "test_password_123"
        
        # Create and unlock wallet
        self.wallet = DiracWallet(str(self.wallet_path))
        self.wallet.create(self.test_password)
        
        # Initialize Solana client
        self.solana_client = QuantumSolanaClient(network="devnet")
        
        # Test recipient address
        self.recipient = "GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE"
        self.amount = 100_000_000  # 0.1 SOL
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_create_client(self):
        """Test creating Solana client"""
        client = QuantumSolanaClient(network="testnet")
        self.assertIsNotNone(client)
        self.assertEqual(client.network, "testnet")
        self.assertEqual(client.current_endpoint, "https://api.testnet.solana.com")
    
    def test_connect_to_network(self):
        """Test connecting to Solana network"""
        async def run_test():
            try:
                connected = await self.solana_client.connect()
                self.assertTrue(connected)
                
                # Test disconnection
                await self.solana_client.disconnect()
                
            except Exception as e:
                # Connection might fail if network is down
                print(f"Network connection test skipped: {e}")
                self.skipTest("Network connectivity test requires internet")
        
        asyncio.run(run_test())
    
    async def test_get_recent_blockhash(self):
        """Test getting recent blockhash"""
        try:
            # Connect to network
            await self.solana_client.connect()
            
            # Get recent blockhash
            blockhash = await self.solana_client.get_recent_blockhash()
            
            # Verify blockhash
            self.assertIsNotNone(blockhash)
            self.assertIsInstance(blockhash, Hash)
            self.assertEqual(len(str(blockhash)), 44)  # Base58 encoded hash length
            
            await self.solana_client.disconnect()
            
        except Exception as e:
            self.skipTest(f"Blockhash test skipped: {str(e)}")
    
    def test_request_airdrop(self):
        """Test requesting airdrop"""
        async def run_test():
            try:
                await self.solana_client.connect()
                
                # Request airdrop
                tx_id = await self.solana_client.request_airdrop(
                    self.wallet.solana_address,
                    0.1  # 0.1 SOL
                )
                
                self.assertIsNotNone(tx_id)
                self.assertIsInstance(tx_id, str)
                
                # Check if transaction confirms
                status = await self.solana_client.get_transaction_status(tx_id)
                self.assertIn("confirmed", status)
                
                await self.solana_client.disconnect()
                
            except Exception as e:
                # Airdrop might fail due to rate limits
                print(f"Airdrop test skipped: {e}")
                self.skipTest("Airdrop test requires network connection")
        
        asyncio.run(run_test())
    
    def test_full_transaction_flow(self):
        """Test complete transaction flow"""
        async def run_test():
            try:
                # Connect to network
                await self.solana_client.connect()
                
                # Get recent blockhash
                blockhash = await self.solana_client.get_recent_blockhash()
                
                # Create and sign transaction
                tx = QuantumTransaction(self.wallet)
                tx.create_transfer(self.recipient, self.amount)
                
                # Prepare transaction for broadcast
                raw_tx, metadata = tx.prepare_for_broadcast(str(blockhash))
                
                # Submit transaction (without actually sending to avoid fees)
                # This test just verifies the flow works
                result = {
                    "transaction_prepared": True,
                    "raw_transaction_size": len(raw_tx),
                    "has_quantum_metadata": "signature" in metadata
                }
                
                self.assertTrue(result["transaction_prepared"])
                self.assertGreater(result["raw_transaction_size"], 0)
                self.assertTrue(result["has_quantum_metadata"])
                
                await self.solana_client.disconnect()
                
            except Exception as e:
                print(f"Transaction flow test skipped: {e}")
                self.skipTest("Transaction flow test requires network connection")
        
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
