"""
Tests for the QuantumKeyring class.
"""

import os
import json
import pytest
from pathlib import Path

import sys
# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crypto.keyring import QuantumKeyring


class TestQuantumKeyring:
    """Test the QuantumKeyring class."""
    
    def test_init(self):
        """Test initialization with default parameters."""
        keyring = QuantumKeyring()
        assert keyring.signature_algorithm == "sphincs"
        assert keyring.hash_algorithm == "dirac_improved"
        assert keyring.security_level == 3
        assert keyring.backup_algorithms is True
    
    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        keyring = QuantumKeyring(
            signature_algorithm="dilithium",
            hash_algorithm="dirac_grover",
            security_level=5,
            backup_algorithms=False
        )
        assert keyring.signature_algorithm == "dilithium"
        assert keyring.hash_algorithm == "dirac_grover"
        assert keyring.security_level == 5
        assert keyring.backup_algorithms is False
    
    def test_init_with_invalid_signature_algorithm(self):
        """Test initialization with invalid signature algorithm."""
        with pytest.raises(ValueError, match="Unsupported signature algorithm"):
            QuantumKeyring(signature_algorithm="invalid_algo")
    
    def test_init_with_invalid_hash_algorithm(self):
        """Test initialization with invalid hash algorithm."""
        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            QuantumKeyring(hash_algorithm="invalid_algo")
    
    def test_generate_keypair(self):
        """Test generating a keypair."""
        keyring = QuantumKeyring(backup_algorithms=False)
        private_key, public_key = keyring.generate_keypair()
        
        # Check structure of keys
        assert "primary" in private_key
        assert "encryption" in private_key
        assert "primary" in public_key
        assert "encryption" in public_key
        
        # Check primary key
        assert private_key["primary"]["algorithm"] == "sphincs"
        assert "key" in private_key["primary"]
        assert private_key["primary"]["security_level"] == 3
        
        # Check encryption key
        assert private_key["encryption"]["algorithm"] == "kyber"
        assert "key" in private_key["encryption"]
        assert private_key["encryption"]["security_level"] == 3
    
    def test_generate_keypair_with_backups(self):
        """Test generating a keypair with backup keys."""
        keyring = QuantumKeyring(backup_algorithms=True)
        private_key, public_key = keyring.generate_keypair()
        
        # Check backup keys
        assert "backups" in private_key
        assert "backups" in public_key
        assert len(private_key["backups"]) == 2  # Should have 2 backup keys (all except primary)
        assert len(public_key["backups"]) == 2
    
    def test_derive_address(self):
        """Test deriving an address from a public key."""
        keyring = QuantumKeyring()
        _, public_key = keyring.generate_keypair()
        
        address = keyring.derive_address(public_key)
        
        # Check that we got a valid address
        assert isinstance(address, str)
        assert len(address) > 0
    
    def test_sign_and_verify_transaction(self):
        """Test signing and verifying a transaction."""
        keyring = QuantumKeyring()
        private_key, public_key = keyring.generate_keypair()
        
        # Create sample transaction data
        transaction_data = b"Sample transaction data"
        
        # Sign the transaction
        signature = keyring.sign_transaction(transaction_data, private_key)
        
        # Verify the signature
        is_valid = keyring.verify_transaction(transaction_data, signature, public_key)
        
        assert is_valid is True
    
    def test_encrypt_and_decrypt(self):
        """Test encrypting and decrypting data."""
        keyring = QuantumKeyring()
        private_key, public_key = keyring.generate_keypair()
        
        # Create sample data
        data = b"Sensitive data to encrypt"
        
        # Encrypt the data
        encrypted_data, ciphertext = keyring.encrypt(data, public_key)
        
        # Decrypt the data
        decrypted_data = keyring.decrypt(encrypted_data, ciphertext, private_key)
        
        assert decrypted_data == data 