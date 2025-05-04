#!/usr/bin/env python3
"""
Demonstrate quantum key generation and Solana address derivation
"""
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dirac_wallet.core.keys import QuantumKeyManager
from dirac_wallet.core.address import AddressDerivation
from dirac_wallet.utils.logger import logger


def main():
    # Initialize key manager with security level 3
    logger.info("Initializing Quantum Key Manager...")
    key_manager = QuantumKeyManager(security_level=3)
    
    # Generate a new quantum-resistant key pair
    logger.info("Generating quantum-resistant key pair...")
    keypair = key_manager.generate_keypair()
    
    # Create hybrid keypair with Solana address
    hybrid_keypair = AddressDerivation.create_quantum_keypair(keypair)
    
    # Display information
    print("\n=== Quantum-Solana Hybrid Keypair ===")
    print(f"Algorithm: {hybrid_keypair['keypair_info']['algorithm']}")
    print(f"Security Level: {hybrid_keypair['keypair_info']['security_level']}")
    print(f"Public Key Size: {hybrid_keypair['keypair_info']['public_key_size']} bytes")
    print(f"Solana Address: {hybrid_keypair['solana_address']}")
    
    # Verify address mapping
    is_valid = AddressDerivation.verify_address_mapping(
        keypair, 
        hybrid_keypair['solana_address']
    )
    print(f"\nAddress mapping verified: {'✓ Passed' if is_valid else '✗ Failed'}")
    
    # Test signing with the quantum keypair
    message = b"Test transaction data"
    signature = key_manager.sign_message(message, keypair.private_key)
    is_valid_signature = key_manager.verify_signature(
        message, 
        signature, 
        keypair.public_key
    )
    print(f"Signature test: {'✓ Passed' if is_valid_signature else '✗ Failed'}")


if __name__ == "__main__":
    main()