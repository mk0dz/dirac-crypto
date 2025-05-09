"""
Main FastAPI application for Dirac Wallet Backend
"""
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

# Add the parent directory to sys.path to be able to import dirac_wallet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.routes import network, transactions, wallet

# Initialize FastAPI app
app = FastAPI(
    title="Dirac Wallet API",
    description="API for interacting with Dirac Quantum-Resistant Wallet",
    version="0.1.0"
)

# Set up CORS middleware
origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000",
    # Add your frontend deployment URLs here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(network.router, prefix="/api/network", tags=["Network"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["Wallet"])

@app.get("/")
async def root():
    """Root endpoint for API health check"""
    return {
        "name": "Dirac Wallet API",
        "status": "online",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 