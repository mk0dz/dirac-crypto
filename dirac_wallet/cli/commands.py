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
from solders.transaction import Transaction
from datetime import datetime

from ..core.wallet import DiracWallet, TransactionRecord
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


def print_transaction_history(transactions):
    """Print transaction history in a formatted table"""
    table = Table(title="Transaction History", box=box.ROUNDED)
    table.add_column("Date", style="cyan", width=10)
    table.add_column("Type", style="cyan", width=10)
    table.add_column("Amount", style="green", width=12)
    table.add_column("Fee", style="red", width=10)
    table.add_column("Status", style="yellow", width=10)
    table.add_column("Signature", style="magenta", width=15)
    
    for tx in transactions:
        # Format date
        try:
            date_str = tx.get('timestamp', '')
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    # If we can't parse the date, just use the first 10 chars
                    date = date_str[:10] if len(date_str) >= 10 else date_str
            else:
                date = "Unknown"
        except Exception:
            date = "Unknown"
            
        # Format amount with + or - prefix
        try:
            amount = float(tx.get('amount', 0.0))
            amount_str = f"{amount:.6f}"
        except (ValueError, TypeError):
            amount_str = "0.000000"
            
        # Add +/- prefix based on transaction direction
        try:
            sender = tx.get('sender', '')
            recipient = tx.get('recipient', '')
            wallet_address = tx.get('wallet_address', '')
            
            # If wallet address not provided, use the current display context
            if not wallet_address and sender == recipient:
                # Self-transfer
                amount_str = f"{amount_str}"
            elif not wallet_address:
                # Assume outgoing by default
                amount_str = f"-{amount_str}"
            elif sender == wallet_address and recipient != wallet_address:
                # Outgoing transaction
                amount_str = f"-{amount_str}"
            elif recipient == wallet_address and sender != wallet_address:
                # Incoming transaction
                amount_str = f"+{amount_str}"
            else:
                # Neutral (like self-transfer)
                amount_str = f"{amount_str}"
        except Exception:
            # Keep the amount as is if we can't determine direction
            pass
                
        # Format signature to be shorter
        try:
            sig = str(tx.get('signature', ''))
            if len(sig) > 12:
                sig = f"{sig[:6]}...{sig[-6:]}"
        except Exception:
            sig = "Unknown"
            
        # Format fee
        try:
            fee = float(tx.get('fee', 0.0))
            fee_str = f"{fee:.6f}"
        except (ValueError, TypeError):
            fee_str = "0.000000"
            
        # Get transaction type
        tx_type = str(tx.get('type', 'unknown'))
        
        # Get status
        status = str(tx.get('status', 'unknown'))
        
        table.add_row(
            date,
            tx_type,
            amount_str,
            fee_str,
            status,
            sig
        )
    
    console.print(table)


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
@click.option('--network', '-n', default='devnet', type=click.Choice(['testnet', 'devnet', 'mainnet']), 
              help='Solana network to use')
@click.option('--path', '-p', help='Path to save wallet file')
@click.argument('name', required=True)
def create(network, path, name):
    """Create a new quantum-resistant wallet"""
    try:
        if not path:
            wallet_dir = Path.home() / ".dirac_wallet"
            # Ensure wallet directory exists
            wallet_dir.mkdir(parents=True, exist_ok=True)
            path = wallet_dir / f"{name}_{network}.dwf"
        
        # Ensure wallet file doesn't already exist
        if Path(path).exists():
            print_error(f"Wallet already exists at {path}")
            print_info("Use a different name or delete the existing wallet first")
            return
            
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
@click.option('--network', '-n', default='devnet', type=click.Choice(['testnet', 'devnet', 'mainnet']), 
              help='Solana network to use')
@click.argument('name', required=True)
def balance(path, network, name):
    """Check wallet balance"""
    try:
        if not path:
            wallet_path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
            path = wallet_path
        if not Path(path).exists():
            print_error(f"Wallet not found at {path}")
            print_info(f"Create or import a wallet for '{name}' on network '{network}'")
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
@click.option('--network', '-n', default='devnet', type=click.Choice(['testnet', 'devnet', 'mainnet']), 
              help='Solana network to use')
@click.argument('name', required=True)
def info(path, network, name):
    """Show wallet information"""
    try:
        if not path:
            wallet_path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
            path = wallet_path
        if not Path(path).exists():
            print_error(f"Wallet not found at {path}")
            print_info(f"Create or import a wallet for '{name}' on network '{network}'")
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
@click.option('--network', '-n', default='devnet', type=click.Choice(['testnet', 'devnet', 'mainnet']), 
              help='Solana network to use')
