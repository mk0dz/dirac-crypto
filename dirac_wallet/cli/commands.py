"""
Command Line Interface for Dirac-Wallet
"""
import click
import asyncio
import json
import sys
from pathlib import Path
from decimal import Decimal
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from ..core.wallet import DiracWallet
from ..core.transactions import QuantumTransaction
from ..network.solana_client import QuantumSolanaClient
from ..utils.logger import logger

console = Console()


def print_success(message):
    """Print success message in green"""
    console.print(f"✓ {message}", style="bold green")


def print_error(message):
    """Print error message in red"""
    console.print(f"✗ {message}", style="bold red")


def print_info(message):
    """Print info message in blue"""
    console.print(f"ℹ {message}", style="bold blue")


def print_wallet_info(wallet_info):
    """Print wallet information in a formatted table"""
    table = Table(title="Wallet Information", box=box.ROUNDED)
    table.add_column("Property", style="cyan", width=15)
    table.add_column("Value", style="white")
    
    for key, value in wallet_info.items():
        if key != "path":  # Skip full path for cleaner display
            table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(table)


def print_balance(address, balance):
    """Print balance information"""
    panel = Panel(
        f"[bold green]{balance:.6f} SOL[/bold green]",
        title=f"Balance for {address[:8]}...{address[-8:]}",
        border_style="green"
    )
    console.print(panel)


