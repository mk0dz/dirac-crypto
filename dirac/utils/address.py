"""
Address generation and validation utilities.
"""

import hashlib
import base64
from typing import Dict, Any, Optional

try:
    import base58
    from solders.pubkey import Pubkey
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    base58 = None
    Pubkey = None

def get_solana_address_from_bytes(key_bytes: bytes) -> str:
    """
    Convert bytes to a valid Solana address.
    
    Args:
        key_bytes: Raw bytes for the public key
        
    Returns:
        A Solana address as a base58 encoded string
    """
    # If Solana libraries are available, use them for proper conversion
    if SOLANA_AVAILABLE and Pubkey is not None:
        try:
            # Ensure we have exactly 32 bytes
            if len(key_bytes) != 32:
                key_bytes = hashlib.sha256(key_bytes).digest()
            
            # Create a Pubkey object and convert to string
            pubkey = Pubkey.from_bytes(key_bytes)
            return str(pubkey)
        except Exception:
            # Fall back to the simplified method if there's an error
            pass
    
    # Simplified fallback method
    hashed = hashlib.sha256(key_bytes).digest()
    
    # Use base58 if available, otherwise use a simplified encoding
    if SOLANA_AVAILABLE and base58 is not None:
        return base58.b58encode(hashed).decode('utf-8')
    else:
        # Simple conversion algorithm with base58-like character set
        chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        result = ""
        
        value = int.from_bytes(hashed, byteorder='big')
        while value > 0:
            value, remainder = divmod(value, 58)
            result = chars[remainder] + result
        
        # Ensure it's the right length for a Solana address
        while len(result) < 32:
            result = chars[0] + result
        
        return result[:44]  # Solana addresses are typically this length

def validate_solana_address(address: str) -> bool:
    """
    Validate a Solana address format.
    
    Args:
        address: Solana address to validate
        
    Returns:
        True if the address is valid, False otherwise
    """
    # Use Solana libraries for proper validation if available
    if SOLANA_AVAILABLE and Pubkey is not None:
        try:
            Pubkey.from_string(address)
            return True
        except Exception:
            return False
    
    # Simplified fallback check
    # Check length (Solana addresses are typically 32-44 characters)
    if not (32 <= len(address) <= 44):
        return False
        
    # Check character set
    valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
    return all(c in valid_chars for c in address)

def pubkey_to_base58(pubkey: Any) -> Optional[str]:
    """
    Convert a Solana Pubkey object to a base58 encoded string.
    
    Args:
        pubkey: A Solana Pubkey object
        
    Returns:
        Base58 encoded string of the public key
    """
    if not SOLANA_AVAILABLE or Pubkey is None or not isinstance(pubkey, Pubkey):
        return None
    
    try:
        return str(pubkey)
    except Exception:
        return None 