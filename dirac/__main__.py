"""
Main entry point for the Dirac Wallet CLI application.
"""

import typer
from rich.console import Console

from dirac.ui.cli import create_app

def main():
    """Main entry point for the CLI application."""
    app = create_app()
    app()

if __name__ == "__main__":
    main() 