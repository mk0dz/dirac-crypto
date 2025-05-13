"""
Dirac-Wallet: A quantum-resistant Solana wallet
"""
__version__ = "0.1.3"
__author__ = "Dirac Team"
__description__ = "Quantum-resistant Solana wallet using quantum-inspired cryptography"

from .utils.logger import logger

# Log startup
logger.info(f"Dirac-Wallet v{__version__} initialized")