"""
Command-line interface for benchmarking quantum-resistant algorithms.
"""

import typer
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.table import Table

from ..utils.benchmarks import QuantumBenchmark, run_benchmarks

app = typer.Typer(help="Dirac Quantum-Resistant Algorithms Benchmark CLI")
console = Console()


@app.callback()
def callback():
    """
    Dirac Quantum-Resistant Algorithms Benchmark CLI.
    """
    pass


@app.command("run")
def run(
    iterations: int = typer.Option(
        50, "--iterations", "-i", help="Number of iterations for each test"
    ),
    output_dir: str = typer.Option(
        "benchmark_results", "--output", "-o", help="Directory to save results"
    ),
    skip_plots: bool = typer.Option(
        False, "--skip-plots", help="Skip generating plots"
    ),
):
    """
    Run benchmarks for all quantum-resistant algorithms.
    """
    with console.status("Setting up benchmarks..."):
        benchmark = QuantumBenchmark(iterations=iterations)
    
    # Create progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[bold]{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        # Add tasks
        key_gen_task = progress.add_task("Benchmarking key generation...", total=1)
        signing_task = progress.add_task("Benchmarking signing...", total=1)
        verify_task = progress.add_task("Benchmarking verification...", total=1)
        hash_task = progress.add_task("Benchmarking hashing...", total=1)
        encrypt_task = progress.add_task("Benchmarking encryption...", total=1)
        decrypt_task = progress.add_task("Benchmarking decryption...", total=1)
        
        # Run benchmarks
        console.print("[bold]Running benchmarks...[/]")
        
        # Key generation
        key_gen_results = benchmark.benchmark_key_generation()
        progress.update(key_gen_task, completed=1)
        
        # Signing
        signing_results = benchmark.benchmark_signing()
        progress.update(signing_task, completed=1)
        
        # Verification
        verify_results = benchmark.benchmark_verification()
        progress.update(verify_task, completed=1)
        
        # Hashing
        hash_results = benchmark.benchmark_hashing()
        progress.update(hash_task, completed=1)
        
        # Encryption
        encrypt_results = benchmark.benchmark_encryption()
        progress.update(encrypt_task, completed=1)
        
        # Decryption
        decrypt_results = benchmark.benchmark_decryption()
        progress.update(decrypt_task, completed=1)
    
    # Save results
    os.makedirs(output_dir, exist_ok=True)
    
    import json
    with open(f"{output_dir}/benchmark_results.json", "w") as f:
        json.dump(benchmark.results, f, indent=2)
    
    console.print(f"[bold green]Benchmark results saved to {output_dir}/benchmark_results.json[/]")
    
    # Generate plots
    if not skip_plots:
        with console.status("Generating plots..."):
            benchmark.plot_results(output_dir=output_dir)
        console.print(f"[bold green]Benchmark plots saved to {output_dir}/[/]")
    
    # Display summary
    display_summary(benchmark.results)


@app.command("summary")
def summary(
    results_file: str = typer.Argument(
        ..., help="Path to benchmark_results.json file"
    ),
):
    """
    Display a summary of benchmark results.
    """
    if not os.path.exists(results_file):
        console.print(f"[bold red]Results file {results_file} not found.[/]")
        raise typer.Exit(1)
    
    import json
    with open(results_file, "r") as f:
        results = json.load(f)
    
    display_summary(results)


def display_summary(results):
    """Display a summary of benchmark results."""
    console.print("[bold]Benchmark Summary[/]")
    
    # Key generation table
    if "key_generation" in results:
        table = Table(title="Key Generation (ms)")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Min", style="green")
        table.add_column("Max", style="red")
        table.add_column("Mean", style="yellow")
        table.add_column("Median", style="blue")
        
        for algo, metrics in results["key_generation"].items():
            table.add_row(
                algo,
                f"{metrics['min']:.2f}",
                f"{metrics['max']:.2f}",
                f"{metrics['mean']:.2f}",
                f"{metrics['median']:.2f}",
            )
        
        console.print(table)
    
    # Signing table
    if "signing" in results:
        table = Table(title="Signing (ms)")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Min", style="green")
        table.add_column("Max", style="red")
        table.add_column("Mean", style="yellow")
        table.add_column("Median", style="blue")
        
        for algo, metrics in results["signing"].items():
            table.add_row(
                algo,
                f"{metrics['min']:.2f}",
                f"{metrics['max']:.2f}",
                f"{metrics['mean']:.2f}",
                f"{metrics['median']:.2f}",
            )
        
        console.print(table)
    
    # Verification table
    if "verification" in results:
        table = Table(title="Verification (ms)")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Min", style="green")
        table.add_column("Max", style="red")
        table.add_column("Mean", style="yellow")
        table.add_column("Median", style="blue")
        
        for algo, metrics in results["verification"].items():
            table.add_row(
                algo,
                f"{metrics['min']:.2f}",
                f"{metrics['max']:.2f}",
                f"{metrics['mean']:.2f}",
                f"{metrics['median']:.2f}",
            )
        
        console.print(table)
    
    # Hashing table
    if "hashing" in results:
        table = Table(title="Hashing (ms)")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Min", style="green")
        table.add_column("Max", style="red")
        table.add_column("Mean", style="yellow")
        table.add_column("Median", style="blue")
        
        for algo, metrics in results["hashing"].items():
            table.add_row(
                algo,
                f"{metrics['min']:.2f}",
                f"{metrics['max']:.2f}",
                f"{metrics['mean']:.2f}",
                f"{metrics['median']:.2f}",
            )
        
        console.print(table)
    
    # Encryption/Decryption table
    encryption_data = results.get("encryption", {})
    decryption_data = results.get("decryption", {})
    
    if encryption_data or decryption_data:
        table = Table(title="Encryption/Decryption (ms)")
        table.add_column("Operation", style="cyan")
        table.add_column("Min", style="green")
        table.add_column("Max", style="red")
        table.add_column("Mean", style="yellow")
        table.add_column("Median", style="blue")
        
        for category, data in [("encryption", encryption_data), ("decryption", decryption_data)]:
            for op, metrics in data.items():
                table.add_row(
                    f"{category.capitalize()} - {op}",
                    f"{metrics['min']:.2f}",
                    f"{metrics['max']:.2f}",
                    f"{metrics['mean']:.2f}",
                    f"{metrics['median']:.2f}",
                )
        
        console.print(table)


if __name__ == "__main__":
    app() 