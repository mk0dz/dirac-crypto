#!/bin/bash

# Dirac Quantum-Resistant Wallet Menu
# This script provides a unified menu-based interface for all wallet operations

# Colors and formatting
BOLD=$(tput bold)
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
BLUE=$(tput setaf 4)
MAGENTA=$(tput setaf 5)
CYAN=$(tput setaf 6)
RESET=$(tput sgr0)

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Initialize variables
WALLET_NAME=""
DEMO_RECIPIENT="DykvQoXUFD23LH6Gep3uZx2sDVJPxsQsXCQXVwZcP9H"  # Sample Solana address
DEMO_AMOUNT="0.01"
DEMO_OUTPUT_DIR="export"

# Helper functions
clear_screen() {
    clear
    print_header
}

print_header() {
    echo "${BOLD}${BLUE}Dirac Quantum-Resistant Wallet${RESET}"
    echo "${YELLOW}====================================${RESET}"
    echo ""
}

print_success() {
    echo "${GREEN}✓ $1${RESET}"
}

print_error() {
    echo "${RED}✗ $1${RESET}"
}

print_info() {
    echo "${CYAN}ℹ $1${RESET}"
}

wait_for_key() {
    echo ""
    echo "${BOLD}${YELLOW}Press any key to continue...${RESET}"
    read -n 1 -s
    echo ""
}

check_requirements() {
    if ! command -v python &> /dev/null; then
        print_error "Python not found. Please install Python 3.8 or newer"
        exit 1
    fi
    
    # Create requirements.txt if it doesn't exist
    if [ ! -f "requirements.txt" ]; then
        print_info "Creating requirements.txt..."
        cat > requirements.txt << EOF
solana==0.29.2
solders==0.18.1
quantum_hash==0.5.0
typer==0.9.0
rich==13.4.2
matplotlib==3.7.1
pandas==2.0.2
EOF
    fi
    
    print_info "Checking dependencies..."
    python -c "import solana; import solders" 2>/dev/null
    if [ $? -ne 0 ]; then
        print_info "Installing dependencies..."
        pip install -r requirements.txt
    else
        print_success "Dependencies already installed"
    fi
}

create_core_structure() {
    # Check if essential directories and files exist; if not, create a minimal structure
    print_info "Checking wallet structure..."
    
    # Create src directory structure
    mkdir -p src/wallet src/crypto src/utils src/cli 2>/dev/null
    
    # Create a placeholder implementation if files don't exist
    if [ ! -f "src/wallet/__init__.py" ]; then
        echo '"""Wallet module."""' > src/wallet/__init__.py
    fi
    
    if [ ! -f "src/crypto/__init__.py" ]; then
        echo '"""Crypto module."""' > src/crypto/__init__.py
    fi
    
    if [ ! -f "src/utils/__init__.py" ]; then
        echo '"""Utility functions."""' > src/utils/__init__.py
    fi
    
    if [ ! -f "src/cli/__init__.py" ]; then
        echo '"""Command-line interface."""' > src/cli/__init__.py
    fi
    
    if [ ! -f "src/cli/__main__.py" ]; then
        cat > src/cli/__main__.py << EOF
"""
Main entry point for CLI.
"""
import sys
import typer
from rich.console import Console

app = typer.Typer(help="Dirac Quantum-Resistant Wallet CLI")
console = Console()

@app.command("create")
def create_wallet(name: str):
    """Create a new wallet."""
    console.print(f"[green]Creating wallet: {name}[/green]")
    console.print("[yellow]This is a placeholder. Actual implementation coming soon.[/yellow]")

@app.command("list")
def list_wallets():
    """List all available wallets."""
    console.print("[green]Available wallets:[/green]")
    console.print("[yellow]This is a placeholder. Actual implementation coming soon.[/yellow]")

@app.command("balance")
def check_balance(name: str):
    """Check wallet balance."""
    console.print(f"[green]Checking balance for wallet: {name}[/green]")
    console.print("[yellow]This is a placeholder. Actual implementation coming soon.[/yellow]")

@app.command("send")
def send_transaction(recipient: str, amount: float):
    """Send SOL to a recipient."""
    console.print(f"[green]Sending {amount} SOL to {recipient}[/green]")
    console.print("[yellow]This is a placeholder. Actual implementation coming soon.[/yellow]")

@app.command("export")
def export_wallet(name: str, output: str = None):
    """Export a wallet."""
    console.print(f"[green]Exporting wallet: {name}[/green]")
    console.print("[yellow]This is a placeholder. Actual implementation coming soon.[/yellow]")

@app.command("import")
def import_wallet(file_path: str, name: str = None):
    """Import a wallet."""
    console.print(f"[green]Importing wallet from: {file_path}[/green]")
    console.print("[yellow]This is a placeholder. Actual implementation coming soon.[/yellow]")

@app.command("benchmark")
def benchmark():
    """Run benchmarks."""
    console.print("[green]Running benchmarks...[/green]")
    console.print("[yellow]This is a placeholder. Actual implementation coming soon.[/yellow]")

if __name__ == "__main__":
    app()
EOF
    fi
    
    print_success "Wallet structure ready"
}

