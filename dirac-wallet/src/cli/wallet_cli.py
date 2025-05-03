"""
Command-line interface for the Dirac quantum-resistant Solana wallet.
"""

import os
import sys
import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..wallet.wallet import DiracWallet
from ..crypto.keyring import QuantumKeyring
from .benchmark_cli import app as benchmark_app

app = typer.Typer(help="Dirac Quantum-Resistant Solana Wallet CLI")
console = Console()

# Add benchmark subcommand
app.add_typer(benchmark_app, name="benchmark", help="Run performance benchmarks")


@app.callback()
def callback():
    """
    Dirac Quantum-Resistant Solana Wallet CLI.
    """
    pass


@app.command("create")
def create_wallet(
    name: str = typer.Argument(..., help="Wallet name"),
    signature_algorithm: str = typer.Option(
        "sphincs", "--sig-algo", "-s", help="Signature algorithm (sphincs, dilithium, lamport)"
    ),
    hash_algorithm: str = typer.Option(
        "dirac_improved", "--hash-algo", "-h", 
        help="Hash algorithm (dirac_standard, dirac_improved, dirac_grover, dirac_shor, quantum_enhanced)"
    ),
    security_level: int = typer.Option(
        3, "--security", "-l", help="Security level (1-5, higher is more secure)"
    ),
    backup: bool = typer.Option(
        True, "--backup/--no-backup", help="Generate backup keys with different algorithms"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing wallet"
    ),
):
    """
    Create a new quantum-resistant wallet.
    """
    with console.status("Creating wallet with quantum-resistant keys..."):
        # Create keyring with specified algorithms
        keyring = QuantumKeyring(
            signature_algorithm=signature_algorithm,
            hash_algorithm=hash_algorithm,
            security_level=security_level,
            backup_algorithms=backup,
        )
        
        # Create wallet
        wallet = DiracWallet(keyring=keyring)
        
        try:
            address = wallet.create_wallet(name, overwrite=force)
            
            console.print(Panel(
                f"[bold green]Wallet created successfully![/]\n\n"
                f"Name: [cyan]{name}[/]\n"
                f"Address: [cyan]{address}[/]\n"
                f"Signature Algorithm: [yellow]{signature_algorithm}[/]\n"
                f"Hash Algorithm: [yellow]{hash_algorithm}[/]\n"
                f"Security Level: [yellow]{security_level}[/]\n"
                f"Backup Keys: [yellow]{'Yes' if backup else 'No'}[/]",
                title="New Wallet",
                border_style="green",
            ))
            
        except FileExistsError:
            console.print(f"[bold red]Wallet '{name}' already exists.[/] Use --force to overwrite.")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[bold red]Error creating wallet:[/] {str(e)}")
            raise typer.Exit(1)


@app.command("balance")
def check_balance(
    name: str = typer.Argument(..., help="Wallet name"),
):
    """
    Check wallet balance.
    """
    with console.status(f"Checking balance for wallet '{name}'..."):
        wallet = DiracWallet()
        
        try:
            # Load wallet
            wallet.load_wallet(name)
            
            # Get balance
            balance = wallet.get_balance()
            
            console.print(Panel(
                f"Balance: [bold green]{balance} SOL[/]",
                title=f"Wallet: {name}",
                border_style="blue",
            ))
            
        except FileNotFoundError:
            console.print(f"[bold red]Wallet '{name}' not found.[/]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[bold red]Error checking balance:[/] {str(e)}")
            raise typer.Exit(1)


@app.command("send")
def send_transaction(
    recipient: str = typer.Argument(..., help="Recipient address"),
    amount: float = typer.Argument(..., help="Amount of SOL to send"),
    wallet: str = typer.Option(..., "--wallet", "-w", help="Wallet name"),
):
    """
    Send SOL to a recipient.
    """
    with console.status(f"Sending {amount} SOL to {recipient}..."):
        wallet_instance = DiracWallet()
        
        try:
            # Load wallet
            wallet_instance.load_wallet(wallet)
            
            # Check balance
            balance = wallet_instance.get_balance()
            if balance < amount:
                console.print(f"[bold red]Insufficient balance.[/] You have {balance} SOL, but tried to send {amount} SOL.")
                raise typer.Exit(1)
            
            # Send transaction
            signature = wallet_instance.send_transaction(recipient, amount)
            
            console.print(Panel(
                f"[bold green]Transaction sent successfully![/]\n\n"
                f"From: [cyan]{wallet}[/]\n"
                f"To: [cyan]{recipient}[/]\n"
                f"Amount: [cyan]{amount} SOL[/]\n"
                f"Signature: [yellow]{signature}[/]",
                title="Transaction",
                border_style="green",
            ))
            
        except FileNotFoundError:
            console.print(f"[bold red]Wallet '{wallet}' not found.[/]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[bold red]Error sending transaction:[/] {str(e)}")
            raise typer.Exit(1)


@app.command("list")
def list_wallets():
    """
    List all available wallets.
    """
    wallet = DiracWallet()
    
    try:
        # Get wallet list
        wallets = wallet.list_wallets()
        
        if not wallets:
            console.print("[yellow]No wallets found.[/]")
            return
        
        # Create table
        table = Table(title="Available Wallets")
        table.add_column("Name", style="cyan")
        
        for wallet_name in wallets:
            table.add_row(wallet_name)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error listing wallets:[/] {str(e)}")
        raise typer.Exit(1)


@app.command("export")
def export_wallet(
    name: str = typer.Argument(..., help="Wallet name"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory"),
):
    """
    Export a wallet (public information only).
    """
    with console.status(f"Exporting wallet '{name}'..."):
        wallet = DiracWallet()
        
        try:
            # Export wallet
            export_path = wallet.export_wallet(name=name, export_path=output)
            
            console.print(Panel(
                f"[bold green]Wallet exported successfully![/]\n\n"
                f"Exported to: [cyan]{export_path}[/]",
                title="Export",
                border_style="green",
            ))
            
        except FileNotFoundError:
            console.print(f"[bold red]Wallet '{name}' not found.[/]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[bold red]Error exporting wallet:[/] {str(e)}")
            raise typer.Exit(1)


@app.command("import")
def import_wallet(
    file_path: str = typer.Argument(..., help="Path to wallet file"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New wallet name"),
):
    """
    Import a wallet from a file.
    """
    with console.status(f"Importing wallet from '{file_path}'..."):
        wallet = DiracWallet()
        
        try:
            # Import wallet
            address = wallet.import_wallet(file_path, name=name)
            
            console.print(Panel(
                f"[bold green]Wallet imported successfully![/]\n\n"
                f"Name: [cyan]{name or os.path.basename(file_path).split('.')[0]}[/]\n"
                f"Address: [cyan]{address}[/]",
                title="Import",
                border_style="green",
            ))
            
        except FileNotFoundError:
            console.print(f"[bold red]File '{file_path}' not found.[/]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[bold red]Error importing wallet:[/] {str(e)}")
            raise typer.Exit(1)


if __name__ == "__main__":
    app() 