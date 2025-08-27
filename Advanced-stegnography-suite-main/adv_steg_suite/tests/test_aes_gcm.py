import pytest
from crypto.aes_gcm import encrypt_bytes, decrypt_bytes

def test_encrypt_decrypt_roundtrip():
    """Test that encrypting and then decrypting returns the original data."""
    original_data = b"This is a super secret message!"
    password = "my_strong_password_123"
    
    encrypted = encrypt_bytes(original_data, password)
    decrypted = decrypt_bytes(encrypted, password)
    
    assert decrypted == original_data, "Decrypted data does not match original!"

def test_wrong_password_fails():
    """Test that decrypting with the wrong password raises an error."""
    original_data = b"Secret data"
    correct_password = "right"
    wrong_password = "wrong"
    
    encrypted = encrypt_bytes(original_data, correct_password)
    
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_bytes(encrypted, wrong_password)

def test_tampered_data_fails():
    """Test that tampering with the ciphertext makes decryption fail."""
    original_data = b"Integrity is important"
    password = "password"
    
    encrypted = encrypt_bytes(original_data, password)
    # Tamper with the ciphertext part (skip the salt and nonce)
    tampered_encrypted = encrypted[:28] + bytes([encrypted[28] ^ 0xFF]) + encrypted[29:]
    
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_bytes(tampered_encrypted, password)