"""
Solana network client for quantum-resistant transactions
"""
import json
import asyncio
from typing import Dict, Optional, Tuple
from solana.rpc.async_api import AsyncClient
from solana.rpc.core import RPCException
from solders.transaction import Transaction
from solders.hash import Hash
from decimal import Decimal

from ..utils.logger import logger


class QuantumSolanaClient:
    """
    Manages connections to Solana network and transaction submission.
    Supports quantum-resistant transaction signing.
    """
    
    def __init__(self, network: str = "testnet", rpc_url: str = None):
        """Initialize Solana client"""
        self.network = network
        
        # Default RPC endpoints
        self.network_urls = {
            "testnet": "https://api.testnet.solana.com",
            "devnet": "https://api.devnet.solana.com",
            "mainnet": "https://api.mainnet-beta.solana.com",
        }
        
        self.rpc_url = rpc_url or self.network_urls.get(network, self.network_urls["testnet"])
        self.client = None
        
        logger.info(f"Initialized QuantumSolanaClient for {network}")
    
    async def connect(self):
        """Connect to Solana RPC"""
        try:
            self.client = AsyncClient(self.rpc_url)
            connection_status = await self.client.is_connected()
            logger.info(f"Connected to Solana {self.network}: {connection_status}")
            return connection_status
        except Exception as e:
            logger.error(f"Failed to connect to Solana: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from Solana RPC"""
        try:
            if self.client:
                await self.client.close()
                logger.info("Disconnected from Solana")
        except Exception as e:
            logger.error(f"Failed to disconnect: {str(e)}")
    
    async def get_balance(self, address: str) -> float:
        """Get SOL balance for an address"""
        try:
            if not self.client:
                await self.connect()
            
            response = await self.client.get_balance(address)
            
            if response.value is not None:
                # Convert lamports to SOL
                balance_sol = Decimal(response.value) / Decimal(10**9)
                logger.debug(f"Balance for {address}: {balance_sol} SOL")
                return float(balance_sol)
            else:
                raise ValueError("Failed to get balance")
                
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            raise
    
    async def get_recent_blockhash(self) -> Hash:
        """Get recent blockhash for transactions"""
        try:
            if not self.client:
                await self.connect()
            
            response = await self.client.get_latest_blockhash()
            
            if response.value and response.value.blockhash:
                blockhash_value = response.value.blockhash
                logger.debug(f"Recent blockhash: {blockhash_value}")
                return blockhash_value
            else:
                raise ValueError("Failed to get recent blockhash")
                
        except Exception as e:
            logger.error(f"Failed to get recent blockhash: {str(e)}")
            raise
    
    async def submit_quantum_transaction(
        self, 
        raw_transaction: bytes, 
        quantum_signature: Dict,
        metadata: Dict
    ) -> Dict:
        """
        Submit quantum-resistant transaction to Solana network
        
        Returns:
            Dict containing transaction_id and status
        """
        try:
            if not self.client:
                await self.connect()
            
            # Submit the raw transaction
            response = await self.client.send_raw_transaction(raw_transaction)
            
            tx_id = str(response.value)
            
            # Store quantum metadata for verification
            result = {
                "transaction_id": tx_id,
                "status": "submitted",
                "quantum_metadata": {
                    "signature": quantum_signature,
                    "algorithm": metadata.get("signature_algorithm", "dilithium"),
                    "security_level": metadata.get("security_level", 3),
                    "timestamp": metadata.get("timestamp")
                }
            }
            
            logger.info(f"Submitted quantum transaction: {tx_id}")
            return result
            
        except RPCException as e:
            logger.error(f"RPC error submitting transaction: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to submit transaction: {str(e)}")
            raise
    
    async def get_transaction_status(self, tx_id: str, max_retries: int = 5) -> Dict:
        """Get transaction confirmation status"""
        try:
            if not self.client:
                await self.connect()
            
            for attempt in range(max_retries):
                try:
                    response = await self.client.get_transaction(tx_id)
                    
                    if response.value is not None:
                        meta = response.value.transaction.meta
                        slot = response.value.slot
                        
                        if meta and meta.err is None:
                            status = {
                                "confirmed": True,
                                "slot": slot,
                                "error": None,
                                "block_time": response.value.blockTime
                            }
                            logger.info(f"Transaction confirmed in slot {slot}")
                            return status
                        elif meta and meta.err is not None:
                            return {
                                "confirmed": False,
                                "error": str(meta.err),
                                "slot": slot
                            }
                    
                    # Transaction not yet confirmed
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1.5)  # Wait 1.5 seconds between retries
                        
                except Exception as e:
                    logger.error(f"Error checking transaction status: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1.5)
                    else:
                        raise
            
            # Transaction not confirmed after max retries
            return {
                "confirmed": False,
                "error": "Transaction confirmation timed out"
            }
            
        except Exception as e:
            logger.error(f"Failed to get transaction status: {str(e)}")
            raise
    
    async def request_airdrop(self, address: str, amount_sol: float = 1.0) -> Optional[str]:
        """Request SOL airdrop on testnet/devnet"""
        try:
            if self.network == "mainnet":
                raise ValueError("Airdrop not available on mainnet")
            
            if not self.client:
                await self.connect()
            
            lamports = int(amount_sol * 10**9)
            response = await self.client.request_airdrop(address, lamports)
            
            if response.value:
                tx_id = str(response.value)
                logger.info(f"Airdrop requested: {tx_id}")
                return tx_id
            else:
                raise ValueError("Airdrop request failed")
                
        except Exception as e:
            logger.error(f"Failed to request airdrop: {str(e)}")
            raise