@click.argument('name', required=True)
@click.argument('recipient', required=True)
@click.argument('amount', required=True, type=float)
def send(path, network, name, recipient, amount):
    """Send SOL to another address"""
    try:
        if not path:
            wallet_path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
            path = wallet_path
        if not Path(path).exists():
            print_error(f"Wallet not found at {path}")
            print_info(f"Create or import a wallet for '{name}' on network '{network}'")
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
                    
                    # Check balance first
                    balance = await client.get_balance(wallet.solana_address)
                    if balance < amount:
                        print_error(f"Insufficient balance: {balance} SOL")
                        print_info(f"Required: {amount} SOL")
                        return "Insufficient balance"
                    
                    # Create transaction
                    tx = QuantumTransaction(wallet)
                    tx.create_transfer(recipient, lamports)
                    
                    # Get recent blockhash
                    blockhash = await client.get_recent_blockhash()
                    if not blockhash:
                        print_error("Failed to get recent blockhash")
                        return "Network error"
                    print_info("Got recent blockhash...")
                    
                    # Sign and prepare transaction
                    try:
                        raw_tx, metadata = tx.prepare_for_broadcast(str(blockhash))
                        print_info("Transaction signed with quantum signature...")
                    except Exception as e:
                        print_error(f"Failed to sign transaction: {str(e)}")
                        return "Signing error"
                    
                    # Submit transaction
                    try:
                        result = await client.submit_quantum_transaction(Transaction.from_bytes(raw_tx))
                        tx_id = result["signature"]
                        print_success(f"Transaction submitted!")
                        print_info(f"Transaction ID: {tx_id}")
                        
                        # Wait for confirmation
                        print_info("Waiting for confirmation...")
                        confirmed = False
                        confirmation_status = None
                        for _ in range(5):  # Try for 5 attempts
                            status = await client.get_transaction_status(tx_id)
                            confirmation_status = status
                            if status.get("confirmed"):
                                print_success("Transaction confirmed!")
                                confirmed = True
                                break
                            elif status.get("error"):
                                print_error(f"Transaction failed: {status['error']}")
                                break
                            await asyncio.sleep(2)
                        
                        if not confirmed:
                            print_error("Transaction confirmation timed out")
                            print_info("Check the transaction status later using the transaction ID")
                        
                        # Show final balance
                        new_balance = await client.get_balance(wallet.solana_address)
                        print_info(f"New balance: {new_balance} SOL")
                        
                        # Record transaction in wallet history
                        tx_record = {
                            "signature": tx_id,
                            "timestamp": datetime.now().isoformat(),
                            "amount": float(amount),
                            "sender": wallet.solana_address,
                            "recipient": recipient,
                            "status": "confirmed" if confirmed else "pending",
                            "fee": 0.000005,  # Standard fee
                            "type": "transfer",
                            "memo": None
                        }
                        wallet.add_transaction(tx_record)
                        wallet.save(password)
                        
                        return {
                            "success": True,
                            "tx_id": tx_id,
                            "new_balance": new_balance
                        }
                        
                    except Exception as e:
                        print_error(f"Failed to submit transaction: {str(e)}")
                        return "Submission error"
                    
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
@click.option('--show-alternatives', '-a', is_flag=True, help='Show alternative ways to get SOL')
@click.option('--use-faucet', '-f', is_flag=True, help='Use SolFaucet.com instead of RPC airdrop')
@click.argument('name', required=True)
@click.argument('amount', required=False, type=float, default=1.0)
def airdrop(path, network, show_alternatives, use_faucet, name, amount):
    """Request SOL airdrop (devnet/testnet only)
    
    Examples:
      dirac-wallet airdrop my_wallet            # Request 1 SOL on devnet
      dirac-wallet airdrop my_wallet 2.0        # Request 2 SOL on devnet
      dirac-wallet airdrop my_wallet --network testnet  # Request on testnet
      dirac-wallet airdrop my_wallet -a         # Show alternative SOL sources
      dirac-wallet airdrop my_wallet -f         # Try faucet API directly
      
    Note:
      If regular airdrop fails, the command will automatically try alternative methods.
      Some networks have rate limits or may restrict airdrops. In that case, use -a to
      see other ways to get SOL.
    """
    try:
        if network == 'mainnet':
            print_error("Airdrop not available on mainnet")
            return
            
        if not path:
            wallet_path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
            path = wallet_path
        if not Path(path).exists():
            print_error(f"Wallet not found at {path}")
            print_info(f"Create or import a wallet for '{name}' on network '{network}'")
            return
        
        wallet = DiracWallet(str(path), network=network)
        password = get_password()
        
        if wallet.unlock(password):
            async def request_airdrop():
                client = QuantumSolanaClient(network=network)
                try:
                    await client.connect()
                    
                    # If user requests alternatives directly, show them
                    if show_alternatives:
                        alternatives = await client.get_airdrop_alternatives(wallet.solana_address)
                        return {"alternatives": alternatives}
                    
                    # If user wants to use faucet directly
                    if use_faucet:
                        print_info(f"Requesting {amount} SOL from faucet...")
                        faucet_result = await client.request_faucet_airdrop(wallet.solana_address, amount)
                        if faucet_result.get("success"):
                            print_success(f"Faucet airdrop successful!")
                            # Check the balance to confirm
                            try:
                                await asyncio.sleep(2)  # Wait for confirmation
                                new_balance = await client.get_balance(wallet.solana_address)
                                print_info(f"Current balance: {new_balance:.6f} SOL")
                            except Exception:
                                pass
                            return {"success": True}
                        else:
                            return {"error": faucet_result.get("error", "Unknown faucet error"), 
                                    "alternatives": await client.get_airdrop_alternatives(wallet.solana_address)}
                    
                    # Try the regular RPC airdrop first
                    print_info(f"Requesting {amount} SOL airdrop via RPC...")
                    
                    try:
                        tx_id = await client.request_airdrop(wallet.solana_address, amount)
                        if not tx_id:
                            return {"error": "Airdrop request failed: No transaction ID returned"}
                            
                        print_info(f"Airdrop request submitted: {tx_id}")
                        
                        print_info("Waiting for confirmation...")
                        try:
                            status = await client.get_transaction_status(tx_id)
                            if status.get("confirmed"):
                                print_success(f"Airdrop confirmed! Added {amount} SOL to your wallet.")
                                # Verify the balance update
                                try:
                                    new_balance = await client.get_balance(wallet.solana_address)
                                    print_info(f"Current balance: {new_balance:.6f} SOL")
                                except Exception:
                                    # If we can't get the balance, it's not a critical error
                                    pass
                                return {"success": True}
                            else:
                                error_msg = status.get('error', 'Unknown error')
                                print_error(f"RPC airdrop failed: {error_msg}")
                                
                                # Try the faucet as fallback
                                print_info("Trying faucet airdrop as fallback...")
                                faucet_result = await client.request_faucet_airdrop(wallet.solana_address, amount)
                                if faucet_result.get("success"):
                                    print_success(f"Faucet airdrop successful!")
                                    # Check the balance to confirm
                                    try:
                                        await asyncio.sleep(2)  # Wait for confirmation
                                        new_balance = await client.get_balance(wallet.solana_address)
                                        print_info(f"Current balance: {new_balance:.6f} SOL")
                                    except Exception:
                                        pass
                                    return {"success": True}
                                else:
                                    return {"error": faucet_result.get("error", "Unknown faucet error"), 
                                            "alternatives": await client.get_airdrop_alternatives(wallet.solana_address)}
                        except Exception as e:
                            print_error(f"Error confirming airdrop: {str(e)}")
                            
                            # Try the faucet as fallback
                            print_info("Trying faucet airdrop as fallback...")
                            faucet_result = await client.request_faucet_airdrop(wallet.solana_address, amount)
                            if faucet_result.get("success"):
                                print_success(f"Faucet airdrop successful!")
                                # Check the balance to confirm
                                try:
                                    await asyncio.sleep(2)  # Wait for confirmation
                                    new_balance = await client.get_balance(wallet.solana_address)
                                    print_info(f"Current balance: {new_balance:.6f} SOL")
                                except Exception:
                                    pass
                                return {"success": True}
                            else:
                                return {"error": faucet_result.get("error", "Unknown faucet error"), 
                                        "alternatives": await client.get_airdrop_alternatives(wallet.solana_address)}
                    except ValueError as e:
                        # Specific errors raised by the client
                        print_error(f"RPC airdrop failed: {str(e)}")
                        
                        # Try the faucet as fallback
                        print_info("Trying faucet airdrop as fallback...")
                        faucet_result = await client.request_faucet_airdrop(wallet.solana_address, amount)
                        if faucet_result.get("success"):
                            print_success(f"Faucet airdrop successful!")
                            # Check the balance to confirm
                            try:
                                await asyncio.sleep(2)  # Wait for confirmation
                                new_balance = await client.get_balance(wallet.solana_address)
                                print_info(f"Current balance: {new_balance:.6f} SOL")
                            except Exception:
                                pass
                            return {"success": True}
                        else:
                            return {"error": faucet_result.get("error", "Unknown faucet error"), 
                                    "alternatives": await client.get_airdrop_alternatives(wallet.solana_address)}
                    except Exception as e:
                        print_error(f"RPC airdrop failed: {str(e)}")
                        
                        # Try the faucet as fallback
                        print_info("Trying faucet airdrop as fallback...")
                        faucet_result = await client.request_faucet_airdrop(wallet.solana_address, amount)
                        if faucet_result.get("success"):
                            print_success(f"Faucet airdrop successful!")
                            # Check the balance to confirm
                            try:
                                await asyncio.sleep(2)  # Wait for confirmation
                                new_balance = await client.get_balance(wallet.solana_address)
                                print_info(f"Current balance: {new_balance:.6f} SOL")
                            except Exception:
                                pass
                            return {"success": True}
                        else:
                            return {"error": faucet_result.get("error", "Unknown faucet error"), 
                                    "alternatives": await client.get_airdrop_alternatives(wallet.solana_address)}
                    
                except Exception as e:
                    return {"error": f"Network connection error: {str(e)}", "alternatives": await client.get_airdrop_alternatives(wallet.solana_address)}
                finally:
                    await client.disconnect()
            
            result = asyncio.run(request_airdrop())
            
            # Handle the result based on the returned dictionary
            if "error" in result:
                print_error(result["error"])
                # Provide helpful tips for specific errors
                if "429" in result["error"] or "rate limit" in result["error"].lower():
                    print_info("You've reached the rate limit. Wait a few seconds and try again.")
                elif "maximum allowed" in result["error"].lower():
                    print_info("Try requesting a smaller amount (e.g. 1.0 SOL)")
                
                # If we have alternatives, display them
                if "alternatives" in result:
                    alternatives = result["alternatives"]
                    print_info("\nAlternative methods to get SOL:")
                    
                    # Display web faucets
                    web_faucets = alternatives.get("web_faucets", [])
                    if web_faucets:
                        print_info("\n🌐 Web Faucets:")
                        for faucet in web_faucets:
                            console.print(f"  • {faucet}", style="blue")
                    
                    # Display CLI command
                    cli_command = alternatives.get("cli_command")
                    if cli_command:
                        print_info("\n💻 Command Line:")
                        console.print(f"  • {cli_command}", style="blue")
                    
                    # Display Discord faucets
                    discord_faucets = alternatives.get("discord_faucets")
                    if discord_faucets:
                        print_info("\n🎮 Discord Communities:")
                        console.print(f"  • {discord_faucets}", style="blue")
                    
                    # Display wallet address for convenience
                    address = alternatives.get("address")
                    if address:
                        print_info("\n📋 Your wallet address (for copying):")
                        console.print(f"  {address}", style="green")
            
            # If alternatives were directly requested
            elif "alternatives" in result:
                alternatives = result["alternatives"]
                print_info(f"\nAlternative methods to get SOL on {network}:")
                
                # Display web faucets
                web_faucets = alternatives.get("web_faucets", [])
                if web_faucets:
                    print_info("\n🌐 Web Faucets:")
                    for faucet in web_faucets:
                        console.print(f"  • {faucet}", style="blue")
                
                # Display CLI command
                cli_command = alternatives.get("cli_command")
                if cli_command:
                    print_info("\n💻 Command Line:")
                    console.print(f"  • {cli_command}", style="blue")
                
                # Display Discord faucets
                discord_faucets = alternatives.get("discord_faucets")
                if discord_faucets:
                    print_info("\n🎮 Discord Communities:")
                    console.print(f"  • {discord_faucets}", style="blue")
                
                # Display wallet address for convenience
                address = alternatives.get("address")
                if address:
                    print_info("\n📋 Your wallet address (for copying):")
                    console.print(f"  {address}", style="green")
                
        else:
            print_error("Failed to unlock wallet")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


