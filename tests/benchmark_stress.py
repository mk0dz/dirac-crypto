"""
Stress testing and load benchmarking for Dirac Wallet
"""
import sys
import os
import time
import json
import tempfile
import shutil
import random
import concurrent.futures
import multiprocessing
import psutil
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from functools import wraps

# Add the parent directory to sys.path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dirac_wallet.core.keys import QuantumKeyManager
from dirac_wallet.core.wallet import DiracWallet
from dirac_wallet.core.transactions import QuantumTransaction
from solders.hash import Hash


def timeit(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {execution_time:.6f} seconds")
        return result, execution_time
    return wrapper


def measure_memory_usage():
    """Measure current process memory usage"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss  # Return resident set size in bytes


# Define this function at module scope for multiprocessing compatibility
def generate_key():
    """Generate a keypair for parallel testing"""
    key_manager = QuantumKeyManager()
    return key_manager.generate_keypair()


# Define this function at module scope for multiprocessing compatibility
def sign_transaction(tx_data):
    """Sign a transaction for parallel testing"""
    wallet, tx_index, recipient, amount = tx_data
    tx = QuantumTransaction(wallet)
    tx.create_transfer(recipient, amount)
    tx.recent_blockhash = Hash.default()
    return tx.sign_transaction(tx.recent_blockhash)


class StressTester:
    """Stress testing for Dirac Wallet"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the stress tester"""
        self.output_dir = output_dir or "benchmark_results"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Track benchmark results
        self.results = {}
    
    @timeit
    def benchmark_key_generation_batch(self, batch_size: int = 100) -> List[Dict]:
        """Benchmark batch key generation"""
        key_manager = QuantumKeyManager()
        
        initial_memory = measure_memory_usage()
        
        keypairs = []
        start_time = time.time()
        
        for _ in range(batch_size):
            keypairs.append(key_manager.generate_keypair())
            
        end_time = time.time()
        
        final_memory = measure_memory_usage()
        memory_used = final_memory - initial_memory
        
        # Calculate metrics
        total_time = end_time - start_time
        avg_time = total_time / batch_size
        memory_per_key = memory_used / max(1, batch_size)  # Avoid division by zero
        
        return {
            "total_time": total_time,
            "avg_time": avg_time,
            "memory_used": memory_used,
            "memory_per_key": memory_per_key,
            "batch_size": batch_size
        }
    
    @timeit
    def benchmark_key_generation_parallel(self, 
                                         num_keys: int = 100, 
                                         max_workers: int = None) -> Dict:
        """Benchmark parallel key generation"""
        if max_workers is None:
            max_workers = min(multiprocessing.cpu_count(), 4)  # Limit workers to avoid overwhelming system
        
        initial_memory = measure_memory_usage()
        start_time = time.time()
        
        # Use ThreadPoolExecutor instead of ProcessPoolExecutor for simpler sharing
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(generate_key) for _ in range(num_keys)]
            keypairs = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        final_memory = measure_memory_usage()
        
        memory_used = final_memory - initial_memory
        
        return {
            "total_time": end_time - start_time,
            "avg_time_per_key": (end_time - start_time) / num_keys,
            "num_keys": num_keys,
            "max_workers": max_workers,
            "memory_used": memory_used,
            "memory_per_key": memory_used / max(1, num_keys)
        }
    
    @timeit
    def benchmark_transaction_signing_batch(self, 
                                          num_transactions: int = 100) -> Dict:
        """Benchmark batch transaction signing"""
        # Create temporary directory for test wallet
        with tempfile.TemporaryDirectory() as temp_dir:
            wallet_path = Path(temp_dir) / "test_wallet.dwf"
            
            # Create wallet
            wallet = DiracWallet(str(wallet_path))
            wallet.create("test_password")
            
            # Create transactions
            transactions = []
            initial_memory = measure_memory_usage()
            
            for i in range(num_transactions):
                tx = QuantumTransaction(wallet)
                # Use different amounts to ensure unique transactions
                tx.create_transfer("GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE", 10000 + i)
                tx.recent_blockhash = Hash.default()
                transactions.append(tx)
            
            # Sign all transactions and measure time
            start_time = time.time()
            signed_txs = []
            
            for tx in transactions:
                signed_txs.append(tx.sign_transaction(tx.recent_blockhash))
                
            end_time = time.time()
            
            final_memory = measure_memory_usage()
            memory_used = final_memory - initial_memory
            
            # Calculate metrics
            total_time = end_time - start_time
            avg_time = total_time / num_transactions
            memory_per_tx = memory_used / max(1, num_transactions)
            
            return {
                "total_time": total_time,
                "avg_time": avg_time,
                "memory_used": memory_used,
                "memory_per_tx": memory_per_tx,
                "num_transactions": num_transactions
            }
    
    @timeit
    def benchmark_transaction_signing_parallel(self,
                                             num_transactions: int = 100,
                                             max_workers: int = None) -> Dict:
        """Benchmark parallel transaction signing"""
        if max_workers is None:
            max_workers = min(multiprocessing.cpu_count(), 4)  # Limit workers
            
        # Create temporary directory for test wallet
        with tempfile.TemporaryDirectory() as temp_dir:
            wallet_path = Path(temp_dir) / "test_wallet.dwf"
            
            # Create wallet
            wallet = DiracWallet(str(wallet_path))
            wallet.create("test_password")
            
            # Prepare transaction data
            tx_data_list = []
            
            for i in range(num_transactions):
                recipient = "GqhP9E3JUYFQiQhJXeZUTTi3zRQhKzk9TRoG9Uo9LBCE"
                tx_data_list.append((wallet, i, recipient, 10000 + i))
            
            initial_memory = measure_memory_usage()
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(sign_transaction, tx_data) for tx_data in tx_data_list]
                signed_txs = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            final_memory = measure_memory_usage()
            
            memory_used = final_memory - initial_memory
            
            return {
                "total_time": end_time - start_time,
                "avg_time_per_tx": (end_time - start_time) / num_transactions,
                "num_transactions": num_transactions,
                "max_workers": max_workers,
                "memory_used": memory_used,
                "memory_per_tx": memory_used / max(1, num_transactions)
            }
    
    @timeit
    def benchmark_wallet_operations(self, num_operations: int = 100) -> Dict:
        """Benchmark mixed wallet operations"""
        # Create temporary directory for test wallet
        with tempfile.TemporaryDirectory() as temp_dir:
            wallet_path = Path(temp_dir) / "test_wallet.dwf"
            
            # Create wallet
            wallet = DiracWallet(str(wallet_path))
            wallet.create("test_password")
            
            operations_time = []
            memory_usage = []
            operation_types = []
            
            initial_memory = measure_memory_usage()
            
            for i in range(num_operations):
                # Choose random operation
                operation = random.choice(["lock", "unlock", "info", "sign"])
                operation_types.append(operation)
                
                # Measure memory before operation
                before_mem = measure_memory_usage()
                
                # Perform operation
                start_time = time.time()
                
                if operation == "lock":
                    wallet.lock()
                elif operation == "unlock":
                    if not wallet.is_unlocked:
                        wallet.unlock("test_password")
                elif operation == "info":
                    wallet.get_info()
                elif operation == "sign":
                    if not wallet.is_unlocked:
                        wallet.unlock("test_password")
                    wallet.sign_message(f"Test message {i}".encode())
                
                end_time = time.time()
                after_mem = measure_memory_usage()
                
                # Record metrics
                operations_time.append(end_time - start_time)
                memory_usage.append(after_mem - before_mem)
            
            final_memory = measure_memory_usage()
            total_memory = final_memory - initial_memory
            
            # Calculate metrics by operation type
            op_metrics = {}
            for op_type in set(operation_types):
                op_times = [operations_time[i] for i in range(len(operations_time)) 
                           if operation_types[i] == op_type]
                op_mem = [memory_usage[i] for i in range(len(memory_usage))
                         if operation_types[i] == op_type]
                
                op_metrics[op_type] = {
                    "count": len(op_times),
                    "avg_time": sum(op_times) / max(1, len(op_times)),
                    "min_time": min(op_times) if op_times else 0,
                    "max_time": max(op_times) if op_times else 0,
                    "avg_memory": sum(op_mem) / max(1, len(op_mem)),
                }
            
            return {
                "total_operations": num_operations,
                "total_time": sum(operations_time),
                "avg_time": sum(operations_time) / num_operations,
                "total_memory": total_memory,
                "avg_memory_per_op": total_memory / num_operations,
                "operation_metrics": op_metrics
            }
    
    def run_all_benchmarks(self) -> Dict:
        """Run all benchmarks and compile results"""
        results = {}
        
        print("Running key generation batch benchmark...")
        key_gen_batch_result, key_gen_batch_time = self.benchmark_key_generation_batch(batch_size=100)
        results["key_generation_batch"] = key_gen_batch_result
        
        print("Running key generation parallel benchmark...")
        key_gen_parallel_result, key_gen_parallel_time = self.benchmark_key_generation_parallel(num_keys=50)  # Reduced count
        results["key_generation_parallel"] = key_gen_parallel_result
        
        print("Running transaction signing batch benchmark...")
        tx_sign_batch_result, tx_sign_batch_time = self.benchmark_transaction_signing_batch(num_transactions=50)  # Reduced count
        results["transaction_signing_batch"] = tx_sign_batch_result
        
        print("Running transaction signing parallel benchmark...")
        tx_sign_parallel_result, tx_sign_parallel_time = self.benchmark_transaction_signing_parallel(num_transactions=50)  # Reduced count
        results["transaction_signing_parallel"] = tx_sign_parallel_result
        
        print("Running wallet operations benchmark...")
        wallet_ops_result, wallet_ops_time = self.benchmark_wallet_operations(num_operations=50)  # Reduced count
        results["wallet_operations"] = wallet_ops_result
        
        # Save results to file
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        results_file = Path(self.output_dir) / f"benchmark_results_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Benchmark results saved to {results_file}")
        
        # Generate charts
        self.generate_charts(results, timestamp)
        
        return results
    
    def generate_charts(self, results: Dict, timestamp: str) -> None:
        """Generate charts from benchmark results"""
        # Create output directory for charts
        charts_dir = Path(self.output_dir) / f"charts_{timestamp}"
        os.makedirs(charts_dir, exist_ok=True)
        
        # Performance comparison chart (key generation)
        plt.figure(figsize=(10, 6))
        labels = ['Batch', 'Parallel']
        times = [
            results["key_generation_batch"]["avg_time"],
            results["key_generation_parallel"]["avg_time_per_key"]
        ]
        plt.bar(labels, times, color=['blue', 'green'])
        plt.title('Key Generation Performance Comparison')
        plt.ylabel('Time per key (seconds)')
        plt.savefig(charts_dir / "key_generation_comparison.png")
        plt.close()  # Close to free memory
        
        # Performance comparison chart (transaction signing)
        plt.figure(figsize=(10, 6))
        labels = ['Batch', 'Parallel']
        times = [
            results["transaction_signing_batch"]["avg_time"],
            results["transaction_signing_parallel"]["avg_time_per_tx"]
        ]
        plt.bar(labels, times, color=['blue', 'green'])
        plt.title('Transaction Signing Performance Comparison')
        plt.ylabel('Time per transaction (seconds)')
        plt.savefig(charts_dir / "transaction_signing_comparison.png")
        plt.close()  # Close to free memory
        
        # Memory usage chart
        plt.figure(figsize=(10, 6))
        labels = ['Key Gen (Batch)', 'Key Gen (Parallel)', 
                 'Tx Sign (Batch)', 'Tx Sign (Parallel)']
        memory = [
            results["key_generation_batch"]["memory_per_key"] / (1024 * 1024),
            results["key_generation_parallel"]["memory_per_key"] / (1024 * 1024),
            results["transaction_signing_batch"]["memory_per_tx"] / (1024 * 1024),
            results["transaction_signing_parallel"]["memory_per_tx"] / (1024 * 1024)
        ]
        plt.bar(labels, memory, color=['blue', 'green', 'red', 'purple'])
        plt.title('Memory Usage Comparison')
        plt.ylabel('Memory per operation (MB)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(charts_dir / "memory_usage_comparison.png")
        plt.close()  # Close to free memory
        
        # Wallet operations comparison
        if "operation_metrics" in results["wallet_operations"]:
            op_metrics = results["wallet_operations"]["operation_metrics"]
            
            plt.figure(figsize=(10, 6))
            labels = list(op_metrics.keys())
            times = [op_metrics[op]["avg_time"] for op in labels]
            plt.bar(labels, times)
            plt.title('Wallet Operation Performance')
            plt.ylabel('Average time (seconds)')
            plt.savefig(charts_dir / "wallet_operations_performance.png")
            plt.close()  # Close to free memory
        
        print(f"Charts generated in {charts_dir}")


if __name__ == "__main__":
    # Run all benchmarks
    tester = StressTester()
    results = tester.run_all_benchmarks() 