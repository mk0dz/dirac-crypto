"""
Solana transaction utilities.
"""

from typing import Dict, Any, Optional, List
import base64
import time

from dirac.solana.keypair import convert_to_solana_keypair, keypair_to_base58

try:
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.system_program import TransferParams, transfer
    from solders.transaction import Transaction as SolTransaction
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    Client = None
    TxOpts = None
    Keypair = None
    Pubkey = None
    TransferParams = None
    transfer = None
    SolTransaction = None

def create_transfer_transaction(
    sender_keypair: Any, 
    recipient_address: str, 
    amount_sol: float,
    client: Optional[Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a Solana transfer transaction.
    
    Args:
        sender_keypair: Solana keypair of the sender
        recipient_address: Recipient's Solana address
        amount_sol: Amount in SOL to transfer
        client: Optional Solana client for fetching recent blockhash
        
    Returns:
        Dictionary with transaction details or None if failed
    """
    if not SOLANA_AVAILABLE or not isinstance(sender_keypair, Keypair):
        return None
    
    try:
        # Convert recipient address to Pubkey
        recipient_pubkey = Pubkey.from_string(recipient_address)
        
        # Convert SOL to lamports
        lamports = int(amount_sol * 1_000_000_000)
        
        # Create transfer instruction
        transfer_instruction = transfer(
            TransferParams(
                from_pubkey=sender_keypair.pubkey(),
                to_pubkey=recipient_pubkey,
                lamports=lamports
            )
        )
        
        # Get recent blockhash if client is provided
        recent_blockhash = None
        if client is not None:
            response = client.get_latest_blockhash()
            recent_blockhash = response["result"]["value"]["blockhash"]
        
        # Create transaction
        transaction = SolTransaction.new_with_payer(
            [transfer_instruction],
            sender_keypair.pubkey()
        )
        
        # Sign transaction
        transaction.sign([sender_keypair])
        
        return {
            "transaction": transaction,
            "signed": True,
            "sender": str(sender_keypair.pubkey()),
            "recipient": recipient_address,
            "amount_sol": amount_sol,
            "amount_lamports": lamports,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"Transaction creation error: {str(e)}")
        return None

def serialize_transaction(transaction: Any) -> Optional[str]:
    """
    Serialize a Solana transaction to base64.
    
    Args:
        transaction: Solana transaction object
        
    Returns:
        Base64 encoded transaction or None if failed
    """
    if not SOLANA_AVAILABLE or not transaction:
        return None
    
    try:
        # Convert transaction to bytes and then base64
        transaction_bytes = transaction.serialize()
        return base64.b64encode(transaction_bytes).decode('utf-8')
    except Exception as e:
        print(f"Transaction serialization error: {str(e)}")
        return None

def deserialize_transaction(transaction_base64: str) -> Optional[Any]:
    """
    Deserialize a base64 encoded transaction.
    
    Args:
        transaction_base64: Base64 encoded transaction
        
    Returns:
        Solana transaction object or None if failed
    """
    if not SOLANA_AVAILABLE or not SolTransaction:
        return None
    
    try:
        # Convert base64 to bytes and then to transaction
        transaction_bytes = base64.b64decode(transaction_base64)
        return SolTransaction.from_bytes(transaction_bytes)
    except Exception as e:
        print(f"Transaction deserialization error: {str(e)}")
        return None 