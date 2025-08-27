from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.exceptions import InvalidTag
import os

def derive_key(password: str, salt: bytes = None) -> tuple:
    """Derives a cryptographic key from a password using Scrypt KDF."""
    if salt is None:
        salt = os.urandom(16)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key = kdf.derive(password.encode())
    return key, salt

def encrypt_bytes(data: bytes, password: str) -> bytes:
    """Encrypts data using AES-GCM. Returns ciphertext, nonce, and salt."""
    key, salt = derive_key(password)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    # Pack the output: [salt (16)][nonce (12)][ciphertext]
    return salt + nonce + ciphertext

def decrypt_bytes(encrypted_data: bytes, password: str) -> bytes:
    """Decrypts data encrypted with encrypt_bytes."""
    # Unpack the input: [salt (16)][nonce (12)][ciphertext (rest)]
    salt = encrypted_data[:16]
    nonce = encrypted_data[16:28]
    ciphertext = encrypted_data[28:]
    
    key, _ = derive_key(password, salt)
    aesgcm = AESGCM(key)
    try:
        decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        return decrypted_data
    except InvalidTag:
        raise ValueError("Decryption failed. Incorrect password or corrupted data.")