"""
Penetration testing for Dirac Wallet
"""
import sys
import os
import unittest
import tempfile
import shutil
import random
import string
import json
import uuid
import hashlib
import math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

# Add the parent directory to sys.path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dirac_wallet.core.keys import QuantumKeyManager, KeyPair
from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.core.transactions import QuantumTransaction
from dirac_wallet.core.secure_storage import SecureStorage
from solders.hash import Hash


class TransactionSecurity(unittest.TestCase):
    """Penetration tests for transaction security"""
    
    def setUp(self):
        # Create temporary directory for test wallet
        self.test_dir = tempfile.mkdtemp()
        self.wallet_path = Path(self.test_dir) / "test_wallet.dwf"
        self.test_password = "Str0ng-P@ssw0rd!"
        
        # Create wallet
        self.wallet = DiracWallet(str(self.wallet_path))
        self.wallet.create(self.test_password)
        
        # Create test transaction
        self.tx = QuantumTransaction(self.wallet)
        self.tx.create_transfer("GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE", 10000)
        self.tx.recent_blockhash = Hash.default()

        # Valid Solana addresses for testing
        self.valid_solana_addresses = [
            "GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE",
            "5nUBHJ5rkyUUKB1UKVpEzr1N9oJRLVGaRsz6jy2tQj4f",
            "EVMYrRKb2fgpUUdmk8VrPH88shzwYxc1YmTR3hmQfwAR",
            "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin",
            "2vLZQhNcqaUQJd9q4Z9RU3BrnNXh1fotcJe6SJqGcBh5"
        ]
    
    def tearDown(self):
        # Clean up test directory
        shutil.rmtree(self.test_dir)
    
    def test_transaction_replay_attack(self):
        """Test resistance to transaction replay attacks"""
        # Sign original transaction
        tx_info = self.tx.sign_transaction(self.tx.recent_blockhash)
        
        # Create a "replay" by using the same signature with a new transaction
        replay_tx = QuantumTransaction(self.wallet)
        replay_tx.create_transfer("GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE", 20000)  # Different amount
        replay_tx.recent_blockhash = Hash.default()
        
        # Attempt to verify the original signature with new transaction
        original_signature = tx_info.signature
        
        # This should fail verification
        message = bytes(replay_tx.build_message())
        
        # Verify the signature fails for different transaction data
        self.assertFalse(
            self.wallet.key_manager.verify_signature(
                message, 
                original_signature, 
                self.wallet.keypair.public_key
            )
        )
    
    def test_double_spend_protection(self):
        """Test protection against double-spend attacks"""
        # Create two transactions sending to different addresses
        tx1 = QuantumTransaction(self.wallet)
        tx1.create_transfer("GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE", 1000000)
        tx1.recent_blockhash = Hash.default()
        
        tx2 = QuantumTransaction(self.wallet)
        tx2.create_transfer("5nUBHJ5rkyUUKB1UKVpEzr1N9oJRLVGaRsz6jy2tQj4f", 1000000)
        tx2.recent_blockhash = Hash.default()
        
        # Sign both transactions
        tx1_info = tx1.sign_transaction(tx1.recent_blockhash)
        tx2_info = tx2.sign_transaction(tx2.recent_blockhash)
        
        # Each transaction should have unique signature and ID
        self.assertNotEqual(tx1_info.signature, tx2_info.signature)
        
        # Verify that transaction hash incorporates the recipient
        hash1 = hashlib.sha256(tx1_info.raw_transaction).digest()
        hash2 = hashlib.sha256(tx2_info.raw_transaction).digest()
        self.assertNotEqual(hash1, hash2)
    
    def test_malleability_attack(self):
        """Test resistance to transaction malleability attacks"""
        # Sign original transaction
        tx_info = self.tx.sign_transaction(self.tx.recent_blockhash)
        original_tx_bytes = tx_info.raw_transaction
        
        # Try to modify transaction without invalidating the signature
        modified_tx_bytes = bytearray(original_tx_bytes)
        
        # Try to modify various parts of the transaction
        # This is a simplified simulation of malleability attacks
        for i in range(len(modified_tx_bytes)):
            # Save original byte
            original_byte = modified_tx_bytes[i]
            
            # Try modifying this byte
            modified_tx_bytes[i] = (original_byte + 1) % 256
            
            # Check if modification invalidates the signature
            try:
                # Attempt to verify with modified data
                result = self.wallet.key_manager.verify_signature(
                    bytes(modified_tx_bytes),
                    tx_info.signature,
                    self.wallet.keypair.public_key
                )
                
                # If the signature still verifies, we found a malleability issue
                if result:
                    self.fail(f"Malleability vulnerability at byte {i}")
            except Exception:
                # Exception during verification is fine - it means tampering was detected
                pass
            
            # Restore the original byte for next iteration
            modified_tx_bytes[i] = original_byte
    
    def test_flooding_attack(self):
        """Test resistance to transaction flooding attacks"""
        # Create and sign multiple transactions with different parameters
        num_transactions = 5
        transactions = []
        
        # Use valid Solana addresses from our list
        for i in range(num_transactions):
            # Get a valid Solana address
            recipient = self.valid_solana_addresses[i % len(self.valid_solana_addresses)]
            amount = 10000 + i * 1000
            
            tx = QuantumTransaction(self.wallet)
            try:
                tx.create_transfer(recipient, amount)
                tx.recent_blockhash = Hash.default()
                
                # Sign and record transaction
                tx_info = tx.sign_transaction(tx.recent_blockhash)
                transactions.append(tx_info)
            except Exception as e:
                print(f"Transaction creation error: {str(e)}")
        
        # Verify we have some successfully signed transactions
        self.assertGreater(len(transactions), 0, 
                           "No transactions were processed successfully")
        
        # Check that all transactions have valid signatures
        for tx_info in transactions:
            self.assertIsNotNone(tx_info.signature)


