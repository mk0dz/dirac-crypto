"""
Network-related API endpoints for Dirac Wallet
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Create router
router = APIRouter()

class NetworkInfo(BaseModel):
    """Network information model"""
    name: str
    rpc_url: str
    status: str
    block_height: Optional[int] = None
    version: Optional[str] = None

class BlockhashResponse(BaseModel):
    """Recent blockhash response model"""
    blockhash: str
    last_valid_block_height: int

@router.get("/status")
async def get_network_status() -> Dict:
    """
    Get the current network status
    
    Returns:
        Status information about the current network
    """
    try:
        # This would connect to the Solana network to check status
        # For now, just return a mock response
        return {
            "status": "online",
            "block_height": 123456789,
            "version": "1.14.12",
            "cluster": "testnet",
            "transaction_count": 98765
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to connect to network: {str(e)}"
        )

@router.get("/info/{network_name}")
async def get_network_info(network_name: str) -> NetworkInfo:
    """
    Get information about a specific network
    
    Args:
        network_name: The name of the network (mainnet, testnet, devnet)
        
    Returns:
        Information about the specified network
    """
    networks = {
        "mainnet": {
            "name": "Mainnet",
            "rpc_url": "https://api.mainnet-beta.solana.com",
            "status": "online",
            "block_height": 225678934,
            "version": "1.14.12"
        },
        "testnet": {
            "name": "Testnet",
            "rpc_url": "https://api.testnet.solana.com",
            "status": "online", 
            "block_height": 198765432,
            "version": "1.14.12"
        },
        "devnet": {
            "name": "Devnet",
            "rpc_url": "https://api.devnet.solana.com",
            "status": "online",
            "block_height": 187654321,
            "version": "1.14.12"
        }
    }
    
    if network_name not in networks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network '{network_name}' not found"
        )
        
    return NetworkInfo(**networks[network_name])

@router.get("/blockhash")
async def get_recent_blockhash() -> BlockhashResponse:
    """
    Get a recent blockhash from the network
    
    Returns:
        A recent blockhash and its last valid block height
    """
    try:
        # In real implementation, this would call the Solana RPC
        # Just returning a dummy blockhash for now
        return BlockhashResponse(
            blockhash="Ew3SR9vU9LNP9t1PxQQz9dBtmSZquFxw6sJ1P9JCoQoH",
            last_valid_block_height=123456859
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to get recent blockhash: {str(e)}"
        ) 