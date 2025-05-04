"""
Solana client wrapper with enhanced functionality.
"""

from typing import Dict, Any, Optional, Union, List
import time

from dirac.solana.keypair import convert_to_solana_keypair, keypair_to_base58

try:
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    Client = None
    TxOpts = None
    Keypair = None
    Pubkey = None

class SolanaClient:
    """Enhanced Solana client with additional functionality."""
    
    def __init__(self, network: str = "testnet"):
        """
        Initialize Solana client.
        
        Args:
            network: Network to connect to (mainnet, testnet, devnet, local)
        """
        self.network = network
        self._rpc_url = {
            "mainnet": "https://api.mainnet-beta.solana.com",
            "testnet": "https://api.testnet.solana.com",
            "devnet": "https://api.devnet.solana.com",
            "local": "http://localhost:8899"
        }.get(network, "https://api.testnet.solana.com")
        
        # Initialize Solana client if available
        self.client = Client(self._rpc_url) if SOLANA_AVAILABLE and Client is not None else None
    
    @property
    def rpc_url(self) -> str:
        """Get the RPC URL for the current network."""
        return self._rpc_url
    
    @rpc_url.setter
    def rpc_url(self, url: str) -> None:
        """
        Set the RPC URL and update the client.
        
        Args:
            url: RPC URL for the Solana API
        """
        self._rpc_url = url
        if SOLANA_AVAILABLE and Client is not None:
            self.client = Client(self._rpc_url)
    
    def is_available(self) -> bool:
        """Check if Solana integration is available."""
        return SOLANA_AVAILABLE and self.client is not None
    
    def get_balance(self, address: str) -> float:
        """
        Get SOL balance for a wallet address.
        
        Args:
            address: Solana wallet address
            
        Returns:
            Balance in SOL
        """
        if not self.is_available():
            return 0.0
        
        try:
            # Convert string address to Pubkey if needed
            pubkey = self._get_pubkey_from_address(address)
            if pubkey is None:
                return 0.0
                
            response = self.client.get_balance(pubkey)
            
            # Handle the response based on the actual structure
            # In the newer solders/solana versions, we need to access the value directly
            try:
                # For newer versions where response is a GetBalanceResp object
                lamports = response.value
            except (AttributeError, TypeError):
                try:
                    # Fall back to dictionary access for older versions
                    lamports = response["result"]["value"]
                except (KeyError, TypeError):
                    # If all else fails, assume no balance
                    lamports = 0
            
            # Convert lamports to SOL (1 SOL = 10^9 lamports)
            sol = lamports / 1_000_000_000
            return sol
        except Exception as e:
            print(f"Balance check error: {str(e)}")
            return 0.0
    
    def request_airdrop(self, address: str, amount_sol: float = 1.0) -> Optional[str]:
        """
        Request an airdrop of SOL to an address.
        
        Args:
            address: Solana wallet address
            amount_sol: Amount in SOL to request (default 1 SOL)
            
        Returns:
            Transaction signature or None if failed
        """
        if not self.is_available() or self.network not in ["testnet", "devnet", "local"]:
            return None
        
        try:
            # Convert SOL to lamports
            lamports = int(amount_sol * 1_000_000_000)
            
            # Convert string address to Pubkey
            pubkey = self._get_pubkey_from_address(address)
            if pubkey is None:
                print(f"Error: Could not convert address {address} to Pubkey")
                return None
                
            # Request airdrop
            response = self.client.request_airdrop(pubkey, lamports)
            
            # Extract transaction signature based on response type
            try:
                # For newer versions where response is a RequestAirdropResp object
                tx_sig = str(response.value)
            except (AttributeError, TypeError):
                try:
                    # Fall back to dictionary access for older versions
                    tx_sig = response["result"]
                except (KeyError, TypeError):
                    print(f"Error: Unexpected airdrop response format: {response}")
                    return None
            
            # Wait for confirmation
            self._confirm_transaction(tx_sig)
            
            return tx_sig
        except Exception as e:
            print(f"Airdrop error: {str(e)}")
            return None
    
    def _confirm_transaction(self, tx_sig: str, max_retries: int = 30) -> bool:
        """
        Wait for a transaction to be confirmed.
        
        Args:
            tx_sig: Transaction signature
            max_retries: Maximum number of confirmation attempts
            
        Returns:
            True if confirmed, False otherwise
        """
        if not self.is_available():
            return False
        
        retries = 0
        while retries < max_retries:
            try:
                response = self.client.get_signature_statuses([tx_sig])
                
                # Handle different response formats
                try:
                    # For newer versions
                    confirmation_status = response.value[0]
                    if confirmation_status is not None and confirmation_status.confirmation_status in ["confirmed", "finalized"]:
                        return True
                except (AttributeError, TypeError):
                    # Fall back to dictionary access for older versions
                    confirmation_status = response["result"]["value"][0]
                    if confirmation_status is not None and confirmation_status["confirmationStatus"] in ["confirmed", "finalized"]:
                        return True
            except Exception as e:
                print(f"Confirmation check error: {str(e)}")
            
            # Wait before retrying
            time.sleep(1)
            retries += 1
        
        return False
    
    def get_transaction_history(self, address: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get transaction history for an address.
        
        Args:
            address: Solana wallet address
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction details
        """
        if not self.is_available():
            return []
        
        try:
            # Convert string address to Pubkey
            pubkey = self._get_pubkey_from_address(address)
            if pubkey is None:
                return []
            
            response = self.client.get_signatures_for_address(pubkey, limit=limit)
            
            # Handle different response formats
            try:
                # For newer versions
                return [tx.__dict__ for tx in response.value]
            except (AttributeError, TypeError):
                # Fall back to dictionary access for older versions
                return response["result"]
        except Exception as e:
            print(f"Transaction history error: {str(e)}")
            return []
    
    def _get_pubkey_from_address(self, address: str) -> Optional[object]:
        """
        Convert a string address to a Solana Pubkey object.
        
        Args:
            address: Solana wallet address as a string
            
        Returns:
            Pubkey object or None if conversion fails
        """
        if not SOLANA_AVAILABLE or Pubkey is None:
            return None
            
        try:
            return Pubkey.from_string(address)
        except Exception as e:
            print(f"Pubkey conversion error: {str(e)}")
            return None 