"""
Benchmarking utilities for measuring performance of quantum-resistant algorithms.
"""

import time
import statistics
from typing import Dict, List, Tuple, Callable, Any
import matplotlib.pyplot as plt
import numpy as np

from ..crypto.keyring import QuantumKeyring, SIGNATURE_ALGORITHMS, HASH_ALGORITHMS


class QuantumBenchmark:
    """
    Benchmark quantum-resistant cryptographic operations.
    """
    
    def __init__(self, iterations: int = 100):
        """
        Initialize the benchmark.
        
        Args:
            iterations: Number of iterations for each test
        """
        self.iterations = iterations
        self.results = {}
    
    def _time_operation(self, operation: Callable, *args, **kwargs) -> float:
        """
        Time a single operation.
        
        Args:
            operation: Function to time
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Execution time in milliseconds
        """
        start_time = time.time()
        operation(*args, **kwargs)
        end_time = time.time()
        
        return (end_time - start_time) * 1000  # Convert to milliseconds
    
    def benchmark_key_generation(self) -> Dict[str, Dict[str, float]]:
        """
        Benchmark key generation for all signature algorithms.
        
        Returns:
            Dictionary of results (algorithm -> metrics)
        """
        results = {}
        
        for algo_name, algo_class in SIGNATURE_ALGORITHMS.items():
            times = []
            
            # Create instance with security level for dilithium
            if algo_name == "dilithium":
                algo = algo_class(security_level=3)
            else:
                algo = algo_class()
            
            for _ in range(self.iterations):
                time_ms = self._time_operation(algo.generate_keypair)
                times.append(time_ms)
            
            results[algo_name] = {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stddev": statistics.stdev(times) if len(times) > 1 else 0,
            }
        
        self.results["key_generation"] = results
        return results
    
    def benchmark_signing(self) -> Dict[str, Dict[str, float]]:
        """
        Benchmark transaction signing for all signature algorithms.
        
        Returns:
            Dictionary of results (algorithm -> metrics)
        """
        results = {}
        test_data = b"TEST TRANSACTION DATA" * 100  # Create reasonable size test data
        
        for algo_name, algo_class in SIGNATURE_ALGORITHMS.items():
            # Create instance with security level for dilithium
            if algo_name == "dilithium":
                algo = algo_class(security_level=3)
            else:
                algo = algo_class()
            
            # Generate a keypair
            private_key, _ = algo.generate_keypair()
            
            times = []
            for _ in range(self.iterations):
                time_ms = self._time_operation(algo.sign, test_data, private_key)
                times.append(time_ms)
            
            results[algo_name] = {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stddev": statistics.stdev(times) if len(times) > 1 else 0,
            }
        
        self.results["signing"] = results
        return results
    
    def benchmark_verification(self) -> Dict[str, Dict[str, float]]:
        """
        Benchmark signature verification for all signature algorithms.
        
        Returns:
            Dictionary of results (algorithm -> metrics)
        """
        results = {}
        test_data = b"TEST TRANSACTION DATA" * 100  # Create reasonable size test data
        
        for algo_name, algo_class in SIGNATURE_ALGORITHMS.items():
            # Create instance with security level for dilithium
            if algo_name == "dilithium":
                algo = algo_class(security_level=3)
            else:
                algo = algo_class()
            
            # Generate a keypair
            private_key, public_key = algo.generate_keypair()
            
            # Sign the test data
            signature = algo.sign(test_data, private_key)
            
            times = []
            for _ in range(self.iterations):
                time_ms = self._time_operation(algo.verify, test_data, signature, public_key)
                times.append(time_ms)
            
            results[algo_name] = {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stddev": statistics.stdev(times) if len(times) > 1 else 0,
            }
        
        self.results["verification"] = results
        return results
    
    def benchmark_hashing(self) -> Dict[str, Dict[str, float]]:
        """
        Benchmark hashing for all hash algorithms.
        
        Returns:
            Dictionary of results (algorithm -> metrics)
        """
        results = {}
        test_data = b"TEST DATA FOR HASHING" * 1000  # Create reasonable size test data
        
        for algo_name, hash_func in HASH_ALGORITHMS.items():
            times = []
            
            for _ in range(self.iterations):
                time_ms = self._time_operation(hash_func, test_data)
                times.append(time_ms)
            
            results[algo_name] = {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stddev": statistics.stdev(times) if len(times) > 1 else 0,
            }
        
        self.results["hashing"] = results
        return results
    
    def benchmark_encryption(self) -> Dict[str, Dict[str, float]]:
        """
        Benchmark KEM encryption.
        
        Returns:
            Dictionary of results with metrics
        """
        results = {}
        test_data = b"SENSITIVE DATA" * 100  # Create reasonable size test data
        
        # Initialize KEM
        kem = QuantumKeyring().kem
        
        # Generate keypair
        public_key, _ = kem.generate_keypair()
        
        # Benchmark encapsulation
        encap_times = []
        for _ in range(self.iterations):
            time_ms = self._time_operation(kem.encapsulate, public_key)
            encap_times.append(time_ms)
        
        results["encapsulation"] = {
            "min": min(encap_times),
            "max": max(encap_times),
            "mean": statistics.mean(encap_times),
            "median": statistics.median(encap_times),
            "stddev": statistics.stdev(encap_times) if len(encap_times) > 1 else 0,
        }
        
        # Generate ciphertext for decapsulation test
        ciphertext, _ = kem.encapsulate(public_key)
        
        # Benchmark actual encryption using a simple XOR
        encrypt_times = []
        for _ in range(self.iterations):
            time_ms = self._time_operation(lambda: bytes(a ^ b for a, b in zip(test_data, b"A" * len(test_data))))
            encrypt_times.append(time_ms)
        
        results["encryption"] = {
            "min": min(encrypt_times),
            "max": max(encrypt_times),
            "mean": statistics.mean(encrypt_times),
            "median": statistics.median(encrypt_times),
            "stddev": statistics.stdev(encrypt_times) if len(encrypt_times) > 1 else 0,
        }
        
        self.results["encryption"] = results
        return results
    
    def benchmark_decryption(self) -> Dict[str, Dict[str, float]]:
        """
        Benchmark KEM decryption.
        
        Returns:
            Dictionary of results with metrics
        """
        results = {}
        
        # Initialize KEM
        kem = QuantumKeyring().kem
        
        # Generate keypair
        public_key, private_key = kem.generate_keypair()
        
        # Generate ciphertext and shared secret
        ciphertext, shared_secret = kem.encapsulate(public_key)
        
        # Benchmark decapsulation
        decap_times = []
        for _ in range(self.iterations):
            time_ms = self._time_operation(kem.decapsulate, ciphertext, private_key)
            decap_times.append(time_ms)
        
        results["decapsulation"] = {
            "min": min(decap_times),
            "max": max(decap_times),
            "mean": statistics.mean(decap_times),
            "median": statistics.median(decap_times),
            "stddev": statistics.stdev(decap_times) if len(decap_times) > 1 else 0,
        }
        
        # Benchmark actual decryption using a simple XOR
        test_data = b"ENCRYPTED DATA" * 100
        decrypt_times = []
        for _ in range(self.iterations):
            time_ms = self._time_operation(lambda: bytes(a ^ b for a, b in zip(test_data, b"A" * len(test_data))))
            decrypt_times.append(time_ms)
        
        results["decryption"] = {
            "min": min(decrypt_times),
            "max": max(decrypt_times),
            "mean": statistics.mean(decrypt_times),
            "median": statistics.median(decrypt_times),
            "stddev": statistics.stdev(decrypt_times) if len(decrypt_times) > 1 else 0,
        }
        
        self.results["decryption"] = results
        return results
    
    def run_all_benchmarks(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Run all benchmarks.
        
        Returns:
            Dictionary of all results
        """
        self.benchmark_key_generation()
        self.benchmark_signing()
        self.benchmark_verification()
        self.benchmark_hashing()
        self.benchmark_encryption()
        self.benchmark_decryption()
        
        return self.results
    
    def plot_results(self, output_dir: str = "."):
        """
        Plot benchmark results.
        
        Args:
            output_dir: Directory to save plots
        """
        if not self.results:
            raise ValueError("No benchmark results to plot. Run benchmarks first.")
        
        # Create output directory
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Plot key generation, signing, verification
        self._plot_algorithm_comparison(
            "key_generation", 
            "Key Generation Performance", 
            f"{output_dir}/key_generation.png"
        )
        
        self._plot_algorithm_comparison(
            "signing", 
            "Signing Performance", 
            f"{output_dir}/signing.png"
        )
        
        self._plot_algorithm_comparison(
            "verification", 
            "Verification Performance", 
            f"{output_dir}/verification.png"
        )
        
        # Plot hashing
        self._plot_algorithm_comparison(
            "hashing", 
            "Hashing Performance", 
            f"{output_dir}/hashing.png"
        )
        
        # Plot encryption/decryption
        self._plot_encryption_decryption(f"{output_dir}/encryption_decryption.png")
    
    def _plot_algorithm_comparison(self, benchmark_type: str, title: str, output_file: str):
        """Plot comparison of algorithms for a specific benchmark."""
        if benchmark_type not in self.results:
            return
        
        data = self.results[benchmark_type]
        algorithms = list(data.keys())
        means = [data[algo]["mean"] for algo in algorithms]
        stddevs = [data[algo]["stddev"] for algo in algorithms]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(algorithms))
        ax.bar(x, means, yerr=stddevs, capsize=10, width=0.6, 
               color="skyblue", edgecolor="black", linewidth=1)
        
        ax.set_xlabel("Algorithm")
        ax.set_ylabel("Time (ms)")
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=45, ha="right")
        
        # Add values on bars
        for i, v in enumerate(means):
            ax.text(i, v + 0.1, f"{v:.2f} ms", ha="center", fontweight="bold")
        
        fig.tight_layout()
        plt.savefig(output_file)
        plt.close()
    
    def _plot_encryption_decryption(self, output_file: str):
        """Plot encryption and decryption performance."""
        if "encryption" not in self.results or "decryption" not in self.results:
            return
        
        # Extract data
        encryption_data = self.results["encryption"]
        decryption_data = self.results["decryption"]
        
        operations = []
        means = []
        stddevs = []
        
        for op, data in encryption_data.items():
            operations.append(op)
            means.append(data["mean"])
            stddevs.append(data["stddev"])
        
        for op, data in decryption_data.items():
            operations.append(op)
            means.append(data["mean"])
            stddevs.append(data["stddev"])
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(operations))
        ax.bar(x, means, yerr=stddevs, capsize=10, width=0.6, 
               color="lightgreen", edgecolor="black", linewidth=1)
        
        ax.set_xlabel("Operation")
        ax.set_ylabel("Time (ms)")
        ax.set_title("Encryption/Decryption Performance")
        ax.set_xticks(x)
        ax.set_xticklabels(operations, rotation=45, ha="right")
        
        # Add values on bars
        for i, v in enumerate(means):
            ax.text(i, v + 0.1, f"{v:.2f} ms", ha="center", fontweight="bold")
        
        fig.tight_layout()
        plt.savefig(output_file)
        plt.close()


def run_benchmarks(iterations: int = 100, output_dir: str = "benchmark_results"):
    """
    Run all benchmarks and save results.
    
    Args:
        iterations: Number of iterations for each test
        output_dir: Directory to save results
    """
    print(f"Running benchmarks with {iterations} iterations...")
    
    benchmark = QuantumBenchmark(iterations=iterations)
    results = benchmark.run_all_benchmarks()
    
    # Save results
    import os
    import json
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Plot results
    print("Generating plots...")
    benchmark.plot_results(output_dir=output_dir)
    
    print(f"Benchmarks completed. Results saved to {output_dir}")


if __name__ == "__main__":
    run_benchmarks() 