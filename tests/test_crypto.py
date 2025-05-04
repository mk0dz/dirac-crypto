"""
Tests for the cryptographic components.
"""

import pytest
import os
import base64
import hashlib

from dirac.crypto import QuantumKeyring

def test_keyring_initialization():
    """Test that QuantumKeyring initializes with default values."""
    keyring = QuantumKeyring()
    assert keyring.signature_algorithm == "sphincs"
    assert keyring.hash_algorithm == "sha256"
    assert keyring.security_level == 3

def test_keyring_custom_params():
    """Test that QuantumKeyring initializes with custom parameters."""
    keyring = QuantumKeyring(
        signature_algorithm="dilithium",
        hash_algorithm="sha512", 
        security_level=5
    )
    assert keyring.signature_algorithm == "dilithium"
    assert keyring.hash_algorithm == "sha512"
    assert keyring.security_level == 5

def test_keypair_generation():
    """Test keypair generation."""
    keyring = QuantumKeyring()
    private_key, public_key = keyring.generate_keypair()
    
    # Check structure
    assert "algorithm" in private_key
    assert "seed" in private_key
    assert "security_level" in private_key
    
    assert "algorithm" in public_key
    assert "key" in public_key
    assert "security_level" in public_key
    
    # Check values
    assert private_key["algorithm"] == keyring.signature_algorithm
    assert private_key["security_level"] == keyring.security_level
    assert isinstance(private_key["seed"], bytes)
    assert len(private_key["seed"]) == 32
    
    assert public_key["algorithm"] == keyring.signature_algorithm
    assert public_key["security_level"] == keyring.security_level
    assert isinstance(public_key["key"], bytes)
    assert len(public_key["key"]) == 32

def test_address_derivation():
    """Test address derivation from public key."""
    keyring = QuantumKeyring()
    _, public_key = keyring.generate_keypair()
    
    address = keyring.derive_address(public_key)
    
    # Check that address is a base64 string
    assert isinstance(address, str)
    
    # Should be decodable as base64
    decoded = base64.b64decode(address)
    assert len(decoded) == 32  # SHA-256 hash produces 32 bytes

def test_transaction_signing():
    """Test transaction signing."""
    keyring = QuantumKeyring()
    private_key, public_key = keyring.generate_keypair()
    
    # Create a test message
    message = b"Test transaction data"
    
    # Sign the message
    signature = keyring.sign_transaction(message, private_key)
    
    # Verify that signature is bytes
    assert isinstance(signature, bytes)
    assert len(signature) == 32  # SHA-256 produces 32 bytes
    
    # Verify the signature
    assert keyring.verify_signature(message, signature, public_key) 