run_wallet_command() {
    local cmd="$1"
    local description="$2"
    
    echo "${MAGENTA}$description${RESET}"
    echo "${YELLOW}Command: ${RESET}python -m src.cli $cmd"
    echo "${GREEN}Output:${RESET}"
    echo "${CYAN}--------------------------------------------------${RESET}"
    
    python -m src.cli $cmd
    
    local result=$?
    echo "${CYAN}--------------------------------------------------${RESET}"
    
    if [ $result -eq 0 ]; then
        print_success "Command executed successfully"
    else
        print_error "Command failed with exit code $result"
    fi
    
    wait_for_key
    return $result
}

# Wallet operation functions
create_wallet_menu() {
    clear_screen
    echo "${BOLD}Create a New Wallet${RESET}"
    echo ""
    
    # Get wallet name
    read -p "Enter wallet name: " WALLET_NAME
    if [ -z "$WALLET_NAME" ]; then
        print_error "Wallet name cannot be empty"
        wait_for_key
        return 1
    fi
    
    # Get signature algorithm
    echo ""
    echo "Select signature algorithm:"
    echo "1) SPHINCS+ (recommended)"
    echo "2) Dilithium"
    echo "3) Lamport"
    read -p "Select option [1-3] (default: 1): " sig_option
    
    case "$sig_option" in
        2) sig_algo="dilithium" ;;
        3) sig_algo="lamport" ;;
        *) sig_algo="sphincs" ;;
    esac
    
    # Get hash algorithm
    echo ""
    echo "Select hash algorithm:"
    echo "1) SHA-256 (standard)"
    echo "2) SHA-512 (more secure)"
    echo "3) BLAKE2b (fast and secure)"
    read -p "Select option [1-3] (default: 1): " hash_option
    
    case "$hash_option" in
        2) hash_algo="sha512" ;;
        3) hash_algo="blake2b" ;;
        *) hash_algo="sha256" ;;
    esac
    
    # Get security level
    echo ""
    echo "Select security level (higher is more secure but slower):"
    echo "1) Low"
    echo "2) Medium-Low"
    echo "3) Medium (recommended)"
    echo "4) Medium-High"
    echo "5) High"
    read -p "Select option [1-5] (default: 3): " sec_option
    
    security=${sec_option:-3}
    
    # Get network
    echo ""
    echo "Select network:"
    echo "1) Testnet (recommended for testing)"
    echo "2) Devnet"
    echo "3) Mainnet (real funds)"
    echo "4) Local"
    read -p "Select option [1-4] (default: 1): " net_option
    
    case "$net_option" in
        2) network="devnet" ;;
        3) network="mainnet" ;;
        4) network="local" ;;
        *) network="testnet" ;;
    esac
    
    # Backup option
    echo ""
    read -p "Generate backup keys? [Y/n]: " backup_option
    backup_flag=""
    if [[ "$backup_option" == "n" || "$backup_option" == "N" ]]; then
        backup_flag="--no-backup"
    fi
    
    # Force option
    echo ""
    read -p "Overwrite if wallet exists? [y/N]: " force_option
    force_flag=""
    if [[ "$force_option" == "y" || "$force_option" == "Y" ]]; then
        force_flag="--force"
    fi
    
    # Build and run command
    cmd="create $WALLET_NAME --sig-algo $sig_algo --hash-algo $hash_algo --security $security --network $network $backup_flag $force_flag"
    run_wallet_command "$cmd" "Creating wallet with $sig_algo signatures and $hash_algo hash on $network..."
}

