"""
Quantum-resistant keyring implementation for Solana wallet.
Integrates multiple quantum-resistant algorithms from quantum_hash.
"""

import os
import base64
import json
from pathlib import Path
from typing import Dict, Tuple, Optional, List, Any, Union

# Import quantum_hash components
from quantum_hash import DiracHash, QuantumEnhancedHash
from quantum_hash.signatures import LamportSignature, SPHINCSSignature, DilithiumSignature
from quantum_hash.kem import KyberKEM

# Define signature algorithm options
SIGNATURE_ALGORITHMS = {
    "sphincs": SPHINCSSignature,
    "dilithium": DilithiumSignature,
    "lamport": LamportSignature,
}

# Define hash algorithm options
HASH_ALGORITHMS = {
    "dirac_standard": lambda data: DiracHash.hash(data, algorithm="standard"),
    "dirac_improved": lambda data: DiracHash.hash(data, algorithm="improved"),
    "dirac_grover": lambda data: DiracHash.hash(data, algorithm="grover"),
    "dirac_shor": lambda data: DiracHash.hash(data, algorithm="shor"),
    "quantum_enhanced": lambda data: QuantumEnhancedHash.hash(data),
}


class QuantumKeyring:
    """
    Quantum-resistant keyring for Solana wallet.
    """
    
    def __init__(
        self, 
        signature_algorithm: str = "sphincs",
        hash_algorithm: str = "dirac_improved",
        security_level: int = 3,
        backup_algorithms: bool = True
    ):
        """
        Initialize the quantum keyring.
        
        Args:
            signature_algorithm: The quantum-resistant signature algorithm to use
            hash_algorithm: The quantum-resistant hash algorithm to use
            security_level: Security level for algorithms that support it
            backup_algorithms: Whether to generate backup keys with different algorithms
        """
        if signature_algorithm not in SIGNATURE_ALGORITHMS:
            raise ValueError(f"Unsupported signature algorithm: {signature_algorithm}")
        
        if hash_algorithm not in HASH_ALGORITHMS:
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}")
        
        self.signature_algorithm = signature_algorithm
        self.hash_algorithm = hash_algorithm
        self.security_level = security_level
        self.backup_algorithms = backup_algorithms
        
        # Initialize the primary signature scheme
        if signature_algorithm == "dilithium":
            self.signer = SIGNATURE_ALGORITHMS[signature_algorithm](security_level=security_level)
        else:
            self.signer = SIGNATURE_ALGORITHMS[signature_algorithm]()
        
        # Initialize KEM for encryption
        self.kem = KyberKEM(security_level=security_level)
    
    def generate_keypair(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate a quantum-resistant keypair.
        
        Returns:
            Tuple of (private_key_dict, public_key_dict)
        """
        # Generate primary keypair
        private_key, public_key = self.signer.generate_keypair()
        
        # Generate KEM keypair for encryption
        kem_public_key, kem_private_key = self.kem.generate_keypair()
        
        # Create key dictionaries
        private_key_dict = {
            "primary": {
                "algorithm": self.signature_algorithm,
                "key": self._encode_key(private_key),
                "security_level": self.security_level,
            },
            "encryption": {
                "algorithm": "kyber",
                "key": self._encode_key(kem_private_key),
                "security_level": self.security_level,
            },
        }
        
        public_key_dict = {
            "primary": {
                "algorithm": self.signature_algorithm,
                "key": self._encode_key(public_key),
                "security_level": self.security_level,
            },
            "encryption": {
                "algorithm": "kyber",
                "key": self._encode_key(kem_public_key),
                "security_level": self.security_level,
            },
        }
        
        # Generate backup keys if requested
        if self.backup_algorithms:
            private_key_dict["backups"] = []
            public_key_dict["backups"] = []
            
            # Generate keys for each alternative algorithm
            for algo_name, algo_class in SIGNATURE_ALGORITHMS.items():
                if algo_name == self.signature_algorithm:
                    continue
                
                # Initialize algorithm
                if algo_name == "dilithium":
                    algo = algo_class(security_level=self.security_level)
                else:
                    algo = algo_class()
                
                # Generate keypair
                backup_private, backup_public = algo.generate_keypair()
                
                private_key_dict["backups"].append({
                    "algorithm": algo_name,
                    "key": self._encode_key(backup_private),
                    "security_level": self.security_level if algo_name == "dilithium" else None,
                })
                
                public_key_dict["backups"].append({
                    "algorithm": algo_name,
                    "key": self._encode_key(backup_public),
                    "security_level": self.security_level if algo_name == "dilithium" else None,
                })
        
        return private_key_dict, public_key_dict
    
    def derive_address(self, public_key_dict: Dict[str, Any]) -> str:
        """
        Derive a Solana address from a quantum-resistant public key.
        
        Args:
            public_key_dict: The public key dictionary
            
        Returns:
            Solana address as base58 string
        """
        # Extract primary public key
        primary_public_key = self._decode_key(public_key_dict["primary"]["key"])
        
        # Serialize the public key to bytes
        serialized_key = json.dumps(public_key_dict, sort_keys=True).encode()
        
        # Hash the serialized key using the selected hash algorithm
        address_bytes = HASH_ALGORITHMS[self.hash_algorithm](serialized_key)
        
        # Encode as base58 (Solana's address format)
        # Note: In a real implementation, we'd need a proper base58 encoding
        # For now, using base64 as a placeholder
        return base64.b64encode(address_bytes).decode('utf-8')
    
    def sign_transaction(self, transaction_data: bytes, private_key_dict: Dict[str, Any]) -> bytes:
        """
        Sign transaction data with the quantum-resistant private key.
        
        Args:
            transaction_data: The transaction data to sign
            private_key_dict: The private key dictionary
            
        Returns:
            Signature bytes
        """
        # Extract primary private key and algorithm
        primary_key = self._decode_key(private_key_dict["primary"]["key"])
        algorithm = private_key_dict["primary"]["algorithm"]
        
        # Initialize the appropriate signer if needed
        if algorithm != self.signature_algorithm:
            if algorithm == "dilithium":
                signer = SIGNATURE_ALGORITHMS[algorithm](security_level=private_key_dict["primary"]["security_level"])
            else:
                signer = SIGNATURE_ALGORITHMS[algorithm]()
        else:
            signer = self.signer
        
        # Sign the transaction
        signature = signer.sign(transaction_data, primary_key)
        
        # Convert signature to bytes if it's not already
        if not isinstance(signature, bytes):
            signature = json.dumps(signature).encode()
        
        return signature
    
    def verify_transaction(
        self, transaction_data: bytes, signature: bytes, public_key_dict: Dict[str, Any]
    ) -> bool:
        """
        Verify a transaction signature with the quantum-resistant public key.
        
        Args:
            transaction_data: The transaction data
            signature: The signature to verify
            public_key_dict: The public key dictionary
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Extract primary public key and algorithm
        primary_key = self._decode_key(public_key_dict["primary"]["key"])
        algorithm = public_key_dict["primary"]["algorithm"]
        
        # Initialize the appropriate verifier if needed
        if algorithm != self.signature_algorithm:
            if algorithm == "dilithium":
                verifier = SIGNATURE_ALGORITHMS[algorithm](security_level=public_key_dict["primary"]["security_level"])
            else:
                verifier = SIGNATURE_ALGORITHMS[algorithm]()
        else:
            verifier = self.signer
        
        # Convert signature from bytes if needed
        if isinstance(signature, bytes):
            try:
                # Try to parse as JSON if it's a complex signature object
                signature = json.loads(signature.decode())
            except:
                # Keep as bytes if it can't be parsed
                pass
        
        # Verify the signature
        return verifier.verify(transaction_data, signature, primary_key)
    
    def encrypt(self, data: bytes, public_key_dict: Dict[str, Any]) -> Tuple[bytes, bytes]:
        """
        Encrypt data using the quantum-resistant KEM.
        
        Args:
            data: The data to encrypt
            public_key_dict: The public key dictionary
            
        Returns:
            Tuple of (ciphertext, shared_secret)
        """
        # Extract encryption public key
        kem_public_key = self._decode_key(public_key_dict["encryption"]["key"])
        
        # Encapsulate a shared secret
        ciphertext, shared_secret = self.kem.encapsulate(kem_public_key)
        
        # XOR the data with the shared secret for encryption
        # Note: In a real implementation, we would use a proper symmetric encryption
        padded_secret = self._pad_to_length(shared_secret, len(data))
        encrypted_data = bytes(a ^ b for a, b in zip(data, padded_secret))
        
        return encrypted_data, ciphertext
    
    def decrypt(
        self, encrypted_data: bytes, ciphertext: bytes, private_key_dict: Dict[str, Any]
    ) -> bytes:
        """
        Decrypt data using the quantum-resistant KEM.
        
        Args:
            encrypted_data: The encrypted data
            ciphertext: The ciphertext from encapsulation
            private_key_dict: The private key dictionary
            
        Returns:
            Decrypted data
        """
        # Extract encryption private key
        kem_private_key = self._decode_key(private_key_dict["encryption"]["key"])
        
        # Decapsulate the shared secret
        shared_secret = self.kem.decapsulate(ciphertext, kem_private_key)
        
        # XOR the data with the shared secret for decryption
        padded_secret = self._pad_to_length(shared_secret, len(encrypted_data))
        decrypted_data = bytes(a ^ b for a, b in zip(encrypted_data, padded_secret))
        
        return decrypted_data
    
    def _encode_key(self, key: Any) -> str:
        """
        Encode a key to string format for JSON serialization.
        Handles various types of keys ensuring all are JSON serializable.
        """
        if isinstance(key, bytes):
            return base64.b64encode(key).decode('utf-8')
        elif isinstance(key, (int, float, str, bool, type(None))):
            # These primitive types are already JSON serializable
            return base64.b64encode(str(key).encode()).decode('utf-8')
        elif isinstance(key, (dict, list)):
            # Convert any nested bytes in collections
            serializable_obj = self._make_json_serializable(key)
            json_str = json.dumps(serializable_obj)
            return base64.b64encode(json_str.encode()).decode('utf-8')
        else:
            # For objects that aren't JSON serializable, convert to string or dict
            try:
                # Try to serialize the object - if it has bytes inside, convert them first
                if hasattr(key, '__dict__'):
                    # Convert all bytes in __dict__ to base64 strings
                    serializable_dict = self._make_json_serializable(key.__dict__)
                    json_str = json.dumps(serializable_dict)
                    return base64.b64encode(json_str.encode()).decode('utf-8')
                else:
                    # Last resort: convert to string
                    return base64.b64encode(str(key).encode()).decode('utf-8')
            except (TypeError, ValueError) as e:
                # If all else fails, use the string representation
                print(f"Error encoding key: {e}, using string representation")
                return base64.b64encode(str(key).encode()).decode('utf-8')
                
    def _make_json_serializable(self, obj):
        """
        Recursively convert an object to be JSON serializable.
        Converts bytes to base64 strings and handles nested structures.
        """
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_json_serializable(obj.__dict__)
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            # For any other type, convert to string
            return str(obj)
    
    def _decode_key(self, encoded_key: str) -> Any:
        """Decode a key from string format."""
        decoded = base64.b64decode(encoded_key)
        try:
            # Try to parse as JSON if it's a complex object
            return json.loads(decoded)
        except:
            # Return as bytes if it can't be parsed
            return decoded
    
    def _pad_to_length(self, data: bytes, length: int) -> bytes:
        """Pad data to a specific length by repeating it."""
        return (data * (length // len(data) + 1))[:length] 