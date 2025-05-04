"""
Global settings for the Dirac wallet.
"""

import os
import json
from typing import Dict, Any, Optional

# Default settings
DEFAULT_SETTINGS = {
    "network": "testnet",
    "wallet_dir": os.path.join(os.path.expanduser("~"), ".dirac-wallet"),
    "default_sig_algo": "sphincs",
    "default_hash_algo": "sha256",
    "default_security_level": 3,
    "networks": {
        "mainnet": "https://api.mainnet-beta.solana.com",
        "testnet": "https://api.testnet.solana.com",
        "devnet": "https://api.devnet.solana.com",
        "local": "http://localhost:8899"
    },
    "version": "0.1.0"
}

def get_settings_path() -> str:
    """Get the path to the settings file."""
    # Settings are stored in the wallet directory
    wallet_dir = DEFAULT_SETTINGS["wallet_dir"]
    os.makedirs(wallet_dir, exist_ok=True)
    return os.path.join(wallet_dir, "settings.json")

def get_settings() -> Dict[str, Any]:
    """Get the current settings, creating default if needed."""
    settings_path = get_settings_path()
    
    # If settings file doesn't exist, create it with defaults
    if not os.path.exists(settings_path):
        with open(settings_path, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=2)
        return DEFAULT_SETTINGS.copy()
    
    # Load settings from file
    try:
        with open(settings_path, "r") as f:
            settings = json.load(f)
            
        # Ensure all default settings exist (in case file is from older version)
        for key, value in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = value
        
        return settings
    except Exception:
        # If there's an error reading settings, return defaults
        return DEFAULT_SETTINGS.copy()

def update_settings(settings: Dict[str, Any]) -> None:
    """Update the settings file."""
    settings_path = get_settings_path()
    
    # Ensure we're not overwriting essential settings
    for key in ["wallet_dir", "networks", "version"]:
        if key not in settings and key in DEFAULT_SETTINGS:
            settings[key] = DEFAULT_SETTINGS[key]
    
    # Write settings to file
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

def get_setting(key: str) -> Any:
    """Get a specific setting by key."""
    settings = get_settings()
    return settings.get(key, DEFAULT_SETTINGS.get(key))

def update_setting(key: str, value: Any) -> None:
    """Update a specific setting."""
    settings = get_settings()
    settings[key] = value
    update_settings(settings) 