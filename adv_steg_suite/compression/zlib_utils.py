"""
zlib-based (de)compression routines.
"""
import zlib

def compress_data(data: bytes) -> bytes:
    """Compress bytes via zlib."""
    return zlib.compress(data)

def decompress_data(data: bytes) -> bytes:
    """Decompress bytes via zlib."""
    return zlib.decompress(data)
