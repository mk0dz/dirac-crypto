"""
Tests for the DiracWallet class.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path

import sys
# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.wallet.wallet import DiracWallet
from src.crypto.keyring import QuantumKeyring


class TestDiracWallet:
    """Test the DiracWallet class."""
    
    @pytest.fixture
    def temp_wallet_dir(self):
        """Create a temporary directory for wallet files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_init(self):
        """Test initialization with default parameters."""
        wallet = DiracWallet()
        assert wallet.client is not None
        assert wallet.keyring is not None
        assert wallet.current_wallet is None
        assert wallet.private_key is None
        assert wallet.public_key is None
        assert wallet.address is None
    
    def test_init_with_custom_parameters(self, temp_wallet_dir):
        """Test initialization with custom parameters."""
        keyring = QuantumKeyring(
            signature_algorithm="dilithium",
            hash_algorithm="dirac_grover",
            security_level=5,
        )
        wallet = DiracWallet(
            keyring=keyring,
            rpc_url="https://api.devnet.solana.com",
            wallet_dir=temp_wallet_dir,
        )
        
        assert wallet.keyring.signature_algorithm == "dilithium"
        assert wallet.keyring.hash_algorithm == "dirac_grover"
        assert wallet.keyring.security_level == 5
        assert wallet.wallet_dir == temp_wallet_dir
        assert "devnet" in wallet.client.endpoint_uri
    
    def test_create_and_load_wallet(self, temp_wallet_dir):
        """Test creating and loading a wallet."""
        wallet = DiracWallet(wallet_dir=temp_wallet_dir)
        
        # Create wallet
        name = "test_wallet"
        address = wallet.create_wallet(name)
        
        # Check that wallet was created
        assert wallet.current_wallet == name
        assert wallet.private_key is not None
        assert wallet.public_key is not None
        assert wallet.address == address
        
        # Check that wallet file exists
        wallet_path = os.path.join(temp_wallet_dir, f"{name}.json")
        assert os.path.exists(wallet_path)
        
        # Create new wallet instance and load the wallet
        new_wallet = DiracWallet(wallet_dir=temp_wallet_dir)
        loaded_address = new_wallet.load_wallet(name)
        
        # Check that wallet was loaded correctly
        assert new_wallet.current_wallet == name
        assert new_wallet.private_key is not None
        assert new_wallet.public_key is not None
        assert new_wallet.address == address
        assert loaded_address == address
    
    def test_create_wallet_already_exists(self, temp_wallet_dir):
        """Test creating a wallet that already exists."""
        wallet = DiracWallet(wallet_dir=temp_wallet_dir)
        
        # Create wallet
        name = "test_wallet"
        wallet.create_wallet(name)
        
        # Try to create again with same name
        with pytest.raises(FileExistsError):
            wallet.create_wallet(name)
        
        # Create with overwrite=True
        address = wallet.create_wallet(name, overwrite=True)
        assert address is not None
    
    def test_load_wallet_not_found(self, temp_wallet_dir):
        """Test loading a wallet that doesn't exist."""
        wallet = DiracWallet(wallet_dir=temp_wallet_dir)
        
        with pytest.raises(FileNotFoundError):
            wallet.load_wallet("nonexistent_wallet")
    
    def test_list_wallets(self, temp_wallet_dir):
        """Test listing all wallets."""
        wallet = DiracWallet(wallet_dir=temp_wallet_dir)
        
        # Create wallets
        wallet.create_wallet("wallet1")
        wallet.create_wallet("wallet2")
        
        # List wallets
        wallets = wallet.list_wallets()
        
        assert len(wallets) == 2
        assert "wallet1" in wallets
        assert "wallet2" in wallets
    
    def test_export_wallet(self, temp_wallet_dir):
        """Test exporting a wallet."""
        wallet = DiracWallet(wallet_dir=temp_wallet_dir)
        
        # Create wallet
        name = "test_wallet"
        wallet.create_wallet(name)
        
        # Create export directory
        export_dir = os.path.join(temp_wallet_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        # Export wallet
        export_path = wallet.export_wallet(name=name, export_path=export_dir)
        
        # Check that exported file exists
        assert os.path.exists(export_path)
        
        # Check that exported file doesn't contain private key
        with open(export_path, "r") as f:
            exported_data = json.load(f)
        
        assert "private_key" not in exported_data
        assert "public_key" in exported_data
        assert "address" in exported_data
    
    def test_import_wallet(self, temp_wallet_dir):
        """Test importing a wallet."""
        wallet = DiracWallet(wallet_dir=temp_wallet_dir)
        
        # Create and export wallet
        original_name = "original_wallet"
        wallet.create_wallet(original_name)
        
        # Create export directory
        export_dir = os.path.join(temp_wallet_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        # Export wallet
        export_path = wallet.export_wallet(name=original_name, export_path=export_dir)
        
        # Import wallet with new name
        import_name = "imported_wallet"
        address = wallet.import_wallet(export_path, name=import_name)
        
        # Check that wallet was imported
        assert wallet.current_wallet == import_name
        assert wallet.address == address
        
        # Verify that wallet file exists
        wallet_path = os.path.join(temp_wallet_dir, f"{import_name}.json")
        assert os.path.exists(wallet_path)
    
    def test_get_balance(self, temp_wallet_dir, monkeypatch):
        """Test getting wallet balance."""
        # This is a simplified test that mocks the RPC call
        from unittest.mock import Mock
        
        wallet = DiracWallet(wallet_dir=temp_wallet_dir)
        
        # Create wallet
        name = "test_wallet"
        wallet.create_wallet(name)
        
        # Mock the get_account_info method
        mock_response = Mock()
        mock_response.value.lamports = 1_000_000_000  # 1 SOL
        
        monkeypatch.setattr(wallet.client, "get_account_info", lambda _: mock_response)
        
        # Get balance
        balance = wallet.get_balance()
        
        assert balance == 1.0  # 1 SOL 