"""
Core wallet functionality for Dirac-Wallet
"""
import os
import json
import getpass
from pathlib import Path
from typing import Optional, Dict, Union
from dataclasses import dataclass, asdict

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
    version: str = "0.1.0"
    network: str = "testnet"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WalletInfo':
        return cls(**data)


class DiracWallet:
    """Main wallet class for Dirac-Wallet"""
    
    def __init__(self, wallet_path: str = None, network: str = "testnet"):
        """Initialize wallet"""
        self.network = network
        self.wallet_path = Path(wallet_path) if wallet_path else self._get_default_path()
        self.key_manager = QuantumKeyManager(security_level=3)
        self.storage = SecureStorage()
        
        # Wallet state
        self.keypair: Optional[KeyPair] = None
        self.wallet_info: Optional[WalletInfo] = None
        self.solana_address: Optional[str] = None
        self.is_unlocked: bool = False
        
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
            decrypted_data = self.storage.decrypt(encrypted_data, password)
            wallet_data = json.loads(decrypted_data.decode('utf-8'))
            
            # Restore wallet state
            self.keypair = KeyPair.deserialize(wallet_data["keypair"])
            self.wallet_info = WalletInfo.from_dict(wallet_data["info"])
            self.solana_address = self.wallet_info.address
            self.is_unlocked = True
            
            logger.info(f"Wallet unlocked: {self.solana_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unlock wallet: {str(e)}")
            # Ensure wallet remains locked on failure
            self.is_unlocked = False
            self.keypair = None
            return False
    
    def lock(self):
        """Lock the wallet (clear sensitive data from memory)"""
        self.keypair = None
        self.is_unlocked = False
        logger.info("Wallet locked")
    
    def _save_encrypted(self, password: str):
        """Save wallet to encrypted file"""
        try:
            # Prepare wallet data
            wallet_data = {
                "keypair": self.keypair.serialize(),
                "info": self.wallet_info.to_dict()
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
    
    def sign_message(self, message: Union[str, bytes]) -> Dict:
        """Sign a message with the wallet's private key"""
        if not self.is_unlocked:
            raise ValueError("Wallet is locked")
        
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        signature = self.key_manager.sign_message(message, self.keypair.private_key)
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