"""
Wallet-related API endpoints for Dirac Wallet
"""
from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel, Field
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import base64

# Add the parent directory to sys.path to be able to import dirac_wallet
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import wallet functions - these are just for reference, actual wallet operations
# will be done client-side with Pyodide/WebAssembly
from dirac_wallet.core.wallet import DiracWallet

# Create router
router = APIRouter()

class PublicKeyInfo(BaseModel):
    """Public key information model"""
    public_key: str
    algorithm: str = "dilithium"
    security_level: int = 3

class BalanceResponse(BaseModel):
    """Balance response model"""
    address: str
    balance: float  # In SOL
    lamports: int   # Raw lamports (1 SOL = 1,000,000,000 lamports)

class TokenBalance(BaseModel):
    """Token balance model"""
    mint: str
    symbol: Optional[str] = None
    name: Optional[str] = None
    amount: float
    decimals: int
    ui_amount: float

class TokenBalanceListResponse(BaseModel):
    """Token balance list response model"""
    address: str
    sol_balance: float
    tokens: List[TokenBalance]

@router.get("/balance/{address}")
async def get_balance(address: str) -> BalanceResponse:
    """
    Get the SOL balance for a wallet address
    
    Args:
        address: The wallet address to check
        
    Returns:
        The SOL balance for the address
    """
    try:
        # In a real implementation, we'd query the balance from the Solana RPC
        # For now, just return mock data
        lamports = 1_500_000_000  # 1.5 SOL in lamports
        sol = lamports / 1_000_000_000  # Convert to SOL
        
        return BalanceResponse(
            address=address,
            balance=sol,
            lamports=lamports
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get balance: {str(e)}"
        )

@router.get("/tokens/{address}")
async def get_token_balances(address: str) -> TokenBalanceListResponse:
    """
    Get token balances for a wallet address
    
    Args:
        address: The wallet address to check
        
    Returns:
        Token balances for the address
    """
    try:
        # In a real implementation, we'd query token accounts from the Solana RPC
        # For now, just return mock data
        tokens = [
            TokenBalance(
                mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                symbol="USDC",
                name="USD Coin",
                amount=100.0,
                decimals=6,
                ui_amount=100.0
            ),
            TokenBalance(
                mint="DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
                symbol="BONK",
                name="Bonk",
                amount=1000000.0,
                decimals=5,
                ui_amount=1000000.0
            )
        ]
        
        return TokenBalanceListResponse(
            address=address,
            sol_balance=1.5,  # Mock SOL balance
            tokens=tokens
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get token balances: {str(e)}"
        )

@router.get("/address/{public_key}")
async def derive_address(public_key: str) -> Dict:
    """
    Derive a Solana address from a quantum public key 
    
    This endpoint is provided for reference only. In the actual implementation,
    address derivation will be done client-side with Pyodide/WebAssembly.
    
    Args:
        public_key: The base64-encoded quantum public key
        
    Returns:
        The derived Solana address
    """
    try:
        # In a real implementation, this would use the AddressDerivation class
        # Here we just return a mock response
        return {
            "address": "5UfDMpuKnuYs4AFzGzwrjMnTWqk2cfJYf4QPRcz1ace4",
            "is_valid": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to derive address: {str(e)}"
        )

class WalletStateInfo(BaseModel):
    """Wallet state info for browser wallet status check"""
    has_wallet: bool
    address: Optional[str] = None
    network: Optional[str] = None
    is_connected: bool = False
    type: str = "dirac"  # The wallet type

@router.get("/state")
async def check_wallet_state() -> WalletStateInfo:
    """
    Check whether the browser wallet is available
    
    This is a mock endpoint - in reality, the wallet state would be managed
    client-side with the wallet WebAssembly module
    
    Returns:
        Information about the wallet state
    """
    # Mock state - in reality, this would be managed client-side
    return WalletStateInfo(
        has_wallet=False,
        is_connected=False
    ) 