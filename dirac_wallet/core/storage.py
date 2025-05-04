"""
Secure storage for wallet data
"""
import os
from typing import Union
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from ..utils.logger import logger


class SecureStorage:
    """Handles secure encryption and decryption of wallet data"""
    
    def __init__(self, 
                 key_derivation_rounds: int = 100000,
                 key_length: int = 32):
        """Initialize secure storage with encryption parameters"""
        self.key_derivation_rounds = key_derivation_rounds
        self.key_length = key_length
        logger.debug(f"Initialized SecureStorage with {key_derivation_rounds} rounds")
    
    def encrypt(self, data: bytes, password: str) -> bytes:
        """Encrypt data using AES-256-GCM"""
        try:
            # Generate salt for key derivation
            salt = get_random_bytes(16)
            
            # Derive key from password using PBKDF2
            key = PBKDF2(
                password,
                salt,
                dkLen=self.key_length,
                count=self.key_derivation_rounds,
                hmac_hash_module=SHA256
            )
            
            # Generate nonce for AES-GCM
            nonce = get_random_bytes(12)
            
            # Encrypt data
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            
            # Combine salt + nonce + tag + ciphertext
            encrypted_data = salt + nonce + tag + ciphertext
            
            logger.debug(f"Data encrypted successfully, size: {len(encrypted_data)} bytes")
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: bytes, password: str) -> bytes:
        """Decrypt data using AES-256-GCM"""
        try:
            # Extract components
            salt = encrypted_data[:16]
            nonce = encrypted_data[16:28]
            tag = encrypted_data[28:44]
            ciphertext = encrypted_data[44:]
            
            # Derive key from password
            key = PBKDF2(
                password,
                salt,
                dkLen=self.key_length,
                count=self.key_derivation_rounds,
                hmac_hash_module=SHA256
            )
            
            # Decrypt data
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            
            logger.debug(f"Data decrypted successfully, size: {len(data)} bytes")
            return data
            
        except ValueError as e:
            logger.error("Invalid password or corrupted data")
            raise ValueError("Invalid password or corrupted data")
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def verify_password(self, encrypted_data: bytes, password: str) -> bool:
        """Verify if password can decrypt data without full decryption"""
        try:
            # Try to decrypt just a small portion to verify password
            salt = encrypted_data[:16]
            nonce = encrypted_data[16:28]
            tag = encrypted_data[28:44]
            ciphertext = encrypted_data[44:48]  # Just first 4 bytes
            
            key = PBKDF2(
                password,
                salt,
                dkLen=self.key_length,
                count=self.key_derivation_rounds,
                hmac_hash_module=SHA256
            )
            
            # Test key with short ciphertext
            try:
                cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
                cipher.decrypt_and_verify(ciphertext, tag[:16])
                return True
            except:
                return False
            
        except Exception:
            return False