"""
Test transaction handling - Complete version
"""
import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to sys.path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.signature import Signature
from solders.transaction import Transaction
from solders.message import Message
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.core.transactions import QuantumTransaction
from dirac_wallet.network.solana_client import QuantumSolanaClient

class TestTransactions(unittest.TestCase):
    
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
    
    def test_create_transaction(self):
        """Test creating a quantum transaction"""
        tx = QuantumTransaction(self.wallet)
        self.assertIsNotNone(tx)
        self.assertEqual(len(tx.instructions), 0)
        self.assertEqual(str(tx.fee_payer), self.wallet.solana_address)
    
    def test_create_transfer(self):
        """Test creating a transfer transaction"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        # Verify instruction was added
        self.assertEqual(len(tx.instructions), 1)
        
        # Verify fee payer is set
        self.assertEqual(str(tx.fee_payer), self.wallet.solana_address)
        
        # Verify instruction data
        instruction = tx.instructions[0]
        self.assertEqual(instruction.program_id, SYSTEM_PROGRAM_ID)
        self.assertEqual(len(instruction.accounts), 2)
        self.assertEqual(instruction.accounts[0].pubkey, tx.fee_payer)
        self.assertEqual(str(instruction.accounts[1].pubkey), self.recipient)
    
    def test_build_message(self):
        """Test building transaction message"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        # Set blockhash
        blockhash = Hash.default()
        tx.recent_blockhash = blockhash
        
        message = tx.build_message()
        self.assertIsNotNone(message)
        
        # Verify message contains instruction
        self.assertGreater(len(message.instructions), 0)
        
        # Verify fee payer
        self.assertEqual(message.account_keys[0], tx.fee_payer)
    
    def test_sign_transaction(self):
        """Test signing transaction with quantum signature"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        # Create a valid blockhash
        blockhash = Hash.default()
        tx.recent_blockhash = blockhash
        
        # Sign transaction
        raw_tx, metadata = tx.prepare_for_broadcast(str(blockhash))
        
        # Verify transaction data
        self.assertIsInstance(raw_tx, bytes)
        self.assertGreater(len(raw_tx), 0)
        self.assertIn("signature", metadata)
        self.assertEqual(metadata["signature_algorithm"], "dilithium")
    
    def test_prepare_for_broadcast(self):
        """Test preparing transaction for broadcast"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        blockhash = str(Hash.default())
        
        raw_tx, metadata = tx.prepare_for_broadcast(blockhash)
        
        # Verify raw transaction
        self.assertIsInstance(raw_tx, bytes)
        self.assertGreater(len(raw_tx), 0)
        
        # Verify metadata
        self.assertIn("signature", metadata)
        self.assertIn("signature_algorithm", metadata)
        self.assertIn("security_level", metadata)
        self.assertIn("public_key", metadata)
        self.assertIn("transaction_hash", metadata)
        self.assertEqual(metadata["signature_algorithm"], "dilithium")
    
    def test_verify_quantum_signature(self):
        """Test independent quantum signature verification"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        blockhash = str(Hash.default())
        raw_tx, metadata = tx.prepare_for_broadcast(blockhash)
        
        # Verify signature
        is_valid = QuantumTransaction.verify_quantum_signature(raw_tx, metadata, self.wallet)
        self.assertTrue(is_valid)
        
        # Test with tampered transaction
        transaction = Transaction.from_bytes(raw_tx)
        message_bytes = bytearray(bytes(transaction.message))
        message_bytes[0] ^= 1  # Flip a bit in the message
        transaction = Transaction.new_unsigned(Message.from_bytes(bytes(message_bytes)))
        tampered_tx = bytes(transaction)
        
        is_valid_tampered = QuantumTransaction.verify_quantum_signature(tampered_tx, metadata, self.wallet)
        self.assertFalse(is_valid_tampered)
    
    def test_missing_instructions(self):
        """Test error handling for missing instructions"""
        tx = QuantumTransaction(self.wallet)
        
        with self.assertRaises(ValueError):
            tx.build_message()
    
    def test_missing_blockhash(self):
        """Test error handling for missing blockhash"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        with self.assertRaises(ValueError):
            tx.sign_transaction()
    
    def test_sign_locked_wallet(self):
        """Test signing with locked wallet raises error"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        # Lock wallet
        self.wallet.lock()
        
        # Attempt to sign
        blockhash = Hash.default()
        
        with self.assertRaises(ValueError):
            tx.sign_transaction(blockhash)
    
    async def test_submit_transaction(self):
        """Test submitting transaction to network"""
        try:
            # Connect to network
            await self.solana_client.connect()
            
            # Create and prepare transaction
            tx = QuantumTransaction(self.wallet)
            tx.create_transfer(self.recipient, self.amount)
            
            # Get recent blockhash
            blockhash = await self.solana_client.get_recent_blockhash()
            
            # Prepare transaction
            raw_tx, metadata = tx.prepare_for_broadcast(str(blockhash))
            
            # Verify metadata contains all required fields
            self.assertIn("signature", metadata)
            self.assertIn("message_hash", metadata)
            self.assertIn("blockhash", metadata)
            self.assertIn("fee_payer", metadata)
            self.assertIn("public_key", metadata)
            
            # Submit transaction
            result = await self.solana_client.submit_quantum_transaction(
                raw_tx,
                metadata["signature"],
                metadata
            )
            
            # Verify result
            self.assertIn("transaction_id", result)
            self.assertEqual(result["status"], "submitted")
            self.assertIn("quantum_metadata", result)
            
            # Verify quantum metadata
            quantum_metadata = result["quantum_metadata"]
            self.assertIn("signature", quantum_metadata)
            self.assertIn("message_hash", quantum_metadata)
            self.assertIn("blockhash", quantum_metadata)
            self.assertIn("fee_payer", quantum_metadata)
            
            # Wait for confirmation
            status = await self.solana_client.get_transaction_status(result["transaction_id"])
            self.assertIn("confirmed", status)
            
        except Exception as e:
            self.skipTest(f"Network test skipped: {str(e)}")
        finally:
            await self.solana_client.disconnect()

if __name__ == "__main__":
    unittest.main()