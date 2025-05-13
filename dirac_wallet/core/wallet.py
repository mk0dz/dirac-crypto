"""
Core wallet functionality for Dirac-Wallet
"""
import os
import json
import getpass
from pathlib import Path
from typing import Optional, Dict, Union, List
from dataclasses import dataclass, asdict
from solders.signature import Signature

from .keys import QuantumKeyManager, KeyPair
from .address import AddressDerivation
from .storage import SecureStorage
from ..utils.logger import logger


@dataclass
class WalletInfo:
    """Container for wallet information"""
    address: str
    algorithm: str
    security_level: int
    created_at: str
    version: str = "0.1.3"
    network: str = "devnet"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WalletInfo':
        return cls(**data)


@dataclass
class TransactionRecord:
    """Container for transaction history records"""
    signature: str
    timestamp: str
    amount: float
    sender: str
    recipient: str
    status: str
    fee: float = 0.000005
    type: str = "transfer"
    memo: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TransactionRecord':
        return cls(**data)


class DiracWallet:
    """Main wallet class for Dirac-Wallet"""
    
    def __init__(self, wallet_path: str = None, network: str = "devnet"):
        """Initialize wallet"""
        self.network = network
        self.wallet_path = Path(wallet_path) if wallet_path else self._get_default_path()
        self.key_manager = QuantumKeyManager(security_level=3)
        self.storage = SecureStorage()
        
        # Wallet state
        self.keypair: Optional[KeyPair] = None
        self.solana_keypair: Optional[Keypair] = None
        self.wallet_info: Optional[WalletInfo] = None
        self.solana_address: Optional[str] = None
        self.is_unlocked: bool = False
        self.transaction_history: List[TransactionRecord] = []
        
        logger.info(f"Initialized DiracWallet for {network}")
    
    def _get_default_path(self) -> Path:
        """Get default wallet path from config"""
        from pathlib import Path
        import os
        return Path.home() / ".dirac_wallet" / f"wallet_{self.network}.dwf"
    
    def create(self, password: str = None) -> Dict:
        """Create a new wallet"""
        try:
            # Get password if not provided
            if password is None:
                password = getpass.getpass("Enter password to encrypt your wallet: ")
                confirm_password = getpass.getpass("Confirm password: ")
                if password != confirm_password:
                    raise ValueError("Passwords do not match")
            
            # Generate new keypair
            logger.info("Generating quantum-resistant keypair...")
            self.keypair = self.key_manager.generate_keypair()
            
            # Create hybrid keypair with Solana address
            hybrid_keypair = AddressDerivation.create_quantum_keypair(self.keypair)
            self.solana_keypair = hybrid_keypair["solana_keypair"]
            self.solana_address = hybrid_keypair["solana_address"]
            
            # Create wallet info
            from datetime import datetime
            self.wallet_info = WalletInfo(
                address=self.solana_address,
                algorithm=self.keypair.algorithm,
                security_level=self.keypair.security_level,
                created_at=datetime.now().isoformat(),
                network=self.network
            )
            
            # Initialize empty transaction history
            self.transaction_history = []
            
            # Save wallet
            self._save_encrypted(password)
            self.is_unlocked = True
            
            logger.info(f"Wallet created successfully at {self.wallet_path}")
            return {
                "address": self.solana_address,
                "path": str(self.wallet_path),
                "network": self.network
            }
            
        except Exception as e:
            logger.error(f"Failed to create wallet: {str(e)}")
            raise
    
    def unlock(self, password: str = None) -> bool:
        """Unlock an existing wallet"""
        try:
            # Get password if not provided
            if password is None:
                password = getpass.getpass("Enter wallet password: ")
            
            # Load and decrypt wallet
            if not self.wallet_path.exists():
                raise FileNotFoundError(f"Wallet file not found at {self.wallet_path}")
            
            encrypted_data = self.wallet_path.read_bytes()
            try:
                decrypted_data = self.storage.decrypt(encrypted_data, password)
            except Exception as e:
                # Always raise a ValueError for corrupted data or bad password
                logger.error(f"Tampering detected or invalid password: {str(e)}")
                raise ValueError("Invalid password or corrupted data") from e
                
            wallet_data = json.loads(decrypted_data.decode('utf-8'))
            
            # Restore wallet state
            self.keypair = KeyPair.deserialize(wallet_data["keypair"])
            self.wallet_info = WalletInfo.from_dict(wallet_data["info"])
            
            # Load transaction history if available
            if "transaction_history" in wallet_data:
                self.transaction_history = [
                    TransactionRecord.from_dict(tx) for tx in wallet_data["transaction_history"]
                ]
            else:
                self.transaction_history = []
            
            # Recreate Solana keypair
            hybrid_keypair = AddressDerivation.create_quantum_keypair(self.keypair)
            self.solana_keypair = hybrid_keypair["solana_keypair"]
            self.solana_address = hybrid_keypair["solana_address"]
            
            self.is_unlocked = True
            
            logger.info(f"Wallet unlocked: {self.solana_address}")
            return True
            
        except ValueError as ve:
            # Re-raise ValueErrors to be caught in file tampering tests
            self.is_unlocked = False
            self.keypair = None
            self.solana_keypair = None
            raise
        except Exception as e:
            logger.error(f"Failed to unlock wallet: {str(e)}")
            # Ensure wallet remains locked on failure
            self.is_unlocked = False
            self.keypair = None
            self.solana_keypair = None
            return False
    
    def lock(self):
        """Lock the wallet (clear sensitive data from memory)"""
        self.keypair = None
        self.solana_keypair = None
        self.is_unlocked = False
        logger.info("Wallet locked")
    
    def _save_encrypted(self, password: str):
        """Save wallet to encrypted file"""
        try:
            # Prepare wallet data
            wallet_data = {
                "keypair": self.keypair.serialize(),
                "info": self.wallet_info.to_dict(),
                "transaction_history": [tx.to_dict() for tx in self.transaction_history]
            }
            
            # Encrypt and save
            encrypted_data = self.storage.encrypt(
                json.dumps(wallet_data).encode('utf-8'),
                password
            )
            
            # Ensure directory exists
            self.wallet_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write encrypted file
            self.wallet_path.write_bytes(encrypted_data)
            
            logger.info(f"Wallet saved to {self.wallet_path}")
            
        except Exception as e:
            logger.error(f"Failed to save wallet: {str(e)}")
            raise
    
    def get_info(self) -> Dict:
        """Get wallet information"""
        if not self.wallet_info:
            raise ValueError("Wallet not initialized")
        
        info = self.wallet_info.to_dict()
        info["is_unlocked"] = self.is_unlocked
        info["path"] = str(self.wallet_path)
        return info
    
    def add_transaction(self, tx_record: Union[TransactionRecord, Dict]) -> None:
        """Add a transaction to the wallet's history"""
        if not self.is_unlocked:
            raise ValueError("Wallet must be unlocked to add transactions")
            
        if isinstance(tx_record, dict):
            transaction = TransactionRecord.from_dict(tx_record)
        else:
            transaction = tx_record
            
        self.transaction_history.append(transaction)
        logger.info(f"Added transaction {transaction.signature[:8]}... to history")
    
    def get_transaction_history(self) -> List[Dict]:
        """Get the wallet's transaction history"""
        if not self.is_unlocked:
            raise ValueError("Wallet must be unlocked to access transaction history")
            
        return [tx.to_dict() for tx in self.transaction_history]
    
    def save(self, password: str = None):
        """Save the wallet with current state"""
        if not self.is_unlocked:
            raise ValueError("Wallet must be unlocked to save")
            
        if password is None:
            raise ValueError("Password required to save wallet")
            
        self._save_encrypted(password)
        logger.info("Wallet saved successfully")
    
    def sign_message(self, message: Union[str, bytes]) -> Dict:
        """Sign a message with the wallet's private key"""
        if not self.is_unlocked:
            raise ValueError("Wallet is locked")
        
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        signature = self.key_manager.sign_message(message, self.keypair.private_key)
        return signature
    
    def sign_solana_transaction(self, transaction) -> Signature:
        """Sign a Solana transaction with the Solana keypair"""
        if not self.is_unlocked:
            raise ValueError("Wallet is locked")
        
        # Get the message bytes
        message_bytes = bytes(transaction.message)
        
        # Sign with Solana keypair
        signature = self.solana_keypair.sign_message(message_bytes)
        
        return signature
    
    def verify_signature(self, message: Union[str, bytes], signature: Dict) -> bool:
        """Verify a signature"""
        if not self.is_unlocked:
            raise ValueError("Wallet is locked")
        
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        return self.key_manager.verify_signature(
            message,
            signature,
            self.keypair.public_key
        )