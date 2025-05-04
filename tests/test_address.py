"""
Test address derivation functionality
"""
import unittest
import re
from dirac_wallet.core.keys import QuantumKeyManager, KeyPair
from dirac_wallet.core.address import AddressDerivation


class TestAddressDerivation(unittest.TestCase):
    
    def setUp(self):
        self.key_manager = QuantumKeyManager(security_level=3)
    
    def test_derive_solana_address(self):
        """Test Solana address derivation from quantum public key"""
        # Generate a quantum keypair
        keypair = self.key_manager.generate_keypair()
        pub_key_bytes = self.key_manager.get_public_key_bytes(keypair.public_key)
        
        # Derive Solana address
        address = AddressDerivation.derive_solana_address(pub_key_bytes)
        
        # Verify address format (Solana addresses are base58 strings)
        self.assertIsInstance(address, str)
        self.assertGreater(len(address), 32)  # Solana addresses are typically 32-44 chars
        self.assertLess(len(address), 45)
        
        # Verify it's valid base58
        self.assertTrue(re.match(r'^[1-9A-HJ-NP-Za-km-z]+$', address))
    
    def test_deterministic_address_generation(self):
        """Test that same public key generates same address"""
        keypair = self.key_manager.generate_keypair()
        pub_key_bytes = self.key_manager.get_public_key_bytes(keypair.public_key)
        
        # Generate address twice
        address1 = AddressDerivation.derive_solana_address(pub_key_bytes)
        address2 = AddressDerivation.derive_solana_address(pub_key_bytes)
        
        # Should be identical
        self.assertEqual(address1, address2)
    
    def test_create_quantum_keypair(self):
        """Test hybrid quantum-Solana keypair creation"""
        keypair = self.key_manager.generate_keypair()
        hybrid = AddressDerivation.create_quantum_keypair(keypair)
        
        # Verify structure
        self.assertIn("quantum_keypair", hybrid)
        self.assertIn("solana_address", hybrid)
        self.assertIn("keypair_info", hybrid)
        
        # Verify keypair info
        info = hybrid["keypair_info"]
        self.assertEqual(info["algorithm"], "dilithium")
        self.assertEqual(info["security_level"], 3)
        self.assertIn("public_key_size", info)
        self.assertEqual(info["address_type"], "quantum_derived")
    
    def test_verify_address_mapping(self):
        """Test address mapping verification"""
        keypair = self.key_manager.generate_keypair()
        hybrid = AddressDerivation.create_quantum_keypair(keypair)
        
        # Verify correct address mapping
        is_valid = AddressDerivation.verify_address_mapping(
            keypair, 
            hybrid["solana_address"]
        )
        self.assertTrue(is_valid)
        
        # Verify incorrect address mapping
        wrong_address = "WrongAddress123456789"
        is_valid_wrong = AddressDerivation.verify_address_mapping(
            keypair, 
            wrong_address
        )
        self.assertFalse(is_valid_wrong)
    
    def test_different_keypairs_different_addresses(self):
        """Test that different keypairs generate different addresses"""
        keypair1 = self.key_manager.generate_keypair()
        keypair2 = self.key_manager.generate_keypair()
        
        hybrid1 = AddressDerivation.create_quantum_keypair(keypair1)
        hybrid2 = AddressDerivation.create_quantum_keypair(keypair2)
        
        self.assertNotEqual(hybrid1["solana_address"], hybrid2["solana_address"])


if __name__ == "__main__":
    unittest.main()