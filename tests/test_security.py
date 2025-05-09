"""
Security tests for quantum wallet implementation
"""
import pytest
import os
import json
from dirac_wallet.core.keys import KeyPair, QuantumKeyManager
from dirac_wallet.core.secure_storage import SecureStorage

def test_secure_storage_encryption():
    """Test that secure storage properly encrypts and decrypts data"""
    password = "test_password123"
    test_data = {"sensitive": "data", "key": "value"}
    
    # Create secure storage
    storage = SecureStorage(password)
    
    # Encrypt data
    encrypted = storage.encrypt_data(test_data)
    
    # Verify encrypted data is different from original
    assert encrypted != str(test_data).encode()
    
    # Decrypt data
    decrypted = storage.decrypt_data(encrypted)
    
    # Verify decrypted data matches original
    assert decrypted == test_data

def test_secure_storage_salt():
    """Test that different salts produce different keys"""
    password = "test_password123"
    
    # Create two storage instances with different salts
    storage1 = SecureStorage(password)
    storage2 = SecureStorage(password)
    
    # Verify different salts
    assert storage1.salt != storage2.salt
    
    # Verify different encryption results
    test_data = {"test": "data"}
    encrypted1 = storage1.encrypt_data(test_data)
    encrypted2 = storage2.encrypt_data(test_data)
    
    assert encrypted1 != encrypted2

def test_keypair_secure_storage():
    """Test that KeyPair properly handles secure storage"""
    # Generate keypair
    key_manager = QuantumKeyManager()
    keypair = key_manager.generate_keypair()
    
    # Set up secure storage
    password = "test_password123"
    keypair.set_secure_storage(password)
    
    # Serialize with encryption
    serialized = keypair.serialize()
    
    # Verify private key is encrypted
    assert "encrypted_private_key" in serialized
    assert "salt" in serialized
    assert "private_key" not in serialized
    
    # Deserialize with password
    deserialized = KeyPair.deserialize(serialized, password)
    
    # Verify keys match
    assert deserialized.private_key == keypair.private_key
    assert deserialized.public_key == keypair.public_key

def test_keypair_secure_storage_wrong_password():
    """Test that KeyPair deserialization fails with wrong password"""
    # Generate keypair
    key_manager = QuantumKeyManager()
    keypair = key_manager.generate_keypair()
    
    # Set up secure storage
    keypair.set_secure_storage("correct_password")
    
    # Serialize with encryption
    serialized = keypair.serialize()
    
    # Attempt to deserialize with wrong password
    with pytest.raises(Exception):
        KeyPair.deserialize(serialized, "wrong_password")

def test_key_generation_randomness():
    """Test that generated keys are sufficiently random"""
    key_manager = QuantumKeyManager()
    
    # Generate multiple keypairs
    keypairs = [key_manager.generate_keypair() for _ in range(5)]
    
    # Verify all public keys are different
    public_keys = [str(kp.public_key) for kp in keypairs]
    assert len(set(public_keys)) == len(keypairs)
    
    # Verify all private keys are different
    private_keys = [str(kp.private_key) for kp in keypairs]
    assert len(set(private_keys)) == len(keypairs)

def test_secure_storage_persistence():
    """Test that secure storage can be recreated with same salt"""
    password = "test_password123"
    test_data = {"sensitive": "data"}
    
    # Create initial storage
    storage1 = SecureStorage(password)
    salt = storage1.salt
    
    # Encrypt data
    encrypted = storage1.encrypt_data(test_data)
    
    # Create new storage with same salt
    storage2 = SecureStorage(password, salt)
    
    # Verify decryption works
    decrypted = storage2.decrypt_data(encrypted)
    assert decrypted == test_data 