"""
Tests for the Solana integration.
"""

import pytest
import os
import base64
import hashlib

from dirac.crypto import QuantumKeyring
from dirac.solana import convert_to_solana_keypair, convert_from_solana_keypair, SolanaClient
from dirac.wallet import DiracWallet

# Check if Solana libraries are available
try:
    from solders.keypair import Keypair
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False

@pytest.mark.skipif(not SOLANA_AVAILABLE, reason="Solana libraries not available")
def test_solana_keypair_conversion():
    """Test converting between DiracWallet keys and Solana keypairs."""
    # Create a keyring and generate a keypair
    keyring = QuantumKeyring()
    private_key, public_key = keyring.generate_keypair()
    
    # Convert to Solana keypair
    solana_keypair = convert_to_solana_keypair(private_key)
    
    # Check that conversion was successful
    assert solana_keypair is not None
    assert isinstance(solana_keypair, Keypair)
    
    # Convert back to DiracWallet format
    dirac_key = convert_from_solana_keypair(solana_keypair)
    
    # Check that conversion was successful
    assert dirac_key is not None
    assert "algorithm" in dirac_key
    assert "seed" in dirac_key
    assert "security_level" in dirac_key

def test_solana_client_initialization():
    """Test initializing the Solana client."""
    # Create client with default network (testnet)
    client = SolanaClient()
    assert client.network == "testnet"
    assert "api.testnet.solana.com" in client.rpc_url
    
    # Create client with custom network
    client = SolanaClient(network="devnet")
    assert client.network == "devnet"
    assert "api.devnet.solana.com" in client.rpc_url

@pytest.mark.skipif(not SOLANA_AVAILABLE, reason="Solana libraries not available")
def test_solana_client_is_available():
    """Test checking if Solana integration is available."""
    client = SolanaClient()
    assert client.is_available() == SOLANA_AVAILABLE

@pytest.mark.skipif(not SOLANA_AVAILABLE, reason="Solana libraries not available")
def test_wallet_solana_address():
    """Test that created wallets have a Solana address."""
    # Create a temporary wallet
    wallet = DiracWallet()
    wallet_name = "test_solana_address"
    
    try:
        wallet.create_wallet(wallet_name, overwrite=True)
        
        # Check that Solana address exists
        assert wallet.solana_address is not None
        assert isinstance(wallet.solana_address, str)
        assert len(wallet.solana_address) > 30  # Solana addresses are typically 32-44 chars
    finally:
        # Clean up
        try:
            wallet_path = os.path.join(wallet.storage.wallet_dir, f"{wallet_name}.json")
            if os.path.exists(wallet_path):
                os.remove(wallet_path)
            
            tx_path = os.path.join(wallet.storage.tx_history_dir, f"{wallet_name}.json")
            if os.path.exists(tx_path):
                os.remove(tx_path)
        except:
            pass 