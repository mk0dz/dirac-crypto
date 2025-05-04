"""
Encoding and serialization utility functions.
"""

import base64
import os
from typing import Dict, Any

def convert_to_base64(data: bytes) -> str:
    """Convert bytes to base64 string."""
    return base64.b64encode(data).decode('utf-8')

def convert_from_base64(data: str) -> bytes:
    """Convert base64 string to bytes."""
    return base64.b64decode(data)

def generate_random_bytes(length: int = 32) -> bytes:
    """Generate random bytes."""
    return os.urandom(length)

def ensure_json_serializable(obj: Any) -> Any:
    """Recursively ensure an object is JSON serializable."""
    if isinstance(obj, bytes):
        return convert_to_base64(obj)
    elif isinstance(obj, dict):
        return {k: ensure_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_json_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return ensure_json_serializable(obj.__dict__)
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        return str(obj) 