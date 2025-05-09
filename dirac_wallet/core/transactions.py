"""
Transaction handling for Dirac-Wallet with quantum-resistant signatures
"""
import json
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.hash import Hash
from solders.transaction import Transaction
from solders.keypair import Keypair
from solders.system_program import transfer, TransferParams, ID as SYSTEM_PROGRAM_ID
from decimal import Decimal
from solders.signature import Signature

from .wallet import DiracWallet
from ..utils.logger import logger
from quantum_hash import DiracHash


@dataclass
class TransactionInfo:
    """Container for transaction information"""
    signature: Dict  # Quantum signature
    raw_transaction: bytes
    transaction_id: Optional[str] = None
    status: str = "pending"
    blockhash: Optional[str] = None
    amount: Optional[int] = None
    recipient: Optional[str] = None
    timestamp: Optional[str] = None


class QuantumTransaction:
    """Handles quantum-resistant transaction signing for Solana"""
    
    def __init__(self, wallet: DiracWallet):
        """Initialize with a DiracWallet instance"""
        self.wallet = wallet
        self.instructions: List[Instruction] = []
        self.fee_payer = Pubkey.from_string(wallet.solana_address)
        self.recent_blockhash: Optional[Hash] = None
        
        logger.debug("Initialized QuantumTransaction")
    
    def add_instruction(self, instruction: Instruction):
        """Add instruction to transaction"""
        self.instructions.append(instruction)
        logger.debug(f"Added instruction to transaction: {instruction.program_id}")
    
    def create_transfer(self, recipient: str, amount: int):
        """Create a transfer instruction"""
        # Convert recipient to Pubkey
        recipient_pubkey = Pubkey.from_string(recipient)
        
        # Create transfer instruction using system program
        instruction = transfer(
            TransferParams(
                from_pubkey=self.fee_payer,
                to_pubkey=recipient_pubkey,
                lamports=amount
            )
        )
        
        self.instructions.append(instruction)
        
    def build_message(self) -> Message:
        """Build transaction message"""
        if not self.recent_blockhash:
            raise ValueError("Recent blockhash not set")
            
        # Create message
        message = Message.new_with_blockhash(
            self.instructions,
            self.fee_payer,
            self.recent_blockhash
        )
        
        return message
    
    def sign_transaction(self, recent_blockhash: Union[str, Hash] = None) -> TransactionInfo:
        """Sign transaction with quantum-resistant signature"""
        try:
            if not self.wallet.is_unlocked:
                raise ValueError("Wallet is locked")
            
            # Convert blockhash if needed
            if isinstance(recent_blockhash, str):
                blockhash = Hash.from_string(recent_blockhash)
            else:
                blockhash = recent_blockhash
            
            if not blockhash:
                raise ValueError("Recent blockhash required")
            
            # Build message
            message = self.build_message()
            
            # We can't use standard Transaction.sign since we're using quantum signatures
            # Instead, serialize manually
            
            # Convert message to bytes using bytes() function
            message_bytes = bytes(message)
            
            # For custom format with blockhash, append the blockhash bytes
            message_with_blockhash = message_bytes + bytes(blockhash)
            
            # Hash the message for signing
            message_to_sign = DiracHash.hash(message_with_blockhash, digest_size=32, algorithm="improved")
            
            # Sign with quantum-resistant signature
            quantum_signature = self.wallet.key_manager.sign_message(
                message_to_sign,
                self.wallet.keypair.private_key
            )
            
            # Create transaction info
            transaction_info = TransactionInfo(
                signature=quantum_signature,
                raw_transaction=message_with_blockhash,
                blockhash=str(blockhash),
                amount=self._get_transfer_amount(),
                recipient=self._get_transfer_recipient(),
                timestamp=self._get_current_time()
            )
            
            logger.info("Transaction signed successfully with quantum signature")
            return transaction_info
            
        except Exception as e:
            logger.error(f"Failed to sign transaction: {str(e)}")
            raise
    
    def _get_transfer_amount(self) -> Optional[int]:
        """Extract transfer amount from instructions"""
        for instruction in self.instructions:
            if str(instruction.program_id) == '11111111111111111111111111111111':  # System program
                try:
                    # Extract amount from instruction data
                    # This is a simplified extraction for transfer instructions
                    if len(instruction.data) >= 12:
                        # First 4 bytes is instruction type, next 8 bytes is lamports
                        amount_bytes = instruction.data[4:12]
                        return int.from_bytes(amount_bytes, byteorder='little')
                except:
                    pass
        return None
    
    def _get_transfer_recipient(self) -> Optional[str]:
        """Extract recipient from instructions"""
        for instruction in self.instructions:
            if str(instruction.program_id) == '11111111111111111111111111111111':  # System program
                if len(instruction.accounts) >= 2:
                    # Second account in transfer is recipient
                    return str(instruction.accounts[1].pubkey)
        return None
    
    def _get_current_time(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def prepare_for_broadcast(self, blockhash: str) -> Tuple[bytes, Dict]:
        """Prepare transaction for broadcast"""
        if not self.wallet.is_unlocked:
            raise ValueError("Wallet must be unlocked to sign transaction")
            
        # Convert blockhash string to Hash object
        self.recent_blockhash = Hash.from_string(blockhash)
        
        # Build message
        message = self.build_message()
        
        # Create transaction
        transaction = Transaction.new_unsigned(message)
        
        # Get message bytes for quantum signing
        message_bytes = bytes(message)
        
        # Sign with quantum signature
        quantum_signature = self.wallet.sign_message(message_bytes)
        
        # Add Solana signature
        solana_signature = self.wallet.sign_solana_transaction(transaction)
        transaction.signatures = [solana_signature]
        
        # Calculate transaction hash using DiracHash
        tx_hash = DiracHash.hash(message_bytes, digest_size=32, algorithm="improved")
        
        # Prepare metadata with all necessary information
        metadata = {
            "signature": quantum_signature,
            "signature_algorithm": "dilithium",
            "security_level": 3,
            "solana_signature": str(solana_signature),
            "transaction_hash": str(Hash.from_bytes(tx_hash)),
            "public_key": str(self.wallet.keypair.public_key),
            "message_hash": str(Hash.from_bytes(DiracHash.hash(message_bytes, digest_size=32, algorithm="improved"))),
            "blockhash": blockhash,
            "fee_payer": str(self.fee_payer)
        }
        
        # Serialize transaction with proper format
        raw_tx = bytes(transaction)
        
        return raw_tx, metadata
    
    @staticmethod
    def verify_quantum_signature(
        raw_transaction: bytes,
        signature_metadata: Dict,
        wallet: DiracWallet = None
    ) -> bool:
        """
        Verify a quantum signature independently
        Used for off-chain verification of quantum signatures
        """
        try:
            # Extract data
            quantum_signature = signature_metadata["signature"]
            public_key = signature_metadata["public_key"]
            
            # Extract message from transaction
            transaction = Transaction.from_bytes(raw_transaction)
            message_bytes = bytes(transaction.message)
            
            # Verify signature
            if wallet:
                key_manager = wallet.key_manager
            else:
                from .keys import QuantumKeyManager
                key_manager = QuantumKeyManager(
                    security_level=signature_metadata.get("security_level", 3)
                )
            
            is_valid = key_manager.verify_signature(
                message_bytes,
                quantum_signature,
                public_key
            )
            
            logger.debug(f"Quantum signature verification: {is_valid}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Failed to verify quantum signature: {str(e)}")
            return False