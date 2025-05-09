#!/usr/bin/env python3
"""
Script to prepare the Dirac Wallet for WebAssembly compilation with Pyodide

This script:
1. Creates a minimal package structure for the wallet core
2. Copies the necessary files
3. Provides instructions for building with Pyodide

Note: The actual compilation is done by the browser at runtime using Pyodide
"""
import os
import sys
import shutil
from pathlib import Path
import json

# Set up paths
current_dir = Path(__file__).parent
project_root = current_dir.parent
web_dir = project_root / "web"
wasm_build_dir = web_dir / "public" / "wasm"
dirac_src = project_root / "dirac_wallet"
wasm_src_dir = wasm_build_dir / "dirac_wallet"

# Define which modules/files to include
include_modules = [
    "core/keys.py",
    "core/wallet.py",
    "core/address.py",
    "core/transactions.py",
    "core/secure_storage.py",
    "utils/security_validator.py",
    "utils/logger.py",
    "__init__.py"
]

# Also include these bridge modules that will be accessible via WASM
bridge_modules = [
    ("api/services/wallet_bridge.py", "wasm_bridge.py")
]

def create_wasm_build():
    """Create the WebAssembly build structure"""
    print("Creating WebAssembly build structure...")
    
    # Create directories
    os.makedirs(wasm_build_dir, exist_ok=True)
    os.makedirs(wasm_src_dir, exist_ok=True)
    os.makedirs(wasm_src_dir / "core", exist_ok=True)
    os.makedirs(wasm_src_dir / "utils", exist_ok=True)
    
    # Copy the wallet core modules
    for module_path in include_modules:
        src_path = dirac_src / module_path
        dst_path = wasm_src_dir / module_path
        
        print(f"Copying {src_path} -> {dst_path}")
        shutil.copy(src_path, dst_path)
    
    # Copy bridge modules
    for src_rel_path, dst_name in bridge_modules:
        src_path = project_root / src_rel_path
        dst_path = wasm_build_dir / dst_name
        
        print(f"Copying bridge module {src_path} -> {dst_path}")
        shutil.copy(src_path, dst_path)
    
    # Create a setup.py file for Pyodide to use
    with open(wasm_build_dir / "setup.py", "w") as f:
        f.write("""
from setuptools import setup, find_packages

setup(
    name="dirac_wallet",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "cryptography",
        "pycryptodome"
    ],
)
""")
    
    # Create a README
    with open(wasm_build_dir / "README.md", "w") as f:
        f.write("""# Dirac Wallet WebAssembly Build

This directory contains the Dirac Wallet code prepared for WebAssembly compilation
via Pyodide. The code is loaded at runtime by the browser.

## Usage

In your React component:

```javascript
import { useEffect, useState } from 'react';
import { loadPyodide } from 'pyodide';

function WalletComponent() {
  const [wallet, setWallet] = useState(null);
  
  useEffect(() => {
    async function loadWallet() {
      // Load Pyodide
      const pyodide = await loadPyodide();
      
      // Load the dirac_wallet package
      await pyodide.loadPackagesFromImports('import micropip; await micropip.install("./wasm/dirac_wallet-0.1.0-py3-none-any.whl")');
      
      // Import the wallet bridge
      await pyodide.runPythonAsync(`
        import wasm_bridge
        wallet_bridge = wasm_bridge.WalletWasmBridge()
        wallet_bridge.setup()
      `);
      
      // Get the bridge instance
      const walletBridge = pyodide.globals.get('wallet_bridge');
      setWallet(walletBridge);
    }
    
    loadWallet();
  }, []);
  
  // Use the wallet...
}
```
""")
    
    # Create a requirements.txt file
    with open(wasm_build_dir / "requirements.txt", "w") as f:
        f.write("""
cryptography>=41.0.0
pycryptodome>=3.18.0
""")

    print("\nWebAssembly build structure created successfully!")
    print(f"Build directory: {wasm_build_dir}")
    print("\nNext steps:")
    print("1. Install Pyodide in your Next.js application:")
    print("   npm install pyodide")
    print("2. Create a loader component to initialize the wallet")
    print("3. Access the wallet functions through the bridge")

if __name__ == "__main__":
    create_wasm_build() 