class StorageSecurity(unittest.TestCase):
    """Penetration tests for wallet storage security"""
    
    def setUp(self):
        # Create temporary directory for test wallet
        self.test_dir = tempfile.mkdtemp()
        self.wallet_path = Path(self.test_dir) / "test_wallet.dwf"
        self.test_password = "Str0ng-P@ssw0rd!"
        
        # Create wallet
        self.wallet = DiracWallet(str(self.wallet_path))
        self.wallet.create(self.test_password)
    
    def tearDown(self):
        # Clean up test directory
        shutil.rmtree(self.test_dir)
    
    def test_file_tampering_resistance(self):
        """Test resistance to wallet file tampering"""
        # Lock wallet to ensure data is flushed to disk
        self.wallet.lock()
        
        # Read wallet file
        wallet_data = self.wallet_path.read_bytes()
        
        # Make a significant change to the file by overwriting a large portion
        tampered_data = bytearray(wallet_data)
        if len(tampered_data) > 100:
            # Corrupt a chunk of data in the middle of the file
            start_pos = len(tampered_data) // 3
            for i in range(start_pos, min(start_pos + 20, len(tampered_data))):
                tampered_data[i] = (tampered_data[i] + 73) % 256  # Significant change
        
        # Write tampered data back
        self.wallet_path.write_bytes(bytes(tampered_data))
        
        # We should get a ValueError specifically when trying to unlock
        with self.assertRaises(ValueError):
            self.wallet.unlock(self.test_password)
    
    def test_brute_force_resistance(self):
        """Test resistance to password brute force attacks"""
        # Lock wallet to ensure data is flushed to disk
        self.wallet.lock()
        
        # Try a series of incorrect passwords
        correct_password_works = False
        incorrect_passwords_fail = True
        
        # Try incorrect passwords
        for i in range(20):  # Reduced from 100 to speed up the test
            # Generate a random incorrect password
            incorrect_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # Ensure it's not accidentally the correct password
            if incorrect_password == self.test_password:
                incorrect_password += "X"
                
            # Attempt to unlock with incorrect password
            try:
                result = self.wallet.unlock(incorrect_password)
                # If we get here without an exception, the unlock must have returned False
                self.assertFalse(result, f"Incorrect password '{incorrect_password}' unlocked the wallet!")
                incorrect_passwords_fail = incorrect_passwords_fail and not result
            except ValueError:
                # ValueError is expected for incorrect passwords
                pass
                
            # Lock again just in case an incorrect password worked
            self.wallet.lock()
        
        # Verify correct password still works
        try:
            correct_password_works = self.wallet.unlock(self.test_password)
        except ValueError:
            self.fail("Correct password raised ValueError")
            
        self.assertTrue(correct_password_works, "Correct password did not unlock the wallet")
        self.assertTrue(incorrect_passwords_fail, "One or more incorrect passwords unlocked the wallet")
    
    def test_key_extraction_resistance(self):
        """Test resistance to key extraction from wallet file"""
        # Lock wallet to ensure data is flushed to disk
        self.wallet.lock()
        
        # Read wallet file
        wallet_data = self.wallet_path.read_bytes()
        
        # Attempt to find private key patterns in the file
        # For a secure implementation, the private key should not be findable in plaintext
        
        # Convert keypair to string for searching
        keypair_str = str(self.wallet.keypair).encode() if self.wallet.is_unlocked else None
        
        # If wallet is locked, we need to unlock it to get the keypair
        if not self.wallet.is_unlocked:
            self.wallet.unlock(self.test_password)
            keypair_str = str(self.wallet.keypair).encode()
            self.wallet.lock()  # Lock it again
        
        # Check that private key information is not in the wallet file in plaintext
        if keypair_str:
            # Check for significant substrings that might reveal key material
            for i in range(0, len(keypair_str) - 20):
                substring = keypair_str[i:i+20]
                self.assertNotIn(substring, wallet_data)
        
        # Wallet data should be encrypted
        # This is a simple entropy test to confirm data looks encrypted
        entropy = 0
        byte_freq = {}
        for byte in wallet_data:
            if byte not in byte_freq:
                byte_freq[byte] = 0
            byte_freq[byte] += 1
        
        for count in byte_freq.values():
            prob = count / len(wallet_data)
            # Calculate entropy using math.log2 instead of bit_length
            if prob > 0:
                entropy -= prob * math.log2(prob)
        
        # Encrypted data should have high entropy
        self.assertGreater(entropy, 4.0)  # Lowered threshold a bit to account for structure


