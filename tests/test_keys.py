"""
Test key generation functionality
"""
import unittest

from dirac_wallet.core.keys import QuantumKeyManager, KeyPair 


class TestKeyGeneration(unittest.TestCase):
    
    def setUp(self):
        self.key_manager = QuantumKeyManager(security_level=3)
    
    def test_generate_keypair(self):
        """Test key pair generation"""
        keypair = self.key_manager.generate_keypair()
        
        self.assertIsInstance(keypair, KeyPair)
        self.assertIn("private_key", keypair.__dict__)
        self.assertIn("public_key", keypair.__dict__)
        self.assertEqual(keypair.algorithm, "dilithium")
        self.assertEqual(keypair.security_level, 3)
    
    def test_key_serialization(self):
        """Test key serialization and deserialization"""
        keypair = self.key_manager.generate_keypair()
        
        # Serialize
        serialized = keypair.serialize()
        self.assertIn("algorithm", serialized)
        self.assertIn("private_key", serialized)
        self.assertIn("public_key", serialized)
        
        # Deserialize
        deserialized = KeyPair.deserialize(serialized)
        self.assertEqual(deserialized.algorithm, keypair.algorithm)
        self.assertEqual(deserialized.security_level, keypair.security_level)
    
    def test_signature_operations(self):
        """Test signing and verification"""
        keypair = self.key_manager.generate_keypair()
        message = b"Test message for signing"
        
        # Sign message
        signature = self.key_manager.sign_message(message, keypair.private_key)
        self.assertIsNotNone(signature)
        
        # Verify signature
        is_valid = self.key_manager.verify_signature(
            message, 
            signature, 
            keypair.public_key
        )
        self.assertTrue(is_valid)
        
        # Verify with wrong message
        wrong_message = b"Different message"
        is_valid_wrong = self.key_manager.verify_signature(
            wrong_message, 
            signature, 
            keypair.public_key
        )
        self.assertFalse(is_valid_wrong)
    
    def test_get_public_key_bytes(self):
        """Test public key bytes extraction"""
        keypair = self.key_manager.generate_keypair()
        pub_key_bytes = self.key_manager.get_public_key_bytes(keypair.public_key)
        
        self.assertIsInstance(pub_key_bytes, bytes)
        self.assertGreater(len(pub_key_bytes), 0)


if __name__ == "__main__":
    unittest.main()