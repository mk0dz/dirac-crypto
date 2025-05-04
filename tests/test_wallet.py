"""
Tests for the wallet components.
"""

import pytest
import os
import tempfile
import json
import time
from pathlib import Path

from dirac.wallet import DiracWallet, Transaction
from dirac.crypto import QuantumKeyring
from dirac.wallet.storage import WalletStorage

@pytest.fixture
def temp_wallet_dir():
    """Create a temporary wallet directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up is handled by the system

@pytest.fixture
def wallet_storage(temp_wallet_dir):
    """Create a wallet storage instance with a temporary directory."""
    return WalletStorage(temp_wallet_dir)

@pytest.fixture
def wallet(wallet_storage):
    """Create a wallet instance with the test storage."""
    keyring = QuantumKeyring()
    return DiracWallet(keyring=keyring, network="testnet", storage=wallet_storage)

def test_transaction_creation():
    """Test Transaction object creation and serialization."""
    tx = Transaction(
        tx_id="test_tx_123",
        sender="sender_address",
        recipient="recipient_address",
        amount=0.5,
        timestamp=1234567890.0,
        status="pending"
    )
    
    # Test properties
    assert tx.tx_id == "test_tx_123"
    assert tx.sender == "sender_address"
    assert tx.recipient == "recipient_address"
    assert tx.amount == 0.5
    assert tx.timestamp == 1234567890.0
    assert tx.status == "pending"
    
    # Test to_dict serialization
    tx_dict = tx.to_dict()
    assert tx_dict["tx_id"] == "test_tx_123"
    assert tx_dict["sender"] == "sender_address"
    assert tx_dict["recipient"] == "recipient_address"
    assert tx_dict["amount"] == 0.5
    assert tx_dict["timestamp"] == 1234567890.0
    assert tx_dict["status"] == "pending"
    
    # Test from_dict deserialization
    tx2 = Transaction.from_dict(tx_dict)
    assert tx2.tx_id == tx.tx_id
    assert tx2.sender == tx.sender
    assert tx2.recipient == tx.recipient
    assert tx2.amount == tx.amount
    assert tx2.timestamp == tx.timestamp
    assert tx2.status == tx.status

def test_wallet_creation(wallet):
    """Test wallet creation."""
    wallet_name = "test_wallet"
    address = wallet.create_wallet(wallet_name)
    
    # Check that address is returned
    assert isinstance(address, str)
    
    # Check that wallet was loaded
    assert wallet.current_wallet == wallet_name
    assert wallet.address == address
    assert wallet.solana_address is not None
    
    # Check that wallet file was created
    wallet_path = os.path.join(wallet.storage.wallet_dir, f"{wallet_name}.json")
    assert os.path.exists(wallet_path)
    
    # Check wallet content
    with open(wallet_path, "r") as f:
        wallet_data = json.load(f)
    
    assert wallet_data["name"] == wallet_name
    assert wallet_data["address"] == address
    assert "public_key" in wallet_data
    assert "private_key" in wallet_data
    assert "metadata" in wallet_data
    assert "backup" in wallet_data

def test_wallet_loading(wallet):
    """Test wallet loading."""
    # Create a wallet first
    wallet_name = "load_test_wallet"
    original_address = wallet.create_wallet(wallet_name)
    
    # Reset wallet state
    wallet.current_wallet = None
    wallet.address = None
    wallet.solana_address = None
    
    # Load the wallet
    loaded_address = wallet.load_wallet(wallet_name)
    
    # Check that the correct wallet was loaded
    assert loaded_address == original_address
    assert wallet.current_wallet == wallet_name
    assert wallet.address == original_address

def test_wallet_listing(wallet):
    """Test listing available wallets."""
    # Create a couple wallets
    wallet.create_wallet("wallet1")
    wallet.create_wallet("wallet2")
    
    # List wallets
    wallets = wallet.list_wallets()
    
    # Check result
    assert len(wallets) >= 2
    wallet_names = [w["name"] for w in wallets]
    assert "wallet1" in wallet_names
    assert "wallet2" in wallet_names

def test_wallet_export_import(wallet, temp_wallet_dir):
    """Test exporting and importing wallets."""
    # Create a wallet
    wallet_name = "export_test_wallet"
    original_address = wallet.create_wallet(wallet_name)
    
    # Export wallet (without private key)
    export_dir = os.path.join(temp_wallet_dir, "exports")
    export_path = wallet.export_wallet(wallet_name, export_dir, include_private_key=False)
    
    # Check that export file exists
    assert os.path.exists(export_path)
    
    # Check that export doesn't contain private key
    with open(export_path, "r") as f:
        export_data = json.load(f)
    assert "private_key" not in export_data
    
    # Import wallet with a different name
    imported_name = "imported_wallet"
    wallet.import_wallet(export_path, imported_name)
    
    # Check the imported wallet
    wallet.load_wallet(imported_name)
    assert wallet.address == original_address 