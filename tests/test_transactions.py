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
from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.core.transactions import QuantumTransaction, TransactionInfo

class TestTransactions(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directory for test wallet
        self.test_dir = tempfile.mkdtemp()
        self.wallet_path = Path(self.test_dir) / "test_wallet.dwf"
        self.test_password = "test_password_123"
        
        # Create and unlock wallet
        self.wallet = DiracWallet(str(self.wallet_path))
        self.wallet.create(self.test_password)
        
        # Test recipient address
        self.recipient = "GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE"
        self.amount = 100_000_000
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_create_transaction(self):
        """Test creating a quantum transaction"""
        tx = QuantumTransaction(self.wallet)
        self.assertIsNotNone(tx)
        self.assertEqual(len(tx.instructions), 0)
    
    def test_create_transfer(self):
        """Test creating a transfer transaction"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        # Verify instruction was added
        self.assertEqual(len(tx.instructions), 1)
        
        # Verify fee payer is set
        self.assertEqual(str(tx.fee_payer), self.wallet.solana_address)
    
    def test_build_message(self):
        """Test building transaction message"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        message = tx.build_message()
        self.assertIsNotNone(message)
        
        # Verify message contains instruction
        self.assertGreater(len(message.instructions), 0)
    
    def test_sign_transaction(self):
        """Test signing transaction with quantum signature"""
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer(self.recipient, self.amount)
        
        # Create a valid blockhash
        blockhash = Hash.default()
        
        # Sign transaction
        tx_info = tx.sign_transaction(blockhash)
        
        # Verify transaction info
        self.assertIsInstance(tx_info, TransactionInfo)
        self.assertIsNotNone(tx_info.signature)
        self.assertIsNotNone(tx_info.raw_transaction)
        self.assertEqual(tx_info.status, "pending")
        self.assertEqual(tx_info.blockhash, str(blockhash))
        self.assertEqual(tx_info.amount, self.amount)
        self.assertEqual(tx_info.recipient, self.recipient)
    
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
        tampered_tx = raw_tx + b'0'
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

if __name__ == "__main__":
    unittest.main()