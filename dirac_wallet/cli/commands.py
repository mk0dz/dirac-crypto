"""Command Line Interface for Dirac-Wallet (chain-agnostic, ML-DSA quantum identity)."""
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..account import create_account
from ..chains import get_adapter
from ..network.solana_client import QuantumSolanaClient
from ..vault import LegacyWalletError, Vault

console = Console()
WALLET_DIR = Path.home() / ".dirac_wallet"


def print_success(message):
    console.print(f"✓ {message}", style="bold green")


def print_error(message):
    console.print(f"✗ {message}", style="bold red")


def print_info(message):
    console.print(f"ℹ {message}", style="bold blue")


def print_kv_table(title, data):
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("Property", style="cyan", width=28)
    table.add_column("Value", style="white")
    for key, value in data.items():
        table.add_row(str(key).replace("_", " ").title(), str(value))
    console.print(table)


def print_balance(address, balance):
    console.print(Panel(
        f"[bold green]{balance:.6f} SOL[/bold green]",
        title=f"Balance for {address[:8]}...{address[-8:]}",
        border_style="green",
    ))


def print_transaction_history(transactions):
    table = Table(title="Transaction History", box=box.ROUNDED)
    for col, style in (("Date", "cyan"), ("Type", "cyan"), ("Amount", "green"),
                       ("Fee", "red"), ("Status", "yellow"), ("Signature", "magenta")):
        table.add_column(col, style=style)
    for tx in transactions:
        ts = str(tx.get("timestamp", ""))[:10] or "Unknown"
        amount = f"{float(tx.get('amount', 0.0)):.6f}"
        fee = f"{float(tx.get('fee', 0.0)):.6f}"
        sig = str(tx.get("signature", ""))
        sig = f"{sig[:6]}...{sig[-6:]}" if len(sig) > 12 else sig
        table.add_row(ts, str(tx.get("type", "transfer")), amount, fee,
                      str(tx.get("status", "unknown")), sig)
    console.print(table)


def get_password(prompt="Enter wallet password"):
    import getpass
    return getpass.getpass(f"{prompt}: ")


def wallet_path(name, network, path):
    return Path(path) if path else WALLET_DIR / f"{name}_{network}.dwf"


def open_wallet(name, network, path):
    """Resolve, unlock and return (vault, account, history, password) or None on failure."""
    p = wallet_path(name, network, path)
    if not p.exists():
        print_error(f"Wallet not found at {p}")
        print_info(f"Create one with: dirac-wallet create {name} --network {network}")
        return None
    vault = Vault(p)
    password = get_password()
    try:
        account, history = vault.load(password)
    except LegacyWalletError as exc:
        print_error("Legacy wallet detected")
        print_info(str(exc))
        return None
    except ValueError:
        print_error("Invalid password or corrupted wallet")
        return None
    return vault, account, history, password


@click.group()
@click.version_option(version="0.2.0")
def cli():
    """Dirac-Wallet: a Solana wallet with a post-quantum (ML-DSA) identity."""


@cli.command()
@click.option("--network", "-n", default="devnet",
              type=click.Choice(["testnet", "devnet", "mainnet"]))
@click.option("--path", "-p", help="Path to save wallet file")
@click.argument("name", required=True)
def create(network, path, name):
    """Create a new wallet (ed25519 on Solana + ML-DSA quantum identity)."""
    p = wallet_path(name, network, path)
    if p.exists():
        print_error(f"Wallet already exists at {p}")
        return
    while True:
        password = get_password("Create wallet password")
        if password == get_password("Confirm password"):
            break
        print_error("Passwords do not match. Please try again.")

    account = create_account("solana")
    Vault(p).save(account, password, [])
    print_success("Wallet created successfully!")
    print_info(f"Path: {p}")
    print_info(f"Address: {account.address}")
    print_info(f"Quantum identity: {account.quantum_scheme_id.upper()} "
               f"(attestation valid: {account.verify_attestation()})")
    print_info("On-chain signing: ed25519 (Solana). Quantum identity is an off-chain "
               "attestation — Solana funds are not quantum-safe on-chain.")
    click.echo("\n⚠️  Save your password securely. There is no recovery option.")


@cli.command()
@click.option("--path", "-p")
@click.option("--network", "-n", default="devnet",
              type=click.Choice(["testnet", "devnet", "mainnet"]))
@click.argument("name", required=True)
def info(path, network, name):
    """Show wallet information."""
    opened = open_wallet(name, network, path)
    if not opened:
        return
    _vault, account, history, _pw = opened
    view = account.public_view()
    view["attestation_valid"] = account.verify_attestation()
    view["transactions_recorded"] = len(history)
    print_kv_table("Wallet Information", view)


@cli.command()
@click.option("--path", "-p")
@click.option("--network", "-n", default="devnet",
              type=click.Choice(["testnet", "devnet", "mainnet"]))
@click.argument("name", required=True)
def balance(path, network, name):
    """Check wallet balance."""
    opened = open_wallet(name, network, path)
    if not opened:
        return
    _vault, account, _history, _pw = opened

    async def run():
        client = QuantumSolanaClient(network=network)
        try:
            await client.connect()
            return await client.get_balance(account.address)
        finally:
            await client.disconnect()

    try:
        print_balance(account.address, asyncio.run(run()))
    except Exception as exc:
        print_error(f"Failed to get balance: {exc}")


@cli.command()
@click.option("--path", "-p")
@click.option("--network", "-n", default="devnet",
              type=click.Choice(["testnet", "devnet", "mainnet"]))
@click.argument("name", required=True)
@click.argument("recipient", required=True)
@click.argument("amount", required=True, type=float)
def send(path, network, name, recipient, amount):
    """Send SOL to another address (ed25519-signed)."""
    opened = open_wallet(name, network, path)
    if not opened:
        return
    vault, account, history, password = opened
    lamports = int(Decimal(str(amount)) * Decimal(10 ** 9))
    adapter = get_adapter("solana")

    async def run():
        client = QuantumSolanaClient(network=network)
        try:
            await client.connect()
            bal = await client.get_balance(account.address)
            if bal < amount:
                return {"error": f"Insufficient balance: {bal} SOL (need {amount})"}
            blockhash = await client.get_recent_blockhash()
            tx = adapter.build_signed_transfer(account, recipient, lamports, str(blockhash))
            print_info("Transaction signed with ed25519 (Solana on-chain key)...")
            result = await client.submit_quantum_transaction(tx)
            tx_id = result["signature"]
            print_success(f"Submitted: {tx_id}")
            confirmed = False
            for _ in range(5):
                status = await client.get_transaction_status(tx_id)
                if status.get("confirmed"):
                    confirmed = True
                    break
                if status.get("error"):
                    return {"error": status["error"], "tx_id": tx_id}
                await asyncio.sleep(2)
            return {"tx_id": tx_id, "confirmed": confirmed}
        except Exception as exc:
            return {"error": str(exc)}
        finally:
            await client.disconnect()

    result = asyncio.run(run())
    if "error" in result:
        print_error(f"Failed to send: {result['error']}")
        return
    if result["confirmed"]:
        print_success("Transaction confirmed!")
    else:
        print_info("Confirmation timed out; check the transaction ID later.")
    history.append({
        "signature": result["tx_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "amount": float(amount),
        "sender": account.address,
        "recipient": recipient,
        "status": "confirmed" if result["confirmed"] else "pending",
        "fee": 0.000005,
        "type": "transfer",
    })
    vault.save(account, password, history)


@cli.command()
@click.option("--path", "-p")
@click.option("--network", "-n", default="devnet",
              type=click.Choice(["devnet", "testnet"]))
@click.argument("name", required=True)
@click.argument("amount", required=False, type=float, default=1.0)
def airdrop(path, network, name, amount):
    """Request a SOL airdrop (devnet/testnet only)."""
    opened = open_wallet(name, network, path)
    if not opened:
        return
    _vault, account, _history, _pw = opened

    async def run():
        client = QuantumSolanaClient(network=network)
        try:
            await client.connect()
            print_info(f"Requesting {amount} SOL airdrop via RPC...")
            tx_id = await client.request_airdrop(account.address, amount)
            if not tx_id:
                return {"error": "Airdrop failed (rate limited or unavailable). "
                                 "Try https://faucet.solana.com"}
            new_balance = await client.get_balance(account.address)
            return {"tx_id": tx_id, "balance": new_balance}
        except Exception as exc:
            return {"error": str(exc)}
        finally:
            await client.disconnect()

    result = asyncio.run(run())
    if "error" in result:
        print_error(result["error"])
        return
    print_success(f"Airdrop confirmed: {result['tx_id']}")
    print_info(f"Balance: {result['balance']:.6f} SOL")


@cli.command()
@click.option("--path", "-p")
@click.option("--network", "-n", default="devnet",
              type=click.Choice(["testnet", "devnet", "mainnet"]))
@click.option("--limit", "-l", type=int, default=10)
@click.option("--refresh", "-r", is_flag=True, help="Fetch recent transactions from network")
@click.argument("name", required=True)
def history(path, network, limit, refresh, name):
    """Show transaction history."""
    opened = open_wallet(name, network, path)
    if not opened:
        return
    vault, account, txns, password = opened

    if refresh:
        print_info("Refreshing from network...")

        async def run():
            client = QuantumSolanaClient(network=network)
            try:
                await client.connect()
                return await client.get_transaction_history(account.address)
            finally:
                await client.disconnect()

        try:
            fetched = asyncio.run(run())
            known = {t.get("signature") for t in txns}
            added = [t for t in fetched if t.get("signature") not in known]
            txns = txns + added
            vault.save(account, password, txns)
            print_success(f"Added {len(added)} transactions from network")
        except Exception as exc:
            print_error(f"Failed to refresh: {exc}")

    txns = sorted(txns, key=lambda t: t.get("timestamp", ""), reverse=True)[:limit]
    if txns:
        print_transaction_history(txns)
    else:
        print_info("No transaction history found. Use --refresh to fetch from network.")


@cli.command(name="list-wallets")
def list_wallets():
    """List all wallets in the default directory."""
    if not WALLET_DIR.exists() or not list(WALLET_DIR.glob("*.dwf")):
        print_info("No wallets found")
        return
    table = Table(title="Available Wallets", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Network", style="magenta")
    table.add_column("Path", style="white")
    for f in sorted(WALLET_DIR.glob("*.dwf")):
        stem = f.stem
        if stem.endswith(("_devnet", "_testnet", "_mainnet")):
            name, net = stem.rsplit("_", 1)
        else:
            name, net = stem, "unknown"
        table.add_row(name, net, str(f))
    console.print(table)


if __name__ == "__main__":
    cli()
