#!/usr/bin/env python3
"""
Basic usage examples for the quantum-resistant hash framework.

This script demonstrates the basic usage of the framework's main components:
- Hash functions (DiracHash and QuantumEnhancedHash)
- Signature schemes (Lamport, SPHINCS, and Dilithium) 
- Key Encapsulation Mechanism (KyberKEM)
"""

import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow importing the project
sys.path.insert(0, str(Path(__file__).parent.parent))

from quantum_hash import DiracHash, QuantumEnhancedHash
from quantum_hash.signatures import LamportSignature, SPHINCSSignature, DilithiumSignature
from quantum_hash.kem import KyberKEM


def demo_hash_functions():
    """Demonstrate the use of hash functions."""
    print("\n=== Hash Functions Demo ===")
    
    # Sample data
    data = b"Hello, quantum world!"
    
    # Using DiracHash with different algorithms
    hash1 = DiracHash.hash(data, algorithm="standard")
    hash2 = DiracHash.hash(data, algorithm="improved")
    hash3 = DiracHash.hash(data, algorithm="grover")
    hash4 = DiracHash.hash(data, algorithm="shor")
    
    print(f"DiracHash (standard): {hash1.hex()}")
    print(f"DiracHash (improved): {hash2.hex()}")
    print(f"DiracHash (grover):   {hash3.hex()}")
    print(f"DiracHash (shor):     {hash4.hex()}")
    
    # Using QuantumEnhancedHash
    hash5 = QuantumEnhancedHash.hash(data)
    print(f"QuantumEnhancedHash:  {hash5.hex()}")
    
    # Custom digest size
    hash6 = DiracHash.hash(data, digest_size=64)
    print(f"DiracHash (64 bytes): {hash6.hex()}")


def demo_signatures():
    """Demonstrate the use of signature schemes."""
    print("\n=== Signature Schemes Demo ===")
    
    # Sample message
    message = b"This message needs to be signed and verified"
    
    # 1. Lamport signatures
    print("\n--- Lamport Signatures ---")
    lamport = LamportSignature()
    
    # Generate a key pair
    private_key, public_key = lamport.generate_keypair()
    print(f"Generated Lamport keypair")
    
    # Sign the message
    signature = lamport.sign(message, private_key)
    print(f"Message signed, signature size: {len(str(signature))} bytes")
    
    # Verify the signature
    is_valid = lamport.verify(message, signature, public_key)
    print(f"Signature valid: {is_valid}")
    
    # 2. SPHINCS signatures
    print("\n--- SPHINCS Signatures ---")
    sphincs = SPHINCSSignature()
    
    # Generate a key pair
    private_key, public_key = sphincs.generate_keypair()
    print(f"Generated SPHINCS keypair")
    
    # Sign the message
    signature = sphincs.sign(message, private_key)
    print(f"Message signed, signature size: {len(str(signature))} bytes")
    
    # Verify the signature
    is_valid = sphincs.verify(message, signature, public_key)
    print(f"Signature valid: {is_valid}")
    
    # 3. Dilithium signatures
    print("\n--- Dilithium Signatures ---")
    dilithium = DilithiumSignature(security_level=2)
    
    # Generate a key pair
    private_key, public_key = dilithium.generate_keypair()
    print(f"Generated Dilithium keypair")
    
    # Sign the message
    signature = dilithium.sign(message, private_key)
    print(f"Message signed, signature size: {len(str(signature))} bytes")
    
    # Verify the signature
    is_valid = dilithium.verify(message, signature, public_key)
    print(f"Signature valid: {is_valid}")


def demo_kem():
    """Demonstrate the use of Key Encapsulation Mechanism."""
    print("\n=== Key Encapsulation Mechanism Demo ===")
    
    # Create a KEM instance
    kem = KyberKEM(security_level=3)  # Kyber-768
    
    # Generate key pair
    public_key, private_key = kem.generate_keypair()
    print(f"Generated Kyber keypair")
    
    # Encapsulate a shared secret
    ciphertext, shared_secret_1 = kem.encapsulate(public_key)
    print(f"Encapsulated shared secret, ciphertext size: {len(ciphertext)} bytes")
    
    # Decapsulate to get the same shared secret
    shared_secret_2 = kem.decapsulate(ciphertext, private_key)
    
    # Verify both parties have the same shared secret
    secrets_match = shared_secret_1 == shared_secret_2
    print(f"Shared secrets match: {secrets_match}")
    print(f"Shared secret: {shared_secret_1.hex()[:16]}...")


def main():
    """Run all demos."""
    print("Quantum-Resistant Hash Framework - Usage Examples")
    
    demo_hash_functions()
    demo_signatures()
    demo_kem()
    
    print("\nAll demos completed successfully!")


if __name__ == "__main__":
    main() 