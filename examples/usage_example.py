#!/usr/bin/env python3
"""
Example usage of Dirac-Wallet key generation with fixed import
"""

from pathlib import Path


from dirac_wallet.core.keys import QuantumKeyManager
from dirac_wallet.utils.logger import logger


def main():
    # Initialize key manager
    logger.info("Initializing Quantum Key Manager...")
    key_manager = QuantumKeyManager(security_level=3)
    
    # Generate a new key pair
    logger.info("Generating quantum-resistant key pair...")
    keypair = key_manager.generate_keypair()
    
    # Display key information
    print("\n=== Quantum-Resistant Key Pair Generated ===")
    print(f"Algorithm: {keypair.algorithm}")
    print(f"Security Level: {keypair.security_level}")
    print(f"Private Key Type: {type(keypair.private_key)}")
    print(f"Public Key Type: {type(keypair.public_key)}")
    
    # Test serialization
    serialized = keypair.serialize()
    print("\nKey pair serialized successfully")
    
    # Test signing and verification
    message = b"Hello from Dirac-Wallet!"
    signature = key_manager.sign_message(message, keypair.private_key)
    is_valid = key_manager.verify_signature(message, signature, keypair.public_key)
    
    print(f"\nSignature test: {'✓ Passed' if is_valid else '✗ Failed'}")
    
    # Extract public key bytes for address generation
    pub_key_bytes = key_manager.get_public_key_bytes(keypair.public_key)
    print(f"Public key bytes length: {len(pub_key_bytes)}")


if __name__ == "__main__":
    main()