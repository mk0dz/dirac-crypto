"""
Address derivation for Dirac-Wallet using quantum-resistant keys
"""
import hashlib
import base58
from typing import Dict
from solders.keypair import Keypair

from quantum_hash import DiracHash
from .keys import KeyPair
from ..utils.logger import logger


class AddressDerivation:
    """Handles address generation from quantum-resistant keys"""
    
    @staticmethod
    def derive_solana_address(public_key_bytes: bytes) -> str:
        """
        Derive a Solana-compatible address from quantum-resistant public key bytes
        
        Note: This uses DiracHash to create a 32-byte hash suitable for Solana addresses
        """
        try:
            # Use DiracHash to create a 32-byte hash from the quantum public key
            # This gives us a standard 32-byte key that Solana expects
            key_hash = DiracHash.hash(public_key_bytes, digest_size=32, algorithm="improved")
            
            # Convert to Solana address format using base58 encoding
            address = base58.b58encode(key_hash).decode('ascii')
            
            logger.debug(f"Derived Solana address from quantum key: {address}")
            return address
            
        except Exception as e:
            logger.error(f"Failed to derive Solana address: {str(e)}")
            raise
    
    @staticmethod
    def create_quantum_keypair(keypair: KeyPair) -> Dict:
        """
        Create a hybrid quantum-Solana keypair with address mapping
        
        Returns a dictionary containing:
        - quantum_keypair: original quantum-resistant keypair
        - solana_address: derived Solana address
        - keypair_info: metadata about the keypair
        """
        try:
            # Extract public key bytes (using improved method from QuantumKeyManager)
            from .keys import QuantumKeyManager
            key_manager = QuantumKeyManager(security_level=keypair.security_level)
            pub_key_bytes = key_manager.get_public_key_bytes(keypair.public_key)
            
            # Create a deterministic seed from the quantum public key
            hasher = hashlib.sha256()
            hasher.update(pub_key_bytes)
            seed = hasher.digest()
            
            # Create a Solana keypair from the seed
            solana_keypair = Keypair.from_seed(seed)
            solana_address = str(solana_keypair.pubkey())
            
            # Create hybrid keypair info
            hybrid_keypair = {
                "quantum_keypair": keypair,
                "solana_keypair": solana_keypair,
                "solana_address": solana_address,
                "keypair_info": {
                    "algorithm": keypair.algorithm,
                    "security_level": keypair.security_level,
                    "public_key_size": len(pub_key_bytes),
                    "address_type": "quantum_derived"
                }
            }
            
            logger.info(f"Created quantum-Solana hybrid keypair with address: {solana_address}")
            return hybrid_keypair
            
        except Exception as e:
            logger.error(f"Failed to create quantum keypair: {str(e)}")
            raise
    
    @staticmethod
    def verify_address_mapping(quantum_keypair: KeyPair, solana_address: str) -> bool:
        """
        Verify that a Solana address correctly maps to a quantum keypair
        """
        try:
            # Re-derive the address from the quantum keypair using the same 
            # method as in create_quantum_keypair
            from .keys import QuantumKeyManager
            key_manager = QuantumKeyManager(security_level=quantum_keypair.security_level)
            pub_key_bytes = key_manager.get_public_key_bytes(quantum_keypair.public_key)
            
            # Create a deterministic seed from the quantum public key
            hasher = hashlib.sha256()
            hasher.update(pub_key_bytes)
            seed = hasher.digest()
            
            # Create a Solana keypair from the seed
            solana_keypair = Keypair.from_seed(seed)
            derived_address = str(solana_keypair.pubkey())
            
            is_valid = derived_address == solana_address
            logger.debug(f"Address mapping verification: {is_valid}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Failed to verify address mapping: {str(e)}")
            return False