check_balance_menu() {
    clear_screen
    echo "${BOLD}Check Wallet Balance${RESET}"
    echo ""
    
    # Get wallet name
    read -p "Enter wallet name: " WALLET_NAME
    if [ -z "$WALLET_NAME" ]; then
        print_error "Wallet name cannot be empty"
        wait_for_key
        return 1
    fi
    
    # Run command
    run_wallet_command "balance $WALLET_NAME" "Checking balance of wallet '$WALLET_NAME'..."
}

send_transaction_menu() {
    clear_screen
    echo "${BOLD}Send SOL Transaction${RESET}"
    echo ""
    
    # Get wallet name
    read -p "Enter wallet name: " WALLET_NAME
    if [ -z "$WALLET_NAME" ]; then
        print_error "Wallet name cannot be empty"
        wait_for_key
        return 1
    fi
    
    # Get recipient
    read -p "Enter recipient address: " RECIPIENT
    if [ -z "$RECIPIENT" ]; then
        print_error "Recipient address cannot be empty"
        wait_for_key
        return 1
    fi
    
    # Get amount
    read -p "Enter amount in SOL: " AMOUNT
    if ! [[ "$AMOUNT" =~ ^[0-9]*\.?[0-9]+$ ]]; then
        print_error "Amount must be a valid number"
        wait_for_key
        return 1
    fi
    
    # Run command
    run_wallet_command "send $RECIPIENT $AMOUNT --wallet $WALLET_NAME" "Sending $AMOUNT SOL from '$WALLET_NAME' to '$RECIPIENT'..."
}

transaction_history_menu() {
    clear_screen
    echo "${BOLD}Transaction History${RESET}"
    echo ""
    
    # Get wallet name
    read -p "Enter wallet name: " WALLET_NAME
    if [ -z "$WALLET_NAME" ]; then
        print_error "Wallet name cannot be empty"
        wait_for_key
        return 1
    fi
    
    # Run command
    run_wallet_command "history $WALLET_NAME" "Viewing transaction history for '$WALLET_NAME'..."
}

export_wallet_menu() {
    clear_screen
    echo "${BOLD}Export Wallet${RESET}"
    echo ""
    
    # Get wallet name
    read -p "Enter wallet name: " WALLET_NAME
    if [ -z "$WALLET_NAME" ]; then
        print_error "Wallet name cannot be empty"
        wait_for_key
        return 1
    fi
    
    # Get export directory
    read -p "Enter export directory (default: ./export): " EXPORT_DIR
    EXPORT_DIR=${EXPORT_DIR:-"./export"}
    
    # Create export directory if it doesn't exist
    mkdir -p "$EXPORT_DIR" 2>/dev/null
    
    # Private key option
    echo ""
    read -p "Include private keys? This is a security risk! [y/N]: " private_key_option
    private_flag=""
    if [[ "$private_key_option" == "y" || "$private_key_option" == "Y" ]]; then
        private_flag="--include-private"
    fi
    
    # Run command
    run_wallet_command "export $WALLET_NAME --output $EXPORT_DIR $private_flag" "Exporting wallet '$WALLET_NAME' to '$EXPORT_DIR'..."
}