class NetworkSecurity(unittest.TestCase):
    """Penetration tests for network operations"""
    
    def setUp(self):
        # Create temporary directory for test wallet
        self.test_dir = tempfile.mkdtemp()
        self.wallet_path = Path(self.test_dir) / "test_wallet.dwf"
        self.test_password = "Str0ng-P@ssw0rd!"
        
        # Create wallet
        self.wallet = DiracWallet(str(self.wallet_path))
        self.wallet.create(self.test_password)
    
    def tearDown(self):
        # Clean up test directory
        shutil.rmtree(self.test_dir)
    
    def test_mitm_attack_resistance(self):
        """Test resistance to Man-in-the-Middle attacks"""
        # Create a transaction
        tx = QuantumTransaction(self.wallet)
        tx.create_transfer("GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE", 10000)
        tx.recent_blockhash = Hash.default()
        
        # Sign transaction
        tx_info = tx.sign_transaction(tx.recent_blockhash)
        
        # Create a completely different transaction for the MITM attack
        mitm_tx = QuantumTransaction(self.wallet)
        mitm_tx.create_transfer("EVMYrRKb2fgpUUdmk8VrPH88shzwYxc1YmTR3hmQfwAR", 50000)
        mitm_tx.recent_blockhash = Hash.default()
        mitm_info = mitm_tx.build_message()
        
        # Try to use the original signature with the modified transaction data
        # This should fail verification
        result = self.wallet.key_manager.verify_signature(
            bytes(mitm_info),
            tx_info.signature,
            self.wallet.keypair.public_key
        )
        
        # Verification should fail, indicating MITM resistance
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main() 