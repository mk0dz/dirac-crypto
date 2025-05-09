"""
Quantum-resistant key generation using Dilithium
"""
import base64
import json
from dataclasses import dataclass
from typing import Tuple, Dict, Optional

from quantum_hash.signatures import DilithiumSignature
from .secure_storage import SecureStorage
from ..utils.logger import logger


@dataclass
class KeyPair:
    """Container for a quantum-resistant key pair"""
    private_key: Dict
    public_key: Dict
    algorithm: str = "dilithium"
    security_level: int = 3
    _secure_storage: Optional[SecureStorage] = None
                
    def serialize(self) -> Dict:
        """Serialize keypair to dict for storage"""
        serialized = {
            "algorithm": self.algorithm,
            "security_level": self.security_level,
            "public_key": self._serialize_key(self.public_key)
        }
        
        # Only store encrypted private key if secure storage is available
        if self._secure_storage:
            encrypted_private = self._secure_storage.encrypt_data(self.private_key)
            serialized["encrypted_private_key"] = base64.b64encode(encrypted_private).decode()
            serialized["salt"] = base64.b64encode(self._secure_storage.get_salt()).decode()
        else:
            serialized["private_key"] = self._serialize_key(self.private_key)
            
        return serialized
    
    @classmethod
    def deserialize(cls, data: Dict, password: Optional[str] = None) -> 'KeyPair':
        """Deserialize keypair from storage format"""
        if "encrypted_private_key" in data and password:
            # Decrypt private key
            salt = base64.b64decode(data["salt"])
            storage = SecureStorage(password, salt)
            encrypted_private = base64.b64decode(data["encrypted_private_key"])
            private_key = storage.decrypt_data(encrypted_private)
        else:
            private_key = cls._deserialize_key(data["private_key"])
            
        return cls(
            private_key=private_key,
            public_key=cls._deserialize_key(data["public_key"]),
            algorithm=data["algorithm"],
            security_level=data["security_level"]
        )
    
    def set_secure_storage(self, password: str):
        """Set up secure storage for the private key"""
        self._secure_storage = SecureStorage(password)
        logger.info("Secure storage initialized for keypair")
    
    @staticmethod
    def _serialize_key(key: Dict) -> Dict:
        """Helper to serialize individual key components"""
        serialized = {}
        for k, v in key.items():
            if isinstance(v, bytes):
                # Convert bytes to base64
                serialized[k] = base64.b64encode(v).decode()
            elif isinstance(v, (list, tuple)):
                # Convert arrays that might contain bytes
                try:
                    # If it's a list of bytes or a list that might contain bytes
                    serialized[k] = [base64.b64encode(item).decode() if isinstance(item, bytes) else item for item in v]
                except:
                    # Fallback to basic list serialization
                    serialized[k] = v
            else:
                serialized[k] = v
        return serialized
    
    @staticmethod
    def _deserialize_key(key: Dict) -> Dict:
        """Helper to deserialize individual key components"""
        deserialized = {}
        for k, v in key.items():
            if isinstance(v, str) and k != "type":
                try:
                    # Attempt to decode base64
                    decoded = base64.b64decode(v)
                    # This should be bytes, keep it as bytes
                    deserialized[k] = decoded
                except:
                    # If it's not base64, keep as is
                    deserialized[k] = v
            elif isinstance(v, list):
                # Handle list of strings that might be base64 encoded bytes
                try:
                    decoded_list = []
                    for item in v:
                        if isinstance(item, str):
                            try:
                                decoded_list.append(base64.b64decode(item))
                            except:
                                decoded_list.append(item)
                        else:
                            decoded_list.append(item)
                    deserialized[k] = decoded_list
                except:
                    # Fallback 
                    deserialized[k] = v
            else:
                deserialized[k] = v
        return deserialized


class QuantumKeyManager:
    """Manages quantum-resistant key generation and operations"""
    
    def __init__(self, security_level: int = 3):
        """Initialize the key manager with Dilithium settings"""
        self.security_level = security_level
        self.dilithium = DilithiumSignature(security_level=security_level)
        logger.info(f"Initialized QuantumKeyManager with Dilithium security level {security_level}")
    
    def generate_keypair(self) -> KeyPair:
        """Generate a new quantum-resistant key pair"""
        try:
            logger.debug("Generating new Dilithium key pair...")
            private_key, public_key = self.dilithium.generate_keypair()
            
            keypair = KeyPair(
                private_key=private_key,
                public_key=public_key,
                security_level=self.security_level
            )
            
            logger.info("Successfully generated quantum-resistant key pair")
            return keypair
            
        except Exception as e:
            logger.error(f"Failed to generate key pair: {str(e)}")
            raise
    
    def sign_message(self, message: bytes, private_key: Dict) -> Dict:
        """Sign a message using the private key"""
        try:
            signature = self.dilithium.sign(message, private_key)
            logger.debug(f"Message signed, signature size: {len(str(signature))} bytes")
            return signature
            
        except Exception as e:
            logger.error(f"Failed to sign message: {str(e)}")
            raise
    
    def verify_signature(self, message: bytes, signature: Dict, public_key: Dict) -> bool:
        """Verify a signature using the public key"""
        try:
            is_valid = self.dilithium.verify(message, signature, public_key)
            logger.debug(f"Signature verification result: {is_valid}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Failed to verify signature: {str(e)}")
            raise
    
    def get_public_key_bytes(self, public_key: Dict) -> bytes:
        """Extract public key as bytes for address generation"""
        # Extract the key components and create a deterministic byte representation
        # This is used for generating the Solana address
        try:
            if "s1" in public_key:
                # Dilithium public key structure includes s1 vector
                s1 = public_key["s1"]
                if isinstance(s1, bytes):
                    return s1
                elif isinstance(s1, list):
                    # Concatenate list items if they're bytes
                    if all(isinstance(item, bytes) for item in s1):
                        return b''.join(s1)
                    else:
                        # Convert to string representation
                        return str(s1).encode("utf-8")
                else:
                    return str(s1).encode("utf-8")
            else:
                # Create a deterministic representation without JSON serialization
                # Sort keys to ensure consistency
                sorted_items = []
                for k in sorted(public_key.keys()):
                    v = public_key[k]
                    if isinstance(v, bytes):
                        sorted_items.append(f"{k}:{len(v)}")
                    else:
                        sorted_items.append(f"{k}:{str(v)}")
                return "\n".join(sorted_items).encode("utf-8")
        except Exception as e:
            logger.error(f"Failed to extract public key bytes: {str(e)}")
            # Fallback: use the string representation
            return str(public_key).encode("utf-8")