"""
Solana network client for quantum-resistant transactions
"""
import json
import asyncio
import aiohttp
from typing import Dict, Optional, Tuple, List, Any
from solana.rpc.async_api import AsyncClient
from solana.rpc.core import RPCException as RpcException
from solders.transaction import Transaction
from solders.hash import Hash
from solders.pubkey import Pubkey
from decimal import Decimal
from datetime import datetime
from solders.signature import Signature

from ..utils.logger import logger
from ..core.transactions import QuantumTransaction


class QuantumSolanaClient:
    """
    Manages connections to Solana network and transaction submission.
    Supports quantum-resistant transaction signing.
    """
    
    # RPC endpoints for different networks with fallbacks
    RPC_ENDPOINTS = {
        "devnet": [
            "https://api.devnet.solana.com",
            "https://rpc-devnet.helius.xyz/?api-key=1d41c193-0e68-4e53-8a44-35504168d3f3",
            "https://devnet.genesysgo.net",
            "https://devnet.solana.com",
            "https://api.mainnet-beta.solana.com",  # Mainnet can also serve devnet requests
            "https://solana-api.projectserum.com"   # ProjectSerum can also serve devnet requests
        ],
        "testnet": [
            "https://api.testnet.solana.com",
            "https://testnet.solana.com",
            "https://testnet.genesysgo.net"
        ],
        "mainnet": [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana"
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
        
        # Set current endpoint
        if endpoint:
            self.current_endpoint = endpoint
        else:
            endpoints = self.RPC_ENDPOINTS.get(network, [])
            if endpoints:
                self.current_endpoint = endpoints[0]
            else:
                raise ValueError(f"No RPC endpoints available for network: {network}")
        
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
            self.client = AsyncClient(endpoint, commitment="confirmed")
            
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
        self.current_endpoint = endpoints[self.current_endpoint_index]
        
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
    
    async def submit_quantum_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """Submit a quantum-signed transaction to the Solana network."""
        try:
            if not self.client:
                await self.connect()

            # Initialize quantum metadata storage if not exists
            if not hasattr(self, 'quantum_metadata'):
                self.quantum_metadata = {}

            # Submit transaction
            response = await self.client.send_transaction(
                transaction
            )
            
            # Extract signature from response
            if hasattr(response, 'value'):
                signature = str(response.value)
            else:
                signature = str(response)
            
            # Store quantum metadata for verification
            self.quantum_metadata[signature] = {
                "signature": bytes(transaction.signatures[0]).hex(),
                "algorithm": "DILITHIUM3",
                "security_level": 3,
                "message_hash": bytes(transaction.message.hash()).hex(),
                "blockhash": str(transaction.message.recent_blockhash),
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "signature": signature,
                "status": "submitted"
            }
            
        except RpcException as e:
            logger.error(f"RPC error submitting transaction: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error submitting transaction: {str(e)}")
            raise
    
    async def get_transaction_status(self, tx_id: str, max_retries: int = 5) -> Dict:
        """Get transaction confirmation status"""
        try:
            if not self.client:
                await self.connect()
            
            # Convert string signature to Signature object
            signature = Signature.from_string(tx_id)
            
            for attempt in range(max_retries):
                try:
                    response = await self.client.get_transaction(signature)
                    
                    if response.value is not None:
                        meta = response.value.transaction.meta
                        slot = response.value.slot
                        
                        if meta and meta.err is None:
                            status = {
                                "confirmed": True,
                                "slot": slot,
                                "error": None
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
                f"Visit https://solfaucet.com and request SOL for {network_name}",
                f"Visit https://faucet.solana.com and request SOL for {network_name}",
                f"Visit https://quicknode.com/faucet/sol and request SOL for {network_name}"
            ],
            "cli_commands": [
                f"Run: solana config set --url {self.network}",
                f"Run: solana airdrop 1 {address}",
                "If rate limited, wait a few minutes and try again"
            ],
            "discord_faucets": [
                "Join Solana Discord: https://discord.gg/solana",
                "Use the #devnet-faucet channel to request SOL"
            ],
            "address": address,
            "network": self.network,
            "note": "If one method fails, please try another. Rate limits may apply."
        }
        
        return alternatives
    
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
                        
                        # Wait for confirmation
                        await asyncio.sleep(2)
                        status = await self.get_transaction_status(tx_id)
                        if status.get("confirmed"):
                            return tx_id
                        elif status.get("error") and "rate limit" in str(status.get("error")).lower():
                            logger.warning("Rate limit reached, trying alternative endpoint")
                            await asyncio.sleep(2)  # Wait before trying next endpoint
                            continue
                        
                    error_msg = f"Airdrop request failed or not confirmed"
                    logger.error(error_msg)
                    last_error = ValueError(error_msg)
                        
                except asyncio.TimeoutError:
                    error_msg = "Airdrop request timed out. The network may be congested."
                    logger.error(error_msg)
                    last_error = ValueError(error_msg)
                    await asyncio.sleep(2)  # Wait before retrying
                    
                except RpcException as rpc_err:
                    # Catch specific RPC exceptions from the Solana client
                    error_msg = f"RPC error during airdrop request: {str(rpc_err)}"
                    logger.error(error_msg)
                    
                    if "429" in str(rpc_err) or "rate limit" in str(rpc_err).lower():
                        logger.warning("Rate limit reached, trying alternative endpoint")
                        await asyncio.sleep(2)  # Wait before trying next endpoint
                        continue
                    elif "exceeds max allowed amount" in str(rpc_err).lower():
                        # Don't retry for amount errors
                        raise ValueError("Requested amount exceeds maximum allowed airdrop amount.")
                    else:
                        last_error = ValueError(f"Airdrop failed: {str(rpc_err)}")
                
                except Exception as e:
                    error_msg = f"Unexpected error during airdrop request: {str(e)}"
                    logger.error(error_msg)
                    last_error = ValueError(error_msg)
                    
                # If we got here, the request failed. Try the next endpoint
                success = await self.try_next_endpoint()
                if not success:
                    logger.error("Failed to connect to next endpoint")
                    break
                    
                tries += 1
                await asyncio.sleep(1)  # Wait before retrying
                    
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
                await asyncio.sleep(1)  # Wait before retrying
                
        # If we've tried all endpoints, return None to indicate failure
        # The caller should then use get_airdrop_alternatives()
        return None
    
    async def request_faucet_airdrop(self, address: str, amount_sol: float = 1.0) -> Dict[str, Any]:
        """
        Request an airdrop from alternative faucets
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
            # Try multiple faucet APIs
            faucet_urls = {
                "devnet": [
                    "https://faucet.devnet.solana.com/api/v1/request",
                    "https://api.faucet.solana.com/api/v1/request",
                    "https://faucet.quicknode.com/solana/devnet"
                ],
                "testnet": [
                    "https://faucet.testnet.solana.com/api/v1/request",
                    "https://api.faucet.solana.com/api/v1/request"
                ]
            }
            
            urls = faucet_urls.get(self.network, [])
            if not urls:
                return {
                    "success": False,
                    "error": f"No faucet URLs available for {self.network}"
                }
            
            # Try each faucet URL
            for url in urls:
                try:
                    # Prepare the request data
                    data = {
                        "address": address,
                        "network": self.network,
                        "amount": amount_sol
                    }
                    
                    logger.info(f"Trying faucet at {url}")
                    
                    # Send the request to the faucet API
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, json=data, timeout=30) as response:
                            if response.status == 200:
                                try:
                                    result = await response.json()
                                    logger.info(f"Faucet airdrop request successful: {result}")
                                    return {
                                        "success": True,
                                        "response": result
                                    }
                                except:
                                    # If JSON parsing fails, try text
                                    text = await response.text()
                                    if "success" in text.lower():
                                        return {
                                            "success": True,
                                            "response": {"message": text}
                                        }
                            
                            # If this faucet failed, try the next one
                            logger.warning(f"Faucet {url} failed, trying next...")
                            await asyncio.sleep(1)
                            
                except Exception as e:
                    logger.warning(f"Error with faucet {url}: {str(e)}")
                    continue
            
            # If all faucets failed
            return {
                "success": False,
                "error": "All faucet attempts failed"
            }
                        
        except Exception as e:
            error_msg = f"Failed to request airdrop from faucets: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def get_transaction_history(self, address: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch transaction history for an address"""
        try:
            if not self.client:
                await self.connect()
            
            # Convert string address to Pubkey
            pubkey = Pubkey.from_string(address)
            
            # Get signatures for address (most recent first)
            response = await self.client.get_signatures_for_address(
                pubkey, 
                limit=limit
            )
            
            if not response.value:
                logger.info(f"No transaction history found for {address}")
                return []
                
            logger.info(f"Found {len(response.value)} transactions for {address}")
            
            # Process each transaction
            transactions = []
            for sig_info in response.value:
                signature = sig_info.signature
                
                try:
                    # Get transaction details
                    tx_response = await self.client.get_transaction(
                        signature, 
                        max_supported_transaction_version=0
                    )
                    
                    if not tx_response.value:
                        logger.warning(f"Transaction {signature} details not found")
                        continue
                    
                    # Extract transaction data
                    tx_data = tx_response.value
                    
                    # The object structure may vary depending on Solders version
                    # First, try to extract using the enhanced transaction structure
                    try:
                        # For newer Solders versions
                        meta = tx_data.meta
                        transaction = tx_data.transaction
                        fee = meta.fee / 1_000_000_000 if hasattr(meta, 'fee') else 0.000005
                        status = "confirmed" if getattr(meta, 'status', None) and meta.status.Ok is not None else "failed"
                    except (AttributeError, TypeError):
                        # For older or different structure
                        if hasattr(tx_data, 'transaction'):
                            transaction = tx_data.transaction
                            # Try to access transaction.meta
                            if hasattr(transaction, 'meta'):
                                meta = transaction.meta
                                fee = meta.fee / 1_000_000_000 if hasattr(meta, 'fee') else 0.000005
                                status = "confirmed"
                            # Handle EncodedConfirmedTransactionWithStatusMeta structure
                            elif hasattr(tx_data, 'meta'):
                                meta = tx_data.meta
                                fee = 0.000005  # Default fee if not available
                                status = "confirmed"
                            else:
                                # If we can't find meta, use defaults
                                meta = None
                                fee = 0.000005
                                status = "confirmed"
                        else:
                            # If we can't find transaction, skip this entry
                            logger.warning(f"Unknown transaction structure for {signature}")
                            continue
                    
                    # Extract timestamp
                    timestamp = None
                    if hasattr(tx_data, 'block_time') and tx_data.block_time is not None:
                        timestamp = datetime.fromtimestamp(tx_data.block_time).isoformat()
                    else:
                        # Use signature confirm time from signature info
                        timestamp = datetime.fromtimestamp(sig_info.block_time).isoformat() if hasattr(sig_info, 'block_time') and sig_info.block_time else datetime.now().isoformat()
                    
                    # Try to determine amount, sender and recipient
                    amount = 0
                    sender = None
                    recipient = None
                    tx_type = "unknown"
                    
                    # Try to extract account keys and instructions
                    try:
                        if hasattr(transaction, 'message') and hasattr(transaction.message, 'account_keys'):
                            account_keys = transaction.message.account_keys
                            if hasattr(transaction.message, 'instructions'):
                                instructions = transaction.message.instructions
                                
                                # Check for SOL transfers (system program)
                                for inst in instructions:
                                    try:
                                        if hasattr(inst, 'program_id_index'):
                                            program_id_index = inst.program_id_index
                                            if program_id_index < len(account_keys):
                                                program_id = str(account_keys[program_id_index])
                                                
                                                # System program transfers
                                                if program_id == "11111111111111111111111111111111":
                                                    tx_type = "transfer"
                                                    
                                                    # Try to extract accounts from instruction
                                                    if hasattr(inst, 'accounts') and len(inst.accounts) >= 2:
                                                        sender_idx = inst.accounts[0]
                                                        recipient_idx = inst.accounts[1]
                                                        
                                                        if sender_idx < len(account_keys) and recipient_idx < len(account_keys):
                                                            sender = str(account_keys[sender_idx])
                                                            recipient = str(account_keys[recipient_idx])
                                                            
                                                            # Try to extract amount from pre/post balances
                                                            if hasattr(meta, 'pre_balances') and hasattr(meta, 'post_balances'):
                                                                pre_balances = meta.pre_balances
                                                                post_balances = meta.post_balances
                                                                
                                                                if sender_idx < len(pre_balances) and sender_idx < len(post_balances) and \
                                                                   recipient_idx < len(pre_balances) and recipient_idx < len(post_balances):
                                                                    pre_sender = pre_balances[sender_idx]
                                                                    post_sender = post_balances[sender_idx]
                                                                    pre_recipient = pre_balances[recipient_idx]
                                                                    post_recipient = post_balances[recipient_idx]
                                                                    
                                                                    # Calculate amount
                                                                    sender_change = pre_sender - post_sender
                                                                    recipient_change = post_recipient - pre_recipient
                                                                    
                                                                    # Use recipient change as amount
                                                                    if recipient_change > 0:
                                                                        amount = recipient_change / 1_000_000_000  # Convert lamports to SOL
                                    except Exception as inst_error:
                                        logger.warning(f"Error processing instruction: {str(inst_error)}")
                                        continue
                    except Exception as tx_error:
                        logger.warning(f"Error extracting transaction details: {str(tx_error)}")
                    
                    # If we still don't have sender/recipient, use fee payer and fallbacks
                    if not sender:
                        try:
                            # Fee payer is usually the first account
                            if hasattr(transaction, 'message') and hasattr(transaction.message, 'account_keys') and len(transaction.message.account_keys) > 0:
                                sender = str(transaction.message.account_keys[0])
                        except Exception:
                            sender = address  # Use wallet address as fallback
                    
                    if not recipient:
                        recipient = sender  # Self-transfer if no recipient identified
                    
                    # Create transaction record with the information we have
                    tx_record = {
                        "signature": str(signature),
                        "sender": sender or address,
                        "recipient": recipient or address,
                        "amount": amount or 0.0,
                        "fee": fee,
                        "timestamp": timestamp,
                        "status": status,
                        "type": tx_type,
                        "memo": None
                    }
                    
                    transactions.append(tx_record)
                except Exception as e:
                    logger.warning(f"Error processing transaction {signature}: {str(e)}")
                    continue
            
            return transactions
                
        except Exception as e:
            logger.error(f"Failed to get transaction history: {str(e)}")
            return []