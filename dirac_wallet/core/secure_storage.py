"""
Secure storage implementation for quantum wallet keys
"""
import os
import base64
from typing import Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ..utils.logger import logger

class SecureStorage:
    """Handles secure storage of sensitive wallet data"""
    
    def __init__(self, password: str, salt: Optional[bytes] = None):
        """
        Initialize secure storage with password-based encryption
        
        Args:
            password: User password for encryption
            salt: Optional salt for key derivation. If None, generates new salt
        """
        self.salt = salt or os.urandom(16)
        self.key = self._derive_key(password)
        self.cipher_suite = Fernet(self.key)
        logger.info("Initialized secure storage")
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        try:
            # Always use UTF-8 for password encoding to support all Unicode characters
            password_bytes = password.encode('utf-8')
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.salt,
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(password_bytes))
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def encrypt_data(self, data: Dict) -> bytes:
        """Encrypt sensitive data"""
        try:
            # Convert dictionary to string and encode with UTF-8
            serialized = str(data).encode('utf-8')
            return self.cipher_suite.encrypt(serialized)
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes) -> Dict:
        """Decrypt sensitive data"""
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data)
            # Use utf-8 for decoding as well
            return eval(decrypted.decode('utf-8'))  # Safe since we only store our own data
        except Exception as e:
            logger.error(f"Invalid password or corrupted data")
            raise ValueError("Invalid password or corrupted data") from e
    
    def get_salt(self) -> bytes:
        """Get the salt used for key derivation"""
        return self.salt 