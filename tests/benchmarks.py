"""
Benchmarking tests for quantum wallet implementation
"""
import time
import statistics
import tempfile
from pathlib import Path
from typing import List, Dict
from dirac_wallet.core.keys import QuantumKeyManager
from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.core.transactions import QuantumTransaction
from solders.hash import Hash

def measure_time(func, *args, **kwargs) -> float:
    """Measure execution time of a function"""
    start_time = time.time()
    result = func(*args, **kwargs)
    return time.time() - start_time, result

def benchmark_key_generation(iterations: int = 10) -> Dict[str, float]:
    """Benchmark key generation performance"""
    key_manager = QuantumKeyManager()
    times: List[float] = []
    
    for _ in range(iterations):
        time_taken, _ = measure_time(key_manager.generate_keypair)
        times.append(time_taken)
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0
    }

def benchmark_transaction_signing(iterations: int = 10) -> Dict[str, float]:
    """Benchmark transaction signing performance"""
    # Create a temporary directory for wallet storage
    with tempfile.TemporaryDirectory() as temp_dir:
        wallet_path = Path(temp_dir) / "test_wallet"
        
        # Initialize wallet and create with password
        test_password = "benchmark_password"
        wallet = DiracWallet(wallet_path=str(wallet_path))
        wallet_data = wallet.create(test_password)
        
        # Create a transaction
        tx = QuantumTransaction(wallet)
        tx.create_transfer("GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE", 100_000)  # Test recipient
        tx.recent_blockhash = Hash.default()  # Use default hash for test
        
        times: List[float] = []
        
        for _ in range(iterations):
            time_taken, _ = measure_time(tx.sign_transaction, tx.recent_blockhash)
            times.append(time_taken)
        
        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0
        }

def benchmark_secure_storage(iterations: int = 10) -> Dict[str, float]:
    """Benchmark secure storage operations"""
    from dirac_wallet.core.secure_storage import SecureStorage
    
    storage = SecureStorage("test_password")
    test_data = {"sensitive": "data", "key": "value"}
    
    # Benchmark encryption
    encrypt_times: List[float] = []
    for _ in range(iterations):
        time_taken, _ = measure_time(storage.encrypt_data, test_data)
        encrypt_times.append(time_taken)
    
    # Benchmark decryption
    encrypted = storage.encrypt_data(test_data)
    decrypt_times: List[float] = []
    for _ in range(iterations):
        time_taken, _ = measure_time(storage.decrypt_data, encrypted)
        decrypt_times.append(time_taken)
    
    return {
        "encryption": {
            "mean": statistics.mean(encrypt_times),
            "median": statistics.median(encrypt_times),
            "min": min(encrypt_times),
            "max": max(encrypt_times),
            "std_dev": statistics.stdev(encrypt_times) if len(encrypt_times) > 1 else 0
        },
        "decryption": {
            "mean": statistics.mean(decrypt_times),
            "median": statistics.median(decrypt_times),
            "min": min(decrypt_times),
            "max": max(decrypt_times),
            "std_dev": statistics.stdev(decrypt_times) if len(decrypt_times) > 1 else 0
        }
    }

def run_all_benchmarks(iterations: int = 10) -> Dict[str, Dict[str, float]]:
    """Run all benchmarks and return results"""
    return {
        "key_generation": benchmark_key_generation(iterations),
        "transaction_signing": benchmark_transaction_signing(iterations),
        "secure_storage": benchmark_secure_storage(iterations)
    }

if __name__ == "__main__":
    # Run benchmarks and print results
    results = run_all_benchmarks()
    
    print("\nBenchmark Results:")
    print("=================")
    
    for benchmark, metrics in results.items():
        print(f"\n{benchmark.replace('_', ' ').title()}:")
        if isinstance(metrics, dict) and "encryption" in metrics:
            print("  Encryption:")
            for metric, value in metrics["encryption"].items():
                print(f"    {metric}: {value:.6f}s")
            print("  Decryption:")
            for metric, value in metrics["decryption"].items():
                print(f"    {metric}: {value:.6f}s")
        else:
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.6f}s") 