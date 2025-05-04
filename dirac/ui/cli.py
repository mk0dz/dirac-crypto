"""
Command-line interface for the Dirac wallet.
"""

import os
import sys
import time
from typing import Optional, List
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

from dirac.wallet import DiracWallet, Transaction
from dirac.crypto import QuantumKeyring
from dirac.solana import SolanaClient

def create_app():
    """Create the CLI application."""
    app = typer.Typer(help="Dirac Quantum-Resistant Wallet CLI")
    
    # Create global console for rich output
    console = Console()
    
    # Create global wallet instance
    wallet = DiracWallet()
    
    # Create global Solana client
    solana = SolanaClient()
    
    @app.command("create")
    def create_wallet(
        name: str,
        sig_algo: str = typer.Option("sphincs", "--sig-algo", "-s", 
                                     help="Signature algorithm (sphincs, lamport, dilithium)"),
        hash_algo: str = typer.Option("grover", "--hash-algo", "-h", 
                                     help="Hash algorithm (standard, improved, grover, shor, quantum)"),
        security: int = typer.Option(3, "--security", "-l", 
                                    help="Security level (1-5)"),
        backup: bool = typer.Option(True, "--backup/--no-backup", 
                                    help="Generate backup keys"),
        force: bool = typer.Option(False, "--force", "-f", 
                                  help="Overwrite existing wallet"),
        network: str = typer.Option("testnet", "--network", "-n", 
                                   help="Network (mainnet, testnet, devnet, local)")
    ):
        """Create a new wallet with quantum-resistant algorithms."""
        
        # Validate algorithm choices
        valid_sig_algos = ["sphincs", "lamport", "dilithium"]
        valid_hash_algos = ["standard", "improved", "grover", "shor", "quantum"]
        
        if sig_algo not in valid_sig_algos:
            console.print(f"[bold red]Error:[/] Invalid signature algorithm. Valid options: {', '.join(valid_sig_algos)}")
            return
            
        if hash_algo not in valid_hash_algos:
            console.print(f"[bold red]Error:[/] Invalid hash algorithm. Valid options: {', '.join(valid_hash_algos)}")
            return
            
        if security < 1 or security > 5:
            console.print(f"[bold red]Error:[/] Security level must be between 1 and 5")
            return
        
        try:
            # Initialize keyring with chosen algorithms
            keyring = QuantumKeyring(
                signature_algorithm=sig_algo,
                hash_algorithm=hash_algo,
                security_level=security
            )
            
            # Create a new wallet instance with this keyring
            new_wallet = DiracWallet(keyring, network=network)
            
            # Create the wallet
            address = new_wallet.create_wallet(name, overwrite=force)
            
            console.print(Panel.fit(
                f"[bold green]Wallet created successfully![/]\n\n"
                f"Name: [cyan]{name}[/]\n"
                f"Address: [yellow]{address}[/]\n"
                f"Solana Address: [yellow]{new_wallet.solana_address}[/]\n"
                f"Signature algorithm: [magenta]{sig_algo}[/]\n"
                f"Hash algorithm: [magenta]{hash_algo}[/]\n"
                f"Security level: [magenta]{security}[/]\n"
                f"Network: [blue]{network}[/]",
                title="New Wallet"
            ))
        except FileExistsError:
            console.print(f"[bold red]Error:[/] Wallet [yellow]{name}[/] already exists. Use --force to overwrite.")
        except Exception as e:
            console.print(f"[bold red]Error creating wallet:[/] {str(e)}")
    
    @app.command("list")
    def list_wallets():
        """List all available wallets."""
        try:
            wallets = wallet.list_wallets()
            
            if not wallets:
                console.print("[yellow]No wallets found. Create one with 'create' command.[/]")
                return
            
            table = Table(title="Available Wallets")
            table.add_column("Name", style="cyan")
            table.add_column("Address", style="yellow")
            table.add_column("Solana Address", style="green")
            table.add_column("Algorithm", style="magenta")
            table.add_column("Created", style="blue")
            
            for w in wallets:
                # Safely get values with defaults for missing fields
                name = w.get("name", "")
                address = w.get("address", "")
                solana_address = w.get("solana_address", "")
                algorithm = w.get("algorithm", "")
                
                # Format created date if available
                created = "Unknown"
                if "created_at" in w and w["created_at"]:
                    try:
                        dt = datetime.fromtimestamp(w["created_at"])
                        created = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                table.add_row(name, address, solana_address, algorithm, created)
            
            console.print(table)
        except Exception as e:
            console.print(f"[bold red]Error listing wallets:[/] {str(e)}")
    
    @app.command("balance")
    def check_balance(name: str):
        """Check wallet balance."""
        try:
            wallet.load_wallet(name)
            
            # Update Solana client to match wallet network
            solana.network = wallet.network
            
            # Use the Solana client directly to get balance
            balance = solana.get_balance(wallet.solana_address)
            
            console.print(Panel.fit(
                f"[bold cyan]{name}[/]\n\n"
                f"Address: [yellow]{wallet.address or 'Unknown'}[/]\n"
                f"Solana Address: [green]{wallet.solana_address or 'Not available'}[/]\n"
                f"Balance: [green]{balance} SOL[/]\n"
                f"Network: [blue]{wallet.network}[/]",
                title="Wallet Balance"
            ))
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/] Wallet [yellow]{name}[/] not found.")
        except Exception as e:
            console.print(f"[bold red]Error checking balance:[/] {str(e)}")
    
    @app.command("send")
    def send_transaction(
        recipient: str,
        amount: float,
        wallet_name: str = typer.Option(..., "--wallet", help="Source wallet name"),
    ):
        """Send SOL to a recipient."""
        try:
            wallet.load_wallet(wallet_name)
            
            # Confirm the transaction
            console.print(
                f"Sending [green]{amount} SOL[/] from [cyan]{wallet_name}[/] "
                f"to [yellow]{recipient}[/]"
            )
            
            # Send the transaction
            with Progress() as progress:
                task = progress.add_task("[green]Sending transaction...", total=100)
                
                # Simulate progress
                progress.update(task, advance=50)
                tx_id = wallet.send_transaction(recipient, amount)
                progress.update(task, advance=50)
            
            console.print(Panel.fit(
                f"[bold green]Transaction sent![/]\n\n"
                f"From: [cyan]{wallet_name}[/]\n"
                f"To: [yellow]{recipient}[/]\n"
                f"Amount: [green]{amount} SOL[/]\n"
                f"Transaction ID: [magenta]{tx_id}[/]",
                title="Transaction Details"
            ))
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/] Wallet [yellow]{wallet_name}[/] not found.")
        except ValueError as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
        except Exception as e:
            console.print(f"[bold red]Error sending transaction:[/] {str(e)}")
    
    @app.command("history")
    def transaction_history(wallet_name: str):
        """View transaction history for a wallet."""
        try:
            wallet.load_wallet(wallet_name)
            transactions = wallet.get_transaction_history()
            
            if not transactions:
                console.print(f"[yellow]No transactions found for wallet [cyan]{wallet_name}[/].[/]")
                return
            
            table = Table(title=f"Transaction History for {wallet_name}")
            table.add_column("Date", style="blue")
            table.add_column("Type", style="cyan")
            table.add_column("Amount", style="green")
            table.add_column("Recipient/Sender", style="yellow")
            table.add_column("Status", style="magenta")
            table.add_column("ID", style="dim")
            
            for tx in transactions:
                # Format datetime
                date_str = datetime.fromtimestamp(tx.timestamp).strftime("%Y-%m-%d %H:%M")
                
                # Determine if sent or received
                tx_type = "Sent"
                recipient_sender = tx.recipient
                if tx.sender != wallet.address:
                    tx_type = "Received"
                    recipient_sender = tx.sender
                
                # Format amount with sign
                amount = f"{tx.amount:+.4f}" if tx_type == "Received" else f"{-tx.amount:.4f}"
                
                # Truncate transaction ID
                short_id = tx.tx_id[:10] + "..." if len(tx.tx_id) > 10 else tx.tx_id
                
                table.add_row(date_str, tx_type, amount, recipient_sender, tx.status, short_id)
            
            console.print(table)
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/] Wallet [yellow]{wallet_name}[/] not found.")
        except Exception as e:
            console.print(f"[bold red]Error getting transaction history:[/] {str(e)}")
    
    @app.command("export")
    def export_wallet(
        name: str,
        output: str = typer.Option(None, "--output", help="Output directory"),
        include_private: bool = typer.Option(False, "--include-private", help="Include private keys (unsafe)"),
    ):
        """Export a wallet to a file."""
        try:
            # Set default output directory if not specified
            if output is None:
                output = os.path.join(os.getcwd(), "exported_wallets")
            
            # Export the wallet
            export_path = wallet.export_wallet(name, output, include_private)
            
            console.print(Panel.fit(
                f"[bold green]Wallet exported successfully![/]\n\n"
                f"Wallet: [cyan]{name}[/]\n"
                f"Exported to: [yellow]{export_path}[/]\n"
                f"Private keys included: [{'green' if include_private else 'red'}]{include_private}[/]",
                title="Wallet Export"
            ))
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/] Wallet [yellow]{name}[/] not found.")
        except Exception as e:
            console.print(f"[bold red]Error exporting wallet:[/] {str(e)}")
    
    @app.command("import")
    def import_wallet(
        file_path: str,
        name: Optional[str] = typer.Option(None, "--name", help="New wallet name"),
    ):
        """Import a wallet from a file."""
        try:
            name = wallet.import_wallet(file_path, name)
            
            console.print(Panel.fit(
                f"[bold green]Wallet imported successfully![/]\n\n"
                f"Name: [cyan]{name}[/]\n"
                f"Address: [yellow]{wallet.address}[/]\n"
                f"Solana Address: [yellow]{wallet.solana_address}[/]",
                title="Wallet Import"
            ))
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/] Import file [yellow]{file_path}[/] not found.")
        except FileExistsError as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
        except Exception as e:
            console.print(f"[bold red]Error importing wallet:[/] {str(e)}")
    
    @app.command("airdrop")
    def request_airdrop(
        wallet_name: str,
        amount: float = typer.Option(1.0, "--amount", help="Amount of SOL to request"),
    ):
        """Request a SOL airdrop (testnet/devnet only)."""
        try:
            wallet.load_wallet(wallet_name)
            
            # Check if network is valid for airdrops
            if wallet.network not in ["testnet", "devnet", "local"]:
                console.print(f"[bold red]Error:[/] Airdrops are only available on testnet, devnet, or local networks.")
                console.print(f"Current network: [yellow]{wallet.network}[/]")
                console.print("Use [cyan]network[/] command to change networks.")
                return
            
            # Update Solana client to match wallet network
            solana.network = wallet.network
            solana.rpc_url = wallet.rpc_url
            
            # Show more detailed network info
            console.print(f"Requesting [green]{amount} SOL[/] airdrop to [cyan]{wallet_name}[/]...")
            console.print(f"Solana address: [yellow]{wallet.solana_address}[/]")
            console.print(f"Network: [blue]{wallet.network}[/] ([italic]{wallet.rpc_url}[/italic])")
            
            with Progress() as progress:
                task = progress.add_task("[green]Processing airdrop...", total=100)
                
                # Request airdrop
                progress.update(task, advance=30)
                tx_sig = solana.request_airdrop(wallet.solana_address, amount)
                progress.update(task, advance=70)
            
            if tx_sig:
                console.print(Panel.fit(
                    f"[bold green]Airdrop successful![/]\n\n"
                    f"Amount: [green]{amount} SOL[/]\n"
                    f"Wallet: [cyan]{wallet_name}[/]\n"
                    f"Network: [blue]{wallet.network}[/]\n"
                    f"Transaction: [magenta]{tx_sig[:20]}...[/]",
                    title="Airdrop Complete"
                ))
                
                # Wait a moment and check the balance
                time.sleep(2)
                balance = solana.get_balance(wallet.solana_address)
                console.print(f"Updated balance: [green]{balance} SOL[/]")
            else:
                console.print(Panel.fit(
                    f"[bold red]Airdrop failed![/]\n\n"
                    f"Wallet: [cyan]{wallet_name}[/]\n"
                    f"Network: [blue]{wallet.network}[/]",
                    title="Airdrop Failed"
                ))
                console.print("[yellow]Note: Testnet/devnet airdrops may be rate-limited or temporarily unavailable.[/]")
                console.print("[yellow]You can try again later or with a smaller amount.[/]")
                
                # Suggest alternatives
                if wallet.network == "devnet":
                    console.print("\n[cyan]Alternative: You can use the Solana CLI or a faucet website to request an airdrop:[/]")
                    console.print("1. CLI: [dim]solana airdrop 1 YOUR_ADDRESS --url https://api.devnet.solana.com[/]")
                    console.print("2. Visit [link=https://faucet.solana.com]https://faucet.solana.com[/link] and request an airdrop")
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/] Wallet [yellow]{wallet_name}[/] not found.")
        except Exception as e:
            console.print(f"[bold red]Error requesting airdrop:[/] {str(e)}")
    
    @app.command("network")
    def change_network(
        network: str = typer.Argument(..., help="Network to use (mainnet, testnet, devnet, local)"),
        wallet_name: Optional[str] = typer.Option(None, "--wallet", help="Wallet to update (if not provided, only changes default)"),
    ):
        """Change the wallet network."""
        try:
            valid_networks = ["mainnet", "testnet", "devnet", "local"]
            if network not in valid_networks:
                console.print(f"[bold red]Error:[/] Invalid network [yellow]{network}[/]")
                console.print(f"Valid networks: [green]{', '.join(valid_networks)}[/]")
                return
            
            # Update selected wallet if specified
            if wallet_name:
                wallet.load_wallet(wallet_name)
                wallet.change_network(network)
                console.print(f"Changed network for wallet [cyan]{wallet_name}[/] to [green]{network}[/]")
            else:
                # Just change the default for new wallets
                wallet.network = network
                console.print(f"Changed default network to [green]{network}[/]")
                console.print("[yellow]Note: This only affects new wallets and the current session.[/]")
            
            # Update Solana client network
            solana.network = network
        except FileNotFoundError:
            console.print(f"[bold red]Error:[/] Wallet [yellow]{wallet_name}[/] not found.")
        except Exception as e:
            console.print(f"[bold red]Error changing network:[/] {str(e)}")
    
    @app.command("backup")
    def list_backups(name: str):
        """List available backups for a wallet."""
        try:
            # List backups using the storage directly
            backups = wallet.storage.list_backups(name)
            
            if not backups:
                console.print(f"[yellow]No backups found for wallet [cyan]{name}[/].[/]")
                return
            
            table = Table(title=f"Backups for {name}")
            table.add_column("Date", style="blue")
            table.add_column("Time", style="cyan")
            table.add_column("Size", style="green")
            table.add_column("Path", style="dim")
            
            for backup in backups:
                # Format date and time
                ts = backup.get("timestamp", 0)
                if ts > 0:
                    dt = datetime.fromtimestamp(ts)
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M:%S")
                else:
                    date_str = "Unknown"
                    time_str = "Unknown"
                
                # Format size
                size_bytes = backup.get("size", 0)
                if size_bytes < 1024:
                    size_str = f"{size_bytes} bytes"
                else:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                
                # Format path (show only filename)
                path = backup.get("path", "")
                filename = os.path.basename(path)
                
                table.add_row(date_str, time_str, size_str, filename)
            
            console.print(table)
        except Exception as e:
            console.print(f"[bold red]Error listing backups:[/] {str(e)}")
    
    @app.command("restore")
    def restore_backup(
        name: str,
        timestamp: Optional[int] = typer.Option(None, "--timestamp", help="Specific backup timestamp to restore"),
    ):
        """Restore a wallet from backup."""
        try:
            # If timestamp is not provided, show available backups
            if timestamp is None:
                backups = wallet.storage.list_backups(name)
                
                if not backups:
                    console.print(f"[bold red]Error:[/] No backups found for wallet [cyan]{name}[/].")
                    return
                
                console.print(f"Available backups for wallet [cyan]{name}[/]:")
                
                for i, backup in enumerate(backups):
                    ts = backup.get("timestamp", 0)
                    if ts > 0:
                        dt = datetime.fromtimestamp(ts)
                        date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        date_str = "Unknown date"
                    
                    console.print(f"[green]{i+1}.[/] {date_str} [yellow](Timestamp: {ts})[/]")
                
                console.print(f"[yellow]Use 'restore {name} --timestamp <timestamp>' to restore a specific backup[/]")
                console.print(f"[yellow]Or 'restore {name} --timestamp 0' to restore the most recent backup[/]")
                return
            
            # Use timestamp 0 to indicate "most recent backup"
            actual_timestamp = None if timestamp == 0 else timestamp
            
            # Restore from backup
            restored_name = wallet.restore_from_backup(name, actual_timestamp)
            
            console.print(Panel.fit(
                f"[bold green]Wallet restored successfully![/]\n\n"
                f"Name: [cyan]{restored_name}[/]\n"
                f"Address: [yellow]{wallet.address}[/]\n"
                f"Solana Address: [yellow]{wallet.solana_address}[/]",
                title="Wallet Restored"
            ))
        except FileNotFoundError as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
        except ValueError as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
        except Exception as e:
            console.print(f"[bold red]Error restoring backup:[/] {str(e)}")
    
    return app 