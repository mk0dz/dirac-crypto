"""
Solana network client for quantum-resistant transactions
"""
import json
import asyncio
import aiohttp
from typing import Dict, Optional, Tuple, List, Any
from solana.rpc.async_api import AsyncClient
from solana.rpc.core import RPCException
from solders.transaction import Transaction
from solders.hash import Hash
from solders.pubkey import Pubkey
from decimal import Decimal

from ..utils.logger import logger


class QuantumSolanaClient:
    """
    Manages connections to Solana network and transaction submission.
    Supports quantum-resistant transaction signing.
    """
    
    # RPC endpoints for different networks with fallbacks
    RPC_ENDPOINTS = {
        "devnet": [
            "https://api.devnet.solana.com",
            "https://devnet.solana.com",
            "https://rpc-devnet.helius.xyz",
            "https://devnet.genesysgo.net"
        ],
        "testnet": [
            "https://api.testnet.solana.com",
            "https://testnet.solana.com"
        ],
        "mainnet": [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com"
        ]
    }
    
    def __init__(self, network: str = "devnet", endpoint: str = None):
        """
        Initialize Solana client
        
        Args:
            network: Solana network (devnet, testnet, mainnet)
            endpoint: Custom RPC endpoint URL (optional)
        """
        self.network = network
        self.client = None
        self.current_endpoint = endpoint
        self.current_endpoint_index = 0
        
        logger.info(f"Initialized QuantumSolanaClient for {network}")
    
    async def connect(self) -> bool:
        """Connect to Solana RPC endpoint with fallback support"""
        try:
            # Close any existing client
            if self.client:
                await self.client.close()
                self.client = None
            
            # If custom endpoint provided, use it
            if self.current_endpoint:
                endpoint = self.current_endpoint
            else:
                # Otherwise use the current endpoint from the list for the network
                endpoints = self.RPC_ENDPOINTS.get(self.network, [])
                if not endpoints:
                    raise ValueError(f"No RPC endpoints available for network: {self.network}")
                
                endpoint = endpoints[self.current_endpoint_index]
            
            # Create a new client and connect
            self.client = AsyncClient(endpoint)
            
            # Test the connection
            version = await self.client.get_version()
            is_connected = version is not None
            
            logger.info(f"Connected to Solana {self.network}: {is_connected}")
            return is_connected
            
        except Exception as e:
            logger.error(f"Failed to connect to Solana {self.network}: {str(e)}")
            self.client = None
            return False
    
    async def try_next_endpoint(self) -> bool:
        """Try the next available RPC endpoint"""
        # If using a custom endpoint, we don't have fallbacks
        if self.current_endpoint:
            return False
            
        endpoints = self.RPC_ENDPOINTS.get(self.network, [])
        if not endpoints:
            return False
            
        # Move to the next endpoint in the list
        self.current_endpoint_index = (self.current_endpoint_index + 1) % len(endpoints)
        
        # Try to connect to the new endpoint
        return await self.connect()
    
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
            
            # Convert string address to Pubkey object
            pubkey = Pubkey.from_string(address)
            
            response = await self.client.get_balance(pubkey)
            
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
        """Request SOL airdrop on testnet/devnet with automatic retry on different endpoints"""
        if self.network == "mainnet":
            raise ValueError("Airdrop not available on mainnet")
        
        # Number of endpoints to try before giving up
        max_tries = len(self.RPC_ENDPOINTS.get(self.network, []))
        if max_tries == 0:
            max_tries = 1
            
        tries = 0
        last_error = None
        
        while tries < max_tries:
            try:
                if not self.client:
                    await self.connect()
                
                # Convert string address to Pubkey object
                pubkey = Pubkey.from_string(address)
                
                lamports = int(amount_sol * 10**9)
                
                # Detailed debugging before the request
                logger.debug(f"Try #{tries+1}: Requesting airdrop: address={pubkey}, lamports={lamports}, network={self.network}")
                
                try:
                    # Set longer timeout for airdrop request
                    response = await asyncio.wait_for(
                        self.client.request_airdrop(pubkey, lamports),
                        timeout=30.0
                    )
                    
                    # Log raw response for debugging
                    logger.debug(f"Raw airdrop response: {response}")
                    
                    if hasattr(response, 'value') and response.value:
                        tx_id = str(response.value)
                        logger.info(f"Airdrop requested: {tx_id}")
                        return tx_id
                    else:
                        error_msg = f"Airdrop request returned invalid response: {response}"
                        logger.error(error_msg)
                        last_error = ValueError(error_msg)
                        
                except asyncio.TimeoutError:
                    error_msg = "Airdrop request timed out. The network may be congested."
                    logger.error(error_msg)
                    last_error = ValueError(error_msg)
                    
                except RPCException as rpc_err:
                    # Catch specific RPC exceptions from the Solana client
                    error_msg = f"RPC error during airdrop request: {str(rpc_err)}"
                    logger.error(error_msg)
                    
                    if "429" in str(rpc_err):
                        last_error = ValueError("Rate limit exceeded. Please try again later.")
                    elif "exceeds max allowed amount" in str(rpc_err).lower():
                        # Don't retry for amount errors
                        raise ValueError("Requested amount exceeds maximum allowed airdrop amount.")
                    else:
                        last_error = ValueError(f"Airdrop failed: {str(rpc_err)}")
                
                except Exception as e:
                    error_msg = f"Unexpected error during airdrop request: {str(e)}, {type(e)}"
                    logger.error(error_msg)
                    last_error = ValueError(error_msg)
                    
                # If we got here, the request failed. Try the next endpoint
                success = await self.try_next_endpoint()
                if not success:
                    logger.error("Failed to connect to next endpoint")
                    break
                    
                tries += 1
                    
            except Exception as e:
                if "exceeds max allowed amount" in str(e).lower():
                    # Don't retry for specific errors
                    raise
                    
                error_msg = f"Failed to request airdrop: {str(e)}"
                logger.error(error_msg)
                last_error = ValueError(error_msg)
                
                # Try the next endpoint
                success = await self.try_next_endpoint()
                if not success:
                    break
                    
                tries += 1
                
        # If we've tried all endpoints and still failed, raise the last error
        if last_error:
            raise last_error
        else:
            raise ValueError("Failed to request airdrop after trying all available endpoints")
    
    async def get_airdrop_alternatives(self, address: str) -> Dict[str, str]:
        """
        Returns alternative methods to get SOL for test networks
        when the regular airdrop is not working
        
        Args:
            address: The Solana address to receive SOL
            
        Returns:
            Dictionary of alternative methods with instructions
        """
        if self.network not in ["devnet", "testnet"]:
            return {"error": "Alternative airdrop methods are only available for devnet and testnet"}
        
        network_name = self.network.capitalize()
        
        alternatives = {
            "web_faucets": [
                f"Visit https://faucet.solana.com and request SOL for {network_name}",
                f"Visit https://solfaucet.com and request SOL for {network_name}",
                f"Visit https://{self.network}faucet.org and request SOL for your address: {address}"
            ],
            "cli_command": f"Run this command in terminal: solana airdrop 2 {address} --url {self.network}",
            "discord_faucets": "Join Solana discord communities like LamportDAO or The 76 Devs to request SOL from their bots",
            "address": address,
            "network": self.network
        }
        
        return alternatives
    
    async def request_faucet_airdrop(self, address: str, amount_sol: float = 1.0) -> Dict[str, Any]:
        """
        Request an airdrop from SolFaucet.com API
        This is an alternative to the standard RPC airdrop
        
        Args:
            address: Solana address
            amount_sol: Amount in SOL (usually limited to 1.0)
            
        Returns:
            Response from the faucet
        """
        if self.network not in ["devnet", "testnet"]:
            return {
                "success": False,
                "error": "Faucet airdrop only available for devnet and testnet"
            }
            
        try:
            faucet_urls = {
                "devnet": "https://solfaucet.com/api/v1/request",
                "testnet": "https://solfaucet.com/api/v1/request"
            }
            
            url = faucet_urls.get(self.network)
            if not url:
                return {
                    "success": False,
                    "error": f"No faucet URL available for {self.network}"
                }
                
            # Prepare the request data
            data = {
                "address": address,
                "network": self.network
            }
            
            logger.info(f"Requesting airdrop from faucet for {address} on {self.network}")
            
            # Send the request to the faucet API
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=30) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        logger.info(f"Faucet airdrop request successful: {result}")
                        return {
                            "success": True,
                            "response": result
                        }
                    else:
                        logger.error(f"Faucet airdrop request failed: {result}")
                        return {
                            "success": False,
                            "error": f"Faucet error: {result.get('error', 'Unknown error')}"
                        }
                        
        except Exception as e:
            error_msg = f"Failed to request airdrop from faucet: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }