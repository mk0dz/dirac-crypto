"""
Solana keypair conversion utilities.
"""

import base64
import hashlib
from typing import Dict, Any, Optional, Tuple

# Import quantum algorithms
from quantum_hash import DiracHash, QuantumEnhancedHash

try:
    import base58
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    base58 = None
    Keypair = None
    Pubkey = None

def convert_to_solana_keypair(private_key: Dict[str, Any]) -> Optional[object]:
    """
    Convert a DiracWallet private key to a Solana keypair.
    
    Args:
        private_key: The DiracWallet private key dictionary
        
    Returns:
        A Solana keypair object if Solana libraries are available, None otherwise
    """
    if not SOLANA_AVAILABLE or Keypair is None:
        return None
    
    # Extract the seed from the private key
    seed = private_key.get("seed")
    if not seed:
        return None
    
    try:
        # The seed needs to be exactly 32 bytes for Solana keypairs
        # Use DiracHash to derive a deterministic 32-byte seed
        if len(seed) != 32:
            # Use the algorithm specified in the private key or default to grover
            algorithm = private_key.get("algorithm", "grover")
            if algorithm not in ["standard", "improved", "grover", "shor"]:
                algorithm = "grover"
                
            seed = DiracHash.hash(seed, algorithm=algorithm, digest_size=32)
        
        # Construct a Solana keypair from the seed
        keypair = Keypair.from_bytes(seed)
        return keypair
    except Exception as e:
        print(f"Keypair conversion error: {str(e)}")
        return None

def convert_from_solana_keypair(keypair) -> Dict[str, Any]:
    """
    Convert a Solana keypair to a DiracWallet private key format.
    
    Args:
        keypair: A Solana keypair object
        
    Returns:
        A DiracWallet private key dictionary
    """
    if not SOLANA_AVAILABLE or not isinstance(keypair, Keypair):
        # Return a mock private key if Solana is not available
        return {
            "algorithm": "sphincs",
            "seed": b"mock_private_key",
            "security_level": 3
        }
    
    try:
        # Extract seed from keypair
        seed = keypair.secret()
        
        # Create a DiracWallet private key format
        private_key = {
            "algorithm": "sphincs",  # Default to sphincs
            "seed": seed,
            "security_level": 3      # Default security level
        }
        
        return private_key
    except Exception as e:
        print(f"Solana keypair extraction error: {str(e)}")
        # Return a mock private key on error
        return {
            "algorithm": "sphincs",
            "seed": b"error_private_key",
            "security_level": 3
        }

def get_pubkey_from_bytes(key_bytes: bytes) -> Optional[object]:
    """
    Convert bytes to a Solana Pubkey object.
    
    Args:
        key_bytes: Raw bytes for the public key
        
    Returns:
        A Solana Pubkey object if Solana libraries are available, None otherwise
    """
    if not SOLANA_AVAILABLE or Pubkey is None:
        return None
    
    try:
        # Ensure we have exactly 32 bytes using QuantumEnhancedHash
        if len(key_bytes) != 32:
            key_bytes = QuantumEnhancedHash.hash(key_bytes, digest_size=32)
        
        pubkey = Pubkey.from_bytes(key_bytes)
        return pubkey
    except Exception as e:
        print(f"Pubkey conversion error: {str(e)}")
        return None

def keypair_to_base58(keypair) -> Optional[str]:
    """
    Convert a Solana keypair to base58 encoded string.
    
    Args:
        keypair: A Solana keypair object
        
    Returns:
        Base58 encoded string of the keypair's public key
    """
    if not SOLANA_AVAILABLE or not isinstance(keypair, Keypair):
        return None
    
    try:
        return str(keypair.pubkey())
    except Exception as e:
        print(f"Base58 conversion error: {str(e)}")
        return None

def create_keypair_from_base58(private_key_base58: str) -> Optional[object]:
    """
    Create a Solana keypair from a base58 encoded private key string.
    
    Args:
        private_key_base58: Base58 encoded private key string
        
    Returns:
        A Solana keypair object if Solana libraries are available, None otherwise
    """
    if not SOLANA_AVAILABLE or Keypair is None or base58 is None:
        return None
    
    try:
        # Decode base58 string to bytes
        private_key_bytes = base58.b58decode(private_key_base58)
        
        # Create keypair from bytes
        keypair = Keypair.from_bytes(private_key_bytes)
        return keypair
    except Exception as e:
        print(f"Keypair creation error: {str(e)}")
        return None 