def get_password(prompt="Enter wallet password"):
    """Get password from user without echoing"""
    import getpass
    return getpass.getpass(f"{prompt}: ")


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Dirac-Wallet: Quantum-resistant Solana wallet"""
    pass


@cli.command()
@click.option('--network', '-n', default='testnet', type=click.Choice(['testnet', 'devnet', 'mainnet']), 
              help='Solana network to use')
@click.option('--path', '-p', help='Path to save wallet file')
@click.argument('name', required=False, default='default')
def create(network, path, name):
    """Create a new quantum-resistant wallet"""
    try:
        if not path:
            path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
        
        wallet = DiracWallet(str(path), network=network)
        
        # Get password
        while True:
            password = get_password("Create wallet password")
            confirm_password = get_password("Confirm password")
            if password == confirm_password:
                break
            print_error("Passwords do not match. Please try again.")
        
        result = wallet.create(password)
        
        print_success(f"Wallet created successfully!")
        print_info(f"Path: {result['path']}")
        print_info(f"Address: {result['address']}")
        print_info(f"Network: {result['network']}")
        
        click.echo("\n⚠️  Please save your password securely. There's no way to recover it!")
        
    except Exception as e:
        print_error(f"Failed to create wallet: {str(e)}")


@cli.command()
@click.option('--path', '-p', help='Path to wallet file')
@click.option('--network', '-n', default='testnet', type=click.Choice(['testnet', 'devnet', 'mainnet']), 
              help='Solana network to use')
@click.argument('name', required=False, default='default')
def balance(path, network, name):
    """Check wallet balance"""
    try:
        if not path:
            path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
        
        if not Path(path).exists():
            print_error(f"Wallet not found at {path}")
            return
        
        wallet = DiracWallet(str(path), network=network)
        password = get_password()
        
        if wallet.unlock(password):
            # Get balance from network
            async def get_balance():
                client = QuantumSolanaClient(network=network)
                try:
                    await client.connect()
                    balance = await client.get_balance(wallet.solana_address)
                    return balance
                except Exception as e:
                    return str(e)
                finally:
                    await client.disconnect()
            
            balance_result = asyncio.run(get_balance())
            
            if isinstance(balance_result, float):
                print_balance(wallet.solana_address, balance_result)
            else:
                print_error(f"Failed to get balance: {balance_result}")
                print_info("Make sure you're connected to the internet")
        else:
            print_error("Failed to unlock wallet")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


@cli.command()
@click.option('--path', '-p', help='Path to wallet file')
@click.option('--network', '-n', default='testnet', type=click.Choice(['testnet', 'devnet', 'mainnet']), 
              help='Solana network to use')
@click.argument('name', required=False, default='default')
def info(path, network, name):
    """Show wallet information"""
    try:
        if not path:
            path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
        
        if not Path(path).exists():
            print_error(f"Wallet not found at {path}")
            return
        
        wallet = DiracWallet(str(path), network=network)
        password = get_password()
        
        if wallet.unlock(password):
            wallet_info = wallet.get_info()
            print_wallet_info(wallet_info)
        else:
            print_error("Failed to unlock wallet")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


@cli.command()
@click.option('--path', '-p', help='Path to wallet file')
@click.option('--network', '-n', default='testnet', type=click.Choice(['testnet', 'devnet', 'mainnet']), 
              help='Solana network to use')
@click.argument('name', required=False, default='default')
@click.argument('recipient', required=True)
@click.argument('amount', required=True, type=float)
def send(path, network, name, recipient, amount):
    """Send SOL to another address"""
    try:
        if not path:
            path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
        
        if not Path(path).exists():
            print_error(f"Wallet not found at {path}")
            return
        
        wallet = DiracWallet(str(path), network=network)
        password = get_password()
        
        if wallet.unlock(password):
            lamports = int(Decimal(amount) * Decimal(10**9))
            
            async def send_transaction():
                client = QuantumSolanaClient(network=network)
                try:
                    # Connect to network
                    await client.connect()
                    print_info("Connected to Solana network...")
                    
                    # Create transaction
                    tx = QuantumTransaction(wallet)
                    tx.create_transfer(recipient, lamports)
                    
                    # Get recent blockhash
                    blockhash = await client.get_recent_blockhash()
                    print_info("Got recent blockhash...")
                    
                    # Sign and prepare transaction
                    raw_tx, metadata = tx.prepare_for_broadcast(str(blockhash))
                    print_info("Transaction signed with quantum signature...")
                    
                    # Submit transaction
                    result = await client.submit_quantum_transaction(raw_tx, metadata["signature"], metadata)
                    tx_id = result["transaction_id"]
                    print_success(f"Transaction submitted!")
                    print_info(f"Transaction ID: {tx_id}")
                    
                    # Wait for confirmation
                    print_info("Waiting for confirmation...")
                    status = await client.get_transaction_status(tx_id)
                    if status.get("confirmed"):
                        print_success("Transaction confirmed!")
                    else:
                        print_error(f"Transaction status: {status.get('error', 'Unknown error')}")
                    
                except Exception as e:
                    return str(e)
                finally:
                    await client.disconnect()
            
            result = asyncio.run(send_transaction())
            if isinstance(result, str):
                print_error(f"Failed to send transaction: {result}")
                
        else:
            print_error("Failed to unlock wallet")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


@cli.command()
@click.option('--path', '-p', help='Path to wallet file')
@click.option('--network', '-n', default='devnet', type=click.Choice(['devnet', 'testnet']), 
              help='Solana network to use (airdrop only on devnet/testnet)')
@click.argument('name', required=False, default='default')
@click.argument('amount', required=False, type=float, default=1.0)
def airdrop(path, network, name, amount):
    """Request SOL airdrop (devnet/testnet only)"""
    try:
        if network == 'mainnet':
            print_error("Airdrop not available on mainnet")
            return
            
        if not path:
            path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
        
        if not Path(path).exists():
            print_error(f"Wallet not found at {path}")
            return
        
        wallet = DiracWallet(str(path), network=network)
        password = get_password()
        
        if wallet.unlock(password):
            async def request_airdrop():
                client = QuantumSolanaClient(network=network)
                try:
                    await client.connect()
                    print_info(f"Requesting {amount} SOL airdrop...")
                    
                    tx_id = await client.request_airdrop(wallet.solana_address, amount)
                    print_info(f"Airdrop request submitted: {tx_id}")
                    
                    print_info("Waiting for confirmation...")
                    status = await client.get_transaction_status(tx_id)
                    if status.get("confirmed"):
                        print_success(f"Airdrop confirmed! Added {amount} SOL to your wallet.")
                    else:
                        print_error(f"Airdrop status: {status.get('error', 'Unknown error')}")
                    
                except Exception as e:
                    return str(e)
                finally:
                    await client.disconnect()
            
            result = asyncio.run(request_airdrop())
            if isinstance(result, str):
                print_error(f"Failed to request airdrop: {result}")
                
        else:
            print_error("Failed to unlock wallet")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


@cli.command()
@click.option('--network', '-n', help='Show wallets for specific network')
def list_wallets(network):
    """List all available wallets"""
    try:
        wallet_dir = Path.home() / ".dirac_wallet"
        if not wallet_dir.exists():
            print_info("No wallets found")
            return
        
        wallet_files = []
        for file in wallet_dir.glob("*.dwf"):
            wallet_files.append(file)
        
        if not wallet_files:
            print_info("No wallets found")
            return
        
        table = Table(title="Available Wallets", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Network", style="magenta")
        table.add_column("Path", style="white")
        
        for file in wallet_files:
            parts = file.stem.split('_')
            if len(parts) >= 2:
                name = parts[0]
                net = parts[1]
                if network is None or net == network:
                    table.add_row(name, net, str(file))
        
        console.print(table)
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


if __name__ == "__main__":
    cli()
