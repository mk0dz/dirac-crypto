"""
Logging configuration for Dirac-Wallet
"""
import logging
import os
from pathlib import Path
import yaml


def setup_logger(name: str = "dirac_wallet", config_path: str = None) -> logging.Logger:
    """Set up logger with configuration from YAML file."""
    
    # Load configuration
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception:
        # Fallback to default configuration
        config = {
            'logging': {
                'level': 'INFO',
                'file': 'dirac_wallet.log'
            }
        }
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config['logging']['level']))
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_file = Path(config['logging']['file'])
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Create a default logger instance
logger = setup_logger()