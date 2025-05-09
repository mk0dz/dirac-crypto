"""
Test wallet operations
"""
import unittest
import tempfile
import shutil
from pathlib import Path
from dirac_wallet.core.wallet import DiracWallet


class TestWallet(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directory for test wallets
        self.test_dir = tempfile.mkdtemp()
        self.wallet_path = Path(self.test_dir) / "test_wallet.dwf"
        self.test_password = "test_password_123"
    
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_create_wallet(self):
        """Test wallet creation"""
        wallet = DiracWallet(str(self.wallet_path))
        result = wallet.create(self.test_password)
        
        # Verify creation result
        self.assertIn("address", result)
        self.assertIn("path", result)
        self.assertIn("network", result)
        self.assertEqual(result["network"], "testnet")
        
        # Verify wallet file exists
        self.assertTrue(self.wallet_path.exists())
    
    def test_unlock_wallet(self):
        """Test wallet unlocking"""
        # Create wallet first
        wallet = DiracWallet(str(self.wallet_path))
        create_result = wallet.create(self.test_password)
        
        # Lock it (remove from memory)
        wallet.lock()
        
        # Unlock it
        unlock_result = wallet.unlock(self.test_password)
        self.assertTrue(unlock_result)
        self.assertTrue(wallet.is_unlocked)
        self.assertEqual(wallet.solana_address, create_result["address"])
    
    def test_unlock_wrong_password(self):
        """Test wallet unlocking with wrong password"""
        # Create wallet
        wallet = DiracWallet(str(self.wallet_path))
        wallet.create(self.test_password)
        
        # Try to unlock with wrong password
        wrong_password = "wrong_password"
        
        # Now expect a ValueError to be raised with wrong password
        with self.assertRaises(ValueError):
            wallet.unlock(wrong_password)
            
        # Verify wallet remains locked
        self.assertFalse(wallet.is_unlocked)
    
    def test_wallet_info(self):
        """Test getting wallet information"""
        wallet = DiracWallet(str(self.wallet_path))
        wallet.create(self.test_password)
        
        info = wallet.get_info()
        self.assertIn("address", info)
        self.assertIn("algorithm", info)
        self.assertIn("security_level", info)
        self.assertIn("created_at", info)
        self.assertIn("network", info)
        self.assertIn("is_unlocked", info)
        self.assertEqual(info["algorithm"], "dilithium")
        self.assertEqual(info["security_level"], 3)
        self.assertTrue(info["is_unlocked"])
    
    def test_sign_message(self):
        """Test message signing"""
        wallet = DiracWallet(str(self.wallet_path))
        wallet.create(self.test_password)
        
        message = "Test message for signing"
        signature = wallet.sign_message(message)
        self.assertIsNotNone(signature)
        
        # Verify signature
        is_valid = wallet.verify_signature(message, signature)
        self.assertTrue(is_valid)
        
        # Test with wrong message
        wrong_message = "Different message"
        is_valid_wrong = wallet.verify_signature(wrong_message, signature)
        self.assertFalse(is_valid_wrong)
    
    def test_sign_message_locked(self):
        """Test signing with locked wallet raises error"""
        wallet = DiracWallet(str(self.wallet_path))
        wallet.create(self.test_password)
        wallet.lock()
        
        with self.assertRaises(ValueError):
            wallet.sign_message("Should fail")
    
    def test_different_networks(self):
        """Test creating wallets for different networks"""
        devnet_path = Path(self.test_dir) / "devnet.dwf"
        testnet_path = Path(self.test_dir) / "testnet.dwf"
        
        # Create devnet wallet
        devnet_wallet = DiracWallet(str(devnet_path), network="devnet")
        devnet_result = devnet_wallet.create(self.test_password)
        self.assertEqual(devnet_result["network"], "devnet")
        
        # Create testnet wallet  
        testnet_wallet = DiracWallet(str(testnet_path), network="testnet")
        testnet_result = testnet_wallet.create(self.test_password)
        self.assertEqual(testnet_result["network"], "testnet")
        
        # Verify they have different addresses
        self.assertNotEqual(devnet_result["address"], testnet_result["address"])


if __name__ == "__main__":
    unittest.main()