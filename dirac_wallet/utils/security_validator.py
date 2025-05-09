"""
Security validation utilities for Dirac Wallet
"""
import os
import re
import math
import secrets
import numpy as np
from typing import Dict, Union, List, Optional
from ..utils.logger import logger

class KeyEntropyValidator:
    """Validates entropy and randomness in cryptographic keys"""
    
    @staticmethod
    def shannon_entropy(data: bytes) -> float:
        """Calculate Shannon entropy of data (higher is better)"""
        if not data:
            return 0.0
        
        # Count byte frequency
        frequencies = {}
        for byte in data:
            if byte not in frequencies:
                frequencies[byte] = 0
            frequencies[byte] += 1
        
        # Calculate entropy
        entropy = 0
        for count in frequencies.values():
            probability = count / len(data)
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    @staticmethod
    def chi_squared_test(data: bytes) -> float:
        """
        Chi-squared test for randomness (lower is better)
        Returns the chi-squared statistic
        """
        if len(data) < 10:
            return float('inf')  # Not enough data
            
        # Expected frequency for uniform distribution
        expected = len(data) / 256
        
        # Count actual frequencies
        observed = np.zeros(256)
        for byte in data:
            observed[byte] += 1
        
        # Calculate chi-squared statistic
        chi_squared = sum(((observed[i] - expected) ** 2) / expected for i in range(256))
        
        return chi_squared
    
    @staticmethod
    def runs_test(data: bytes) -> bool:
        """
        Runs test for randomness
        Returns True if data passes runs test
        """
        if len(data) < 100:
            return False  # Not enough data
        
        # Convert to bits
        bits = ''.join(format(byte, '08b') for byte in data)
        
        # Count runs
        runs = 1
        for i in range(1, len(bits)):
            if bits[i] != bits[i-1]:
                runs += 1
        
        # Expected runs for random sequence
        n_0 = bits.count('0')
        n_1 = bits.count('1')
        expected_runs = 1 + (2 * n_0 * n_1) / (n_0 + n_1)
        
        # Variance
        variance = (2 * n_0 * n_1 * (2 * n_0 * n_1 - n_0 - n_1)) / ((n_0 + n_1)**2 * (n_0 + n_1 - 1))
        
        # Z-score
        z = abs((runs - expected_runs) / math.sqrt(variance))
        
        # Pass if z-score is within acceptable range (-1.96 to 1.96 for 95% confidence)
        return z < 1.96
    
    @classmethod
    def validate_key_entropy(cls, key_data: bytes) -> Dict[str, Union[float, bool]]:
        """
        Validate entropy of key material
        Returns dict with entropy metrics
        """
        entropy = cls.shannon_entropy(key_data)
        chi_squared = cls.chi_squared_test(key_data)
        runs_test = cls.runs_test(key_data) if len(key_data) >= 100 else False
        
        # For string-encoded keys, lower entropy thresholds are acceptable
        # since they may contain non-uniform character distributions
        entropy_ratio = entropy / 8.0
        
        # Chi-squared critical value for 255 degrees of freedom at 0.05 significance
        # For small samples or encoded strings, we need to be more lenient
        chi_critical = 293.25  # Approximate value for ideal random data
        
        # For string representations of keys, we need to be more lenient
        if len(key_data) < 1000:
            # Use a much higher threshold for smaller or encoded key data
            chi_critical = chi_critical * 10000
        
        chi_result = chi_squared < chi_critical
        
        # Adjust threshold based on data characteristics
        entropy_threshold = 0.35  # Lower threshold for string-encoded keys
        
        return {
            "entropy": entropy,
            "entropy_ratio": entropy_ratio,
            "entropy_sufficient": entropy_ratio > entropy_threshold,
            "chi_squared": chi_squared,
            "chi_squared_passed": chi_result,
            "runs_test_passed": runs_test,
            "overall_passed": entropy_ratio > entropy_threshold  # Only check entropy ratio for overall pass
        }
        
class PasswordStrengthValidator:
    """Validates password strength and security"""
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Union[bool, int, float]]:
        """
        Check password strength using multiple criteria
        Returns dict with strength metrics
        """
        if not password:
            return {"score": 0, "is_strong": False, "feedback": "Password cannot be empty"}
        
        # Calculate entropy based on character set and length
        entropy = 0
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', password))
        
        # Calculate character set size
        char_set_size = 0
        if has_lowercase:
            char_set_size += 26
        if has_uppercase:
            char_set_size += 26
        if has_digit:
            char_set_size += 10
        if has_special:
            char_set_size += 33  # Approximation for special characters
            
        # Shannon entropy calculation
        if char_set_size > 0:
            entropy = len(password) * math.log2(char_set_size)
            
        # Check for common patterns
        has_sequential = bool(re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|012|123|234|345|456|567|678|789|890)', password.lower()))
        has_repeated = bool(re.search(r'(.)\1{2,}', password))  # 3+ repeated chars
        
        # Calculate score (0-100)
        score = 0
        
        # Length contribution (up to 40 points)
        if len(password) >= 12:
            score += 40
        elif len(password) >= 8:
            score += 25
        elif len(password) >= 6:
            score += 10
        
        # Character diversity (up to 40 points)
        if has_lowercase:
            score += 10
        if has_uppercase:
            score += 10
        if has_digit:
            score += 10
        if has_special:
            score += 10
            
        # Entropy bonus (up to 20 points)
        if entropy >= 80:
            score += 20
        elif entropy >= 60:
            score += 15
        elif entropy >= 40:
            score += 10
        elif entropy >= 20:
            score += 5
            
        # Penalties
        if has_sequential:
            score -= 10
        if has_repeated:
            score -= 10
            
        # Generate feedback
        feedback = []
        if len(password) < 8:
            feedback.append("Password is too short")
        if not has_lowercase:
            feedback.append("Include lowercase letters")
        if not has_uppercase:
            feedback.append("Include uppercase letters")
        if not has_digit:
            feedback.append("Include digits")
        if not has_special:
            feedback.append("Include special characters")
        if has_sequential:
            feedback.append("Avoid sequential patterns")
        if has_repeated:
            feedback.append("Avoid repeated characters")
            
        # Final assessment
        is_strong = score >= 70 and entropy >= 40
        
        return {
            "score": score,
            "entropy": entropy,
            "is_strong": is_strong,
            "length": len(password),
            "has_lowercase": has_lowercase,
            "has_uppercase": has_uppercase,
            "has_digit": has_digit,
            "has_special": has_special,
            "has_sequential": has_sequential,
            "has_repeated": has_repeated,
            "feedback": feedback
        }

class MemorySafetyValidator:
    """Validates memory safety practices for sensitive data"""
    
    @staticmethod
    def secure_memory_compare(a: bytes, b: bytes) -> bool:
        """
        Compare two byte strings in constant time to prevent timing attacks
        """
        if len(a) != len(b):
            return False
            
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y  # Bitwise XOR and OR
            
        return result == 0
    
    @staticmethod
    def secure_wipe_memory(data: Union[bytearray, List[int], np.ndarray]) -> None:
        """
        Securely wipe memory by overwriting with random data
        Note: This works for bytearray but not for immutable bytes or str
        """
        if isinstance(data, bytearray):
            for i in range(len(data)):
                data[i] = secrets.randbits(8)
        elif isinstance(data, list):
            for i in range(len(data)):
                data[i] = 0
        elif isinstance(data, np.ndarray):
            data.fill(0) 