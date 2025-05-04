"""
Transaction model for wallet operations.
"""

import time
from typing import Dict, Any

class Transaction:
    """Simple transaction record."""
    
    def __init__(self, 
                 tx_id: str, 
                 sender: str, 
                 recipient: str, 
                 amount: float, 
                 timestamp: float = None,
                 status: str = "pending"):
        self.tx_id = tx_id
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or time.time()
        self.status = status  # pending, confirmed, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            "tx_id": self.tx_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary."""
        return cls(
            tx_id=data["tx_id"],
            sender=data["sender"],
            recipient=data["recipient"],
            amount=data["amount"],
            timestamp=data["timestamp"],
            status=data["status"]
        ) 