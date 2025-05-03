"""
Utilities for converting between quantum addresses and Solana pubkeys.
"""

import base64
import hashlib
from typing import Optional

from solders.pubkey import Pubkey

class AddressConverter:
    """
    Converter between quantum-resistant addresses and Solana addresses.
    """
    
    @staticmethod
    def quantum_to_solana(quantum_address: str) -> Pubkey:
        """
        Convert a quantum-resistant base64 address to a Solana pubkey.
        
        Args:
            quantum_address: Base64-encoded quantum address
            
        Returns:
            Solana pubkey
        """
        # Decode base64 address
        raw_bytes = base64.b64decode(quantum_address)
        
        # Take the first 32 bytes (Solana pubkey size) or hash it down to size
        if len(raw_bytes) != 32:
            raw_bytes = hashlib.sha256(raw_bytes).digest()
        
        # Create Solana pubkey
        pubkey = Pubkey(raw_bytes)
        
        return pubkey
    
    @staticmethod
    def solana_to_quantum(pubkey: Pubkey, hash_algorithm: Optional[str] = None) -> str:
        """
        Convert a Solana pubkey to a quantum-resistant base64 address.
        This is a one-way conversion for display purposes only.
        
        Args:
            pubkey: Solana pubkey
            hash_algorithm: Optional hash algorithm to use
            
        Returns:
            Base64-encoded quantum address
        """
        # Get bytes from pubkey
        pubkey_bytes = bytes(pubkey)
        
        # Optionally apply additional hashing for increased security
        if hash_algorithm == "sha256":
            pubkey_bytes = hashlib.sha256(pubkey_bytes).digest()
        elif hash_algorithm == "sha512":
            pubkey_bytes = hashlib.sha512(pubkey_bytes).digest()
        
        # Encode as base64
        quantum_address = base64.b64encode(pubkey_bytes).decode('utf-8')
        
        return quantum_address

    @staticmethod
    def is_valid_solana_address(address: str) -> bool:
        """
        Check if a string is a valid Solana address.
        
        Args:
            address: String to check
            
        Returns:
            True if valid Solana address, False otherwise
        """
        try:
            # Try to create a Pubkey from the address
            Pubkey.from_string(address)
            return True
        except Exception:
            return False
    
    @staticmethod
    def is_valid_quantum_address(address: str) -> bool:
        """
        Check if a string is a valid quantum address.
        
        Args:
            address: String to check
            
        Returns:
            True if valid quantum address, False otherwise
        """
        try:
            # Try to decode the base64 string
            raw_bytes = base64.b64decode(address)
            # Quantum addresses should be at least 32 bytes
            return len(raw_bytes) >= 32
        except Exception:
            return False 