@cli.command(name="list-wallets")
@click.option('--network', '-n', help='Show wallets for specific network')
def list_wallets(network):
    """List all available wallets"""
    try:
        wallet_dir = Path.home() / ".dirac_wallet"
        if not wallet_dir.exists():
            print_info("No wallets found")
            return
        
        wallet_files = list(wallet_dir.glob("*.dwf"))
        
        if not wallet_files:
            print_info("No wallets found")
            return
        
        table = Table(title="Available Wallets", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Network", style="magenta")
        table.add_column("Path", style="white")
        
        for file in wallet_files:
            # Extract name and network from filename (name_network.dwf)
            filename = file.stem
            
            if "_" in filename:
                # Handle the special case where the wallet might have format name_something_network.dwf
                # Example: my_test_wallet_devnet.dwf
                if filename.endswith(("_devnet", "_testnet", "_mainnet")):
                    network_part = filename.split("_")[-1]
                    name_part = filename[:-len(network_part)-1]  # Remove _network from the end
                    table.add_row(name_part, network_part, str(file))
                else:
                    # Default parsing for name_network.dwf
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        name = parts[0]
                        net = parts[1]
                        table.add_row(name, net, str(file))
            else:
                # Handle files without network in the name
                table.add_row(filename, "unknown", str(file))
        
        if table.row_count == 0:
            if network:
                print_info(f"No wallets found for network: {network}")
            else:
                print_info("No wallets found")
        else:
            console.print(table)
        
    except Exception as e:
        print_error(f"Error: {str(e)}")


@cli.command()
@click.option('--path', '-p', help='Path to wallet file')
@click.option('--network', '-n', default='devnet', type=click.Choice(['testnet', 'devnet', 'mainnet']), 
              help='Solana network to use')
@click.option('--limit', '-l', type=int, default=10, help='Maximum number of transactions to show')
@click.option('--refresh', '-r', is_flag=True, help='Refresh transaction history from network')
@click.argument('name', required=True)
def history(path, network, limit, refresh, name):
    """Show transaction history for wallet"""
    try:
        if not path:
            wallet_path = Path.home() / ".dirac_wallet" / f"{name}_{network}.dwf"
            path = wallet_path
        if not Path(path).exists():
            print_error(f"Wallet not found at {path}")
            print_info(f"Create or import a wallet for '{name}' on network '{network}'")
            return
        
        wallet = DiracWallet(str(path), network=network)
        password = get_password()
        
        if wallet.unlock(password):
            # Get transaction history from wallet
            transactions = wallet.get_transaction_history()
            
            # If refresh flag is set, get transactions from network
            if refresh:
                print_info("Refreshing transaction history from network...")
                
                async def fetch_transactions():
                    client = QuantumSolanaClient(network=network)
                    try:
                        await client.connect()
                        # Get recent transactions for the address
                        new_txs = await client.get_transaction_history(wallet.solana_address)
                        return new_txs
                    except Exception as e:
                        return {"error": str(e)}
                    finally:
                        await client.disconnect()
                
                network_txs = asyncio.run(fetch_transactions())
                
                if isinstance(network_txs, dict) and "error" in network_txs:
                    print_error(f"Failed to refresh transactions: {network_txs['error']}")
                else:
                    # Add new transactions to wallet history
                    added_count = 0
                    for tx in network_txs:
                        try:
                            # Clean the transaction data to match TransactionRecord format
                            # Remove any fields not in the TransactionRecord model
                            if 'wallet_address' in tx:
                                del tx['wallet_address']
                                
                            # Ensure all required fields are present
                            if 'signature' not in tx or not tx['signature']:
                                continue
                                
                            # Add transaction to wallet history
                            wallet.add_transaction(tx)
                            added_count += 1
                        except Exception as e:
                            print_error(f"Error processing transaction: {str(e)}")
                    
                    # Save updated wallet
                    wallet.save(password)
                    
                    print_success(f"Added {added_count} transactions from network")
                    
                    # Get updated transaction list
                    transactions = wallet.get_transaction_history()
            
            # Sort transactions by timestamp (newest first)
            transactions.sort(key=lambda tx: tx.get('timestamp', ''), reverse=True)
            
            # Limit to requested number
            transactions = transactions[:limit]
            
            if transactions:
                print_transaction_history(transactions)
            else:
                print_info("No transaction history found")
                if not refresh:
                    print_info("Use --refresh to fetch transactions from network")
        else:
            print_error("Failed to unlock wallet")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


if __name__ == "__main__":
    cli()
