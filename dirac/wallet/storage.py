"""
File storage operations for wallet data.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from dirac.utils.encoding import ensure_json_serializable

class WalletStorage:
    """Manages file storage for wallet data."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize wallet storage with an optional custom directory."""
        self.wallet_dir = base_dir or os.path.join(os.path.expanduser("~"), ".dirac-wallet")
        self.tx_history_dir = os.path.join(self.wallet_dir, "transactions")
        self.backup_dir = os.path.join(self.wallet_dir, "backups")
        
        # Create necessary directories
        os.makedirs(self.wallet_dir, exist_ok=True)
        os.makedirs(self.tx_history_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def save_wallet(self, name: str, wallet_data: Dict[str, Any]) -> str:
        """Save wallet data to a file."""
        wallet_path = os.path.join(self.wallet_dir, f"{name}.json")
        
        # Ensure data is JSON serializable
        serializable_data = ensure_json_serializable(wallet_data)
        
        # Save wallet data
        with open(wallet_path, "w") as f:
            json.dump(serializable_data, f, indent=2)
        
        # Create transaction history file if it doesn't exist
        tx_history_path = os.path.join(self.tx_history_dir, f"{name}.json")
        if not os.path.exists(tx_history_path):
            with open(tx_history_path, "w") as f:
                json.dump({"transactions": []}, f, indent=2)
        
        return wallet_path
    
    def load_wallet(self, name: str) -> Dict[str, Any]:
        """Load wallet data from a file."""
        wallet_path = os.path.join(self.wallet_dir, f"{name}.json")
        
        if not os.path.exists(wallet_path):
            raise FileNotFoundError(f"Wallet {name} not found.")
        
        with open(wallet_path, "r") as f:
            wallet_data = json.load(f)
        
        return wallet_data
    
    def list_wallets(self) -> List[Dict[str, Any]]:
        """List all available wallets with basic metadata."""
        wallets = []
        
        for filename in os.listdir(self.wallet_dir):
            if filename.endswith(".json"):
                wallet_path = os.path.join(self.wallet_dir, filename)
                wallet_name = filename[:-5]  # Remove .json extension
                
                try:
                    with open(wallet_path, "r") as f:
                        wallet_data = json.load(f)
                    
                    # Extract essential metadata
                    wallets.append({
                        "name": wallet_name,
                        "address": wallet_data.get("address", "Unknown"),
                        "solana_address": wallet_data.get("solana_address", "Unknown"),
                        "algorithm": wallet_data.get("algorithm", {}).get("signature", "Unknown"),
                        "created_at": wallet_data.get("metadata", {}).get("created_at")
                    })
                except Exception as e:
                    # If there's an error reading the wallet, include basic info
                    wallets.append({
                        "name": wallet_name,
                        "status": "Error reading wallet data",
                        "error": str(e)
                    })
        
        return wallets
    
    def create_backup(self, name: str, wallet_data: Dict[str, Any]) -> str:
        """Create a backup of wallet data."""
        backup_path = os.path.join(self.backup_dir, f"{name}_backup_{int(time.time())}.json")
        
        # Ensure data is JSON serializable
        serializable_data = ensure_json_serializable(wallet_data)
        
        with open(backup_path, "w") as f:
            json.dump(serializable_data, f, indent=2)
        
        return backup_path
    
    def list_backups(self, name: str) -> List[Dict[str, Any]]:
        """List all backups for a specific wallet."""
        backups = []
        prefix = f"{name}_backup_"
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith(prefix) and filename.endswith(".json"):
                backup_path = os.path.join(self.backup_dir, filename)
                
                # Extract timestamp from filename
                try:
                    timestamp_str = filename[len(prefix):-5]  # Remove prefix and .json extension
                    timestamp = int(timestamp_str)
                    
                    backups.append({
                        "path": backup_path,
                        "timestamp": timestamp,
                        "size": os.path.getsize(backup_path)
                    })
                except ValueError:
                    # If timestamp parsing fails, include basic info
                    backups.append({
                        "path": backup_path,
                        "filename": filename,
                        "size": os.path.getsize(backup_path)
                    })
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        return backups
    
    def get_transaction_history(self, name: str) -> List[Dict[str, Any]]:
        """Load transaction history for a wallet."""
        tx_history_path = os.path.join(self.tx_history_dir, f"{name}.json")
        
        if not os.path.exists(tx_history_path):
            return []
        
        with open(tx_history_path, "r") as f:
            data = json.load(f)
        
        return data.get("transactions", [])
    
    def save_transaction(self, name: str, transaction: Dict[str, Any]) -> None:
        """Save a transaction to the transaction history."""
        tx_history_path = os.path.join(self.tx_history_dir, f"{name}.json")
        
        # Load existing transactions
        if os.path.exists(tx_history_path):
            with open(tx_history_path, "r") as f:
                data = json.load(f)
            transactions = data.get("transactions", [])
        else:
            transactions = []
        
        # Add new transaction
        transactions.append(transaction)
        
        # Save updated history
        with open(tx_history_path, "w") as f:
            json.dump({"transactions": transactions}, f, indent=2)
    
    def export_wallet(self, name: str, output_dir: str, include_private_key: bool = False) -> str:
        """Export wallet to a file in the specified directory."""
        # Load wallet data
        wallet_data = self.load_wallet(name)
        
        # Remove private key if not including it
        if not include_private_key and "private_key" in wallet_data:
            wallet_data = wallet_data.copy()
            wallet_data.pop("private_key")
            if "backup" in wallet_data and "private_key" in wallet_data["backup"]:
                wallet_data["backup"] = wallet_data["backup"].copy()
                wallet_data["backup"].pop("private_key")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create export file path
        export_path = os.path.join(output_dir, f"{name}_export.json")
        
        # Save the export
        with open(export_path, "w") as f:
            json.dump(ensure_json_serializable(wallet_data), f, indent=2)
        
        return export_path 