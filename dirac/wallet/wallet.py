"""
Core wallet implementation.
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from dirac.crypto import QuantumKeyring
from dirac.wallet.transaction import Transaction
from dirac.wallet.storage import WalletStorage
from dirac.utils.address import get_solana_address_from_bytes

# Try to import Solana libraries, fallback to mock implementations if not available
try:
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False

class DiracWallet:
    """Enhanced implementation of a quantum-resistant wallet."""
    
    def __init__(self, keyring=None, network="testnet", storage=None):
        self.keyring = keyring or QuantumKeyring()
        self.storage = storage or WalletStorage()
        
        # Set network and RPC URL
        self.network = network
        self.rpc_url = {
            "mainnet": "https://api.mainnet-beta.solana.com",
            "testnet": "https://api.testnet.solana.com",
            "devnet": "https://api.devnet.solana.com",
            "local": "http://localhost:8899"
        }.get(network, "https://api.testnet.solana.com")
        
        # Initialize Solana client if available
        self.solana_client = Client(self.rpc_url) if SOLANA_AVAILABLE else None
        
        # Current loaded wallet state
        self.current_wallet = None
        self.private_key = None
        self.public_key = None
        self.address = None
        self.solana_address = None
    
    def create_wallet(self, name: str, overwrite: bool = False, **kwargs) -> str:
        """Create a new wallet."""
        wallet_path = os.path.join(self.storage.wallet_dir, f"{name}.json")
        
        if os.path.exists(wallet_path) and not overwrite:
            raise FileExistsError(f"Wallet {name} already exists. Use overwrite=True to force.")
        
        # Generate main keypair
        private_key, public_key = self.keyring.generate_keypair()
        
        # Generate backup keypair with different algorithm
        backup_algo = "dilithium" if self.keyring.signature_algorithm != "dilithium" else "sphincs"
        backup_keyring = QuantumKeyring(signature_algorithm=backup_algo, 
                                        hash_algorithm=self.keyring.hash_algorithm,
                                        security_level=self.keyring.security_level)
        backup_private_key, backup_public_key = backup_keyring.generate_keypair()
        
        # Derive addresses
        address = self.keyring.derive_address(public_key)
        
        # Generate Solana-compatible address
        solana_address = get_solana_address_from_bytes(public_key.get("key", b""))
        
        # Create wallet data with metadata
        wallet_data = {
            "name": name,
            "address": address,
            "solana_address": solana_address,
            "public_key": public_key,
            "private_key": private_key,
            "algorithm": {
                "signature": self.keyring.signature_algorithm,
                "hash": self.keyring.hash_algorithm,
                "security_level": self.keyring.security_level,
            },
            "backup": {
                "public_key": backup_public_key,
                "private_key": backup_private_key,
                "algorithm": backup_algo
            },
            "metadata": {
                "created_at": time.time(),
                "last_accessed": time.time(),
                "version": "1.0.0",
                "network": self.network
            }
        }
        
        # Save wallet and create backup
        self.storage.save_wallet(name, wallet_data)
        self.storage.create_backup(name, wallet_data)
        
        # Load the new wallet
        self.load_wallet(name)
        
        return address
    
    def load_wallet(self, name: str) -> str:
        """Load a wallet from file."""
        # Load wallet data
        wallet_data = self.storage.load_wallet(name)
        
        # Set wallet state
        self.current_wallet = name
        self.private_key = wallet_data.get("private_key")
        self.public_key = wallet_data.get("public_key")
        self.address = wallet_data.get("address")
        self.solana_address = wallet_data.get("solana_address")
        
        # Set network from wallet metadata
        if "metadata" in wallet_data and "network" in wallet_data["metadata"]:
            self.network = wallet_data["metadata"]["network"]
            self.rpc_url = {
                "mainnet": "https://api.mainnet-beta.solana.com",
                "testnet": "https://api.testnet.solana.com",
                "devnet": "https://api.devnet.solana.com",
                "local": "http://localhost:8899"
            }.get(self.network, "https://api.testnet.solana.com")
            
            # Update Solana client with new RPC URL
            if SOLANA_AVAILABLE:
                self.solana_client = Client(self.rpc_url)
        
        # Update last accessed time
        wallet_data["metadata"]["last_accessed"] = time.time()
        self.storage.save_wallet(name, wallet_data)
        
        return self.address
    
    def get_balance(self) -> float:
        """Get wallet balance."""
        if not self.current_wallet:
            raise ValueError("No wallet loaded. Use load_wallet first.")
        
        if not SOLANA_AVAILABLE or not self.solana_client:
            # Return mock balance if Solana is not available
            return 0.0
        
        try:
            # Attempt to get balance from Solana RPC
            response = self.solana_client.get_balance(self.solana_address)
            
            # Handle different response formats
            try:
                # For newer versions where response is a GetBalanceResp object
                lamports = response.value
            except (AttributeError, TypeError):
                try:
                    # Fall back to dictionary access for older versions
                    lamports = response["result"]["value"]
                except (KeyError, TypeError):
                    lamports = 0
            
            # Convert lamports to SOL (1 SOL = 10^9 lamports)
            balance = lamports / 1_000_000_000
            return balance
        except Exception as e:
            # Return 0 on error
            print(f"Balance check error: {str(e)}")
            return 0.0
    
    def send_transaction(self, recipient: str, amount: float) -> str:
        """Send a transaction."""
        if not self.current_wallet:
            raise ValueError("No wallet loaded. Use load_wallet first.")
        
        if not SOLANA_AVAILABLE or not self.solana_client:
            # Create a mock transaction ID if Solana is not available
            tx_id = hashlib.sha256(f"{self.address}{recipient}{amount}{time.time()}".encode()).hexdigest()
        else:
            # This is a placeholder for actual Solana transaction code
            # In a real implementation, this would create and send a Solana transaction
            tx_id = hashlib.sha256(f"{self.address}{recipient}{amount}{time.time()}".encode()).hexdigest()
        
        # Create transaction record
        tx = Transaction(
            tx_id=tx_id,
            sender=self.address,
            recipient=recipient,
            amount=amount,
            timestamp=time.time(),
            status="pending"
        )
        
        # Save transaction to history
        self._save_transaction(tx)
        
        return tx_id
    
    def _save_transaction(self, tx: Transaction) -> None:
        """Save a transaction to the history."""
        if not self.current_wallet:
            raise ValueError("No wallet loaded. Use load_wallet first.")
        
        # Save to transaction history
        self.storage.save_transaction(self.current_wallet, tx.to_dict())
    
    def get_transaction_history(self) -> List[Transaction]:
        """Get transaction history for the current wallet."""
        if not self.current_wallet:
            raise ValueError("No wallet loaded. Use load_wallet first.")
        
        # Get transactions from storage
        tx_data = self.storage.get_transaction_history(self.current_wallet)
        
        # Convert to Transaction objects
        return [Transaction.from_dict(tx) for tx in tx_data]
    
    def list_wallets(self) -> List[Dict[str, Any]]:
        """List all available wallets."""
        return self.storage.list_wallets()
    
    def export_wallet(self, name: str, output_dir: str, include_private_key: bool = False) -> str:
        """Export a wallet to a file."""
        return self.storage.export_wallet(name, output_dir, include_private_key)
    
    def import_wallet(self, file_path: str, name: Optional[str] = None) -> str:
        """Import a wallet from a file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Import file not found: {file_path}")
        
        # Load wallet data from file
        with open(file_path, "r") as f:
            import_data = json.load(f)
        
        # Determine wallet name
        if name is None:
            name = import_data.get("name", f"imported_{int(time.time())}")
        
        # Check if wallet already exists
        wallet_path = os.path.join(self.storage.wallet_dir, f"{name}.json")
        if os.path.exists(wallet_path):
            raise FileExistsError(f"Wallet with name {name} already exists.")
        
        # Save imported wallet
        self.storage.save_wallet(name, import_data)
        
        # Load the imported wallet
        self.load_wallet(name)
        
        return name
    
    def restore_from_backup(self, name: str, backup_time: Optional[int] = None) -> str:
        """Restore a wallet from backup."""
        # List backups for this wallet
        backups = self.storage.list_backups(name)
        
        if not backups:
            raise FileNotFoundError(f"No backups found for wallet {name}")
        
        # Select the backup to restore
        if backup_time is not None:
            # Find backup with the specified timestamp
            backup = next((b for b in backups if b.get("timestamp") == backup_time), None)
            if backup is None:
                raise ValueError(f"No backup found with timestamp {backup_time}")
        else:
            # Use the most recent backup
            backup = backups[0]
        
        # Load backup data
        with open(backup["path"], "r") as f:
            backup_data = json.load(f)
        
        # Save as the current wallet
        self.storage.save_wallet(name, backup_data)
        
        # Load the restored wallet
        self.load_wallet(name)
        
        return name
    
    def change_network(self, network: str) -> None:
        """Change the network used by the wallet."""
        valid_networks = ["mainnet", "testnet", "devnet", "local"]
        if network not in valid_networks:
            raise ValueError(f"Invalid network. Must be one of {valid_networks}")
        
        # Update network and RPC URL
        self.network = network
        self.rpc_url = {
            "mainnet": "https://api.mainnet-beta.solana.com",
            "testnet": "https://api.testnet.solana.com",
            "devnet": "https://api.devnet.solana.com",
            "local": "http://localhost:8899"
        }.get(network, "https://api.testnet.solana.com")
        
        # Update Solana client if available
        if SOLANA_AVAILABLE:
            self.solana_client = Client(self.rpc_url)
        
        # Update network in loaded wallet if available
        if self.current_wallet:
            wallet_data = self.storage.load_wallet(self.current_wallet)
            if "metadata" in wallet_data:
                wallet_data["metadata"]["network"] = network
                self.storage.save_wallet(self.current_wallet, wallet_data) 