import_wallet_menu() {
    clear_screen
    echo "${BOLD}Import Wallet${RESET}"
    echo ""
    
    # Get wallet file
    read -p "Enter wallet file path: " WALLET_FILE
    if [ -z "$WALLET_FILE" ] || [ ! -f "$WALLET_FILE" ]; then
        print_error "Wallet file not found: $WALLET_FILE"
        wait_for_key
        return 1
    fi
    
    # Get new name (optional)
    read -p "Enter new wallet name (optional): " NEW_NAME
    
    # Build command
    cmd="import $WALLET_FILE"
    if [ ! -z "$NEW_NAME" ]; then
        cmd="$cmd --name $NEW_NAME"
    fi
    
    # Run command
    run_wallet_command "$cmd" "Importing wallet from '$WALLET_FILE'..."
}

backup_menu() {
    clear_screen
    echo "${BOLD}Wallet Backups${RESET}"
    echo ""
    
    # Get wallet name
    read -p "Enter wallet name: " WALLET_NAME
    if [ -z "$WALLET_NAME" ]; then
        print_error "Wallet name cannot be empty"
        wait_for_key
        return 1
    fi
    
    # Display available backups
    run_wallet_command "backup $WALLET_NAME" "Listing backups for '$WALLET_NAME'..."
    
    # Ask if user wants to restore
    read -p "Do you want to restore from a backup? [y/N]: " restore_option
    if [[ "$restore_option" == "y" || "$restore_option" == "Y" ]]; then
        run_wallet_command "restore $WALLET_NAME" "Restoring wallet '$WALLET_NAME' from backup..."
    fi
}

network_menu() {
    clear_screen
    echo "${BOLD}Network Settings${RESET}"
    echo ""
    
    # Get network
    echo "Select network:"
    echo "1) Testnet"
    echo "2) Devnet"
    echo "3) Mainnet"
    echo "4) Local"
    read -p "Select option [1-4]: " net_option
    
    case "$net_option" in
        2) network="devnet" ;;
        3) network="mainnet" ;;
        4) network="local" ;;
        *) network="testnet" ;;
    esac
    
    # Get wallet name (optional)
    read -p "Enter wallet name to update (leave empty for global default): " WALLET_NAME
    
    # Build command
    cmd="network $network"
    if [ ! -z "$WALLET_NAME" ]; then
        cmd="$cmd --wallet $WALLET_NAME"
    fi
    
    # Run command
    run_wallet_command "$cmd" "Changing network to '$network'..."
}

list_wallets_menu() {
    clear_screen
    echo "${BOLD}Available Wallets${RESET}"
    echo ""
    
    run_wallet_command "list" "Listing all wallets..."
}

run_benchmarks_menu() {
    clear_screen
    echo "${BOLD}Run Performance Benchmarks${RESET}"
    echo ""
    
    run_wallet_command "benchmark" "Running benchmarks..."
}

# Main program
check_requirements
create_core_structure

while true; do
    clear_screen
    echo "${BOLD}Main Menu${RESET}"
    echo ""
    echo "1) Create a new wallet"
    echo "2) Check wallet balance"
    echo "3) Send SOL"
    echo "4) Transaction history"
    echo "5) List wallets"
    echo "6) Backup & restore"
    echo "7) Change network"
    echo "8) Export wallet"
    echo "9) Import wallet"
    echo "10) Run benchmarks"
    echo "11) Exit"
    echo ""
    read -p "Select an option [1-11]: " option
    
    case "$option" in
        1) create_wallet_menu ;;
        2) check_balance_menu ;;
        3) send_transaction_menu ;;
        4) transaction_history_menu ;;
        5) list_wallets_menu ;;
        6) backup_menu ;;
        7) network_menu ;;
        8) export_wallet_menu ;;
        9) import_wallet_menu ;;
        10) run_benchmarks_menu ;;
        11) 
            echo "${GREEN}Thank you for using Dirac Quantum-Resistant Wallet!${RESET}"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            wait_for_key
            ;;
    esac
done