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
from solders.system_program import transfer, TransferParams
from decimal import Decimal

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
        self.recent_blockhash: Optional[Hash] = None
        self.fee_payer: Optional[Pubkey] = None
        
        logger.debug("Initialized QuantumTransaction")
    
    def add_instruction(self, instruction: Instruction):
        """Add instruction to transaction"""
        self.instructions.append(instruction)
        logger.debug(f"Added instruction to transaction: {instruction.program_id}")
    
    def create_transfer(self, to_address: str, amount: int) -> 'QuantumTransaction':
        """Create a SOL transfer transaction"""
        try:
            # Get wallet's quantum address as sender
            sender = Pubkey.from_string(self.wallet.solana_address)
            
            # Parse recipient address
            recipient = Pubkey.from_string(to_address)
            
            # Create transfer instruction
            transfer_instruction = transfer(
                TransferParams(
                    from_pubkey=sender,
                    to_pubkey=recipient,
                    lamports=amount
                )
            )
            
            # Add instruction to transaction
            self.add_instruction(transfer_instruction)
            
            # Set fee payer
            self.fee_payer = sender
            
            logger.info(f"Created transfer transaction: {amount} lamports to {to_address}")
            return self
            
        except Exception as e:
            logger.error(f"Failed to create transfer transaction: {str(e)}")
            raise
    
    def build_message(self) -> Message:
        """Build transaction message"""
        try:
            if not self.instructions:
                raise ValueError("No instructions in transaction")
            
            if not self.fee_payer:
                raise ValueError("Fee payer not set")
            
            # Create message with instructions
            message = Message(
                self.instructions,
                self.fee_payer
            )
            
            logger.debug("Built transaction message")
            return message
            
        except Exception as e:
            logger.error(f"Failed to build message: {str(e)}")
            raise
    
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
    
    def prepare_for_broadcast(self, recent_blockhash: str) -> Tuple[bytes, Dict]:
        """
        Prepare transaction for broadcasting to Solana network
        Returns: (serialized_transaction, quantum_signature_metadata)
        """
        try:
            # Sign the transaction
            tx_info = self.sign_transaction(recent_blockhash)
            
            # Prepare metadata for off-chain quantum signature verification
            signature_metadata = {
                "signature": tx_info.signature,
                "signature_algorithm": "dilithium",
                "security_level": self.wallet.keypair.security_level,
                "public_key": self.wallet.keypair.public_key,
                "transaction_hash": DiracHash.hash(tx_info.raw_transaction).hex()
            }
            
            logger.info("Transaction prepared for broadcast")
            return tx_info.raw_transaction, signature_metadata
            
        except Exception as e:
            logger.error(f"Failed to prepare transaction: {str(e)}")
            raise
    
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
            
            # Hash the transaction
            tx_hash = DiracHash.hash(raw_transaction, digest_size=32, algorithm="improved")
            
            # Verify signature
            if wallet:
                key_manager = wallet.key_manager
            else:
                from .keys import QuantumKeyManager
                key_manager = QuantumKeyManager(
                    security_level=signature_metadata.get("security_level", 3)
                )
            
            is_valid = key_manager.verify_signature(
                tx_hash,
                quantum_signature,
                public_key
            )
            
            logger.debug(f"Quantum signature verification: {is_valid}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Failed to verify quantum signature: {str(e)}")
            return False