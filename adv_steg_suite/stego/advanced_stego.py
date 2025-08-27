from crypto.aes_gcm import encrypt_bytes, decrypt_bytes
from stego.image_stego import embed_lsb, extract_lsb, analyze_security, calculate_capacity
import zlib

def encode_data_into_image(carrier_image_path: str, payload: bytes, password: str, 
                          output_image_path: str, lsb_bits: int = 1, use_compression: bool = True) -> dict:
    """
    The full encode pipeline with advanced options.
    
    Args:
        carrier_image_path: Path to the carrier image
        payload: Data to hide
        password: Encryption password
        output_image_path: Path to save stego image
        lsb_bits: How many LSBs to use (1-4)
        use_compression: Whether to compress data before encryption
    
    Returns:
        Dictionary with operation details and metrics
    """
    
    # Calculate capacity and check if data fits
    capacity_info = calculate_capacity(carrier_image_path, lsb_bits)
    required_space = len(payload) + 100  # Add overhead for header and encryption
    
    if required_space > capacity_info['capacity_bytes']:
        raise ValueError(
            f"Data too large for image. "
            f"Capacity: {capacity_info['capacity_bytes']} bytes, "
            f"Required: {required_space} bytes. "
            f"Try using more LSB bits or a larger image."
        )
    
    original_payload_size = len(payload)
    
    # 1. Compress the payload (if enabled)
    if use_compression:
        compressed_payload = zlib.compress(payload)
        compression_ratio = original_payload_size / len(compressed_payload)
    else:
        compressed_payload = payload
        compression_ratio = 1.0
    
    # 2. Encrypt the payload
    encrypted_payload = encrypt_bytes(compressed_payload, password)
    
    # 3. Embed the encrypted payload into the image
    embed_lsb(carrier_image_path, encrypted_payload, output_image_path, lsb_bits)
    
    # 4. Analyze security of the stego image
    security_score = analyze_security(output_image_path)
    
    # Return detailed metrics
    return {
        'success': True,
        'original_size': original_payload_size,
        'compressed_size': len(compressed_payload) if use_compression else original_payload_size,
        'encrypted_size': len(encrypted_payload),
        'compression_ratio': round(compression_ratio, 2),
        'capacity_used_percent': round((len(encrypted_payload) / capacity_info['capacity_bytes']) * 100, 1),
        'security_score': security_score,
        'lsb_bits_used': lsb_bits,
        'compression_used': use_compression,
        'output_path': output_image_path,
        'message': f"✅ Successfully encoded {original_payload_size} bytes into {output_image_path}"
    }

def decode_data_from_image(stego_image_path: str, password: str, 
                          expected_lsb_bits: int = 1) -> dict:
    """
    The full decode pipeline with enhanced error handling.
    
    Args:
        stego_image_path: Path to the stego image
        password: Encryption password
        expected_lsb_bits: Number of LSB bits used during encoding
    
    Returns:
        Dictionary with decoded data and operation details
    """
    
    try:
        # 1. Extract the encrypted payload from the image
        encrypted_payload = extract_lsb(stego_image_path, expected_lsb_bits)
        
        if encrypted_payload is None:
            return {
                'success': False,
                'error': "No data found in image or extraction failed"
            }
        
        # 2. Decrypt the payload
        try:
            compressed_payload = decrypt_bytes(encrypted_payload, password)
        except ValueError as e:
            return {
                'success': False,
                'error': f"Decryption failed: {e}"
            }
        
        # 3. Decompress the payload (try both compressed and uncompressed)
        try:
            original_payload = zlib.decompress(compressed_payload)
            was_compressed = True
        except zlib.error:
            # Data might not have been compressed
            original_payload = compressed_payload
            was_compressed = False
        
        # 4. Analyze the stego image security
        security_score = analyze_security(stego_image_path)
        
        return {
            'success': True,
            'data': original_payload,
            'data_size': len(original_payload),
            'was_compressed': was_compressed,
            'security_score': security_score,
            'lsb_bits_used': expected_lsb_bits,
            'message': f"✅ Successfully decoded {len(original_payload)} bytes"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Decoding failed: {e}"
        }

def get_image_capacity(image_path: str, lsb_bits: int = 1) -> dict:
    """
    Calculate the hiding capacity of an image.
    
    Args:
        image_path: Path to the image
        lsb_bits: Number of LSB bits to consider
    
    Returns:
        Dictionary with capacity information
    """
    return calculate_capacity(image_path, lsb_bits)

def analyze_stego_security(image_path: str) -> dict:
    """
    Analyze the security of a stego image.
    
    Args:
        image_path: Path to the image to analyze
    
    Returns:
        Dictionary with security analysis results
    """
    score = analyze_security(image_path)
    
    security_level = "High"
    if score < 0.3:
        security_level = "Low"
    elif score < 0.6:
        security_level = "Medium"
    
    return {
        'security_score': score,
        'security_level': security_level,
        'detection_risk': f"{((1 - score) * 100):.1f}%",
        'recommendation': f"Security level: {security_level}. " +
                         ("Consider using fewer LSB bits for better stealth." if score < 0.6 
                          else "Good stealth characteristics detected.")
    }
from crypto.aes_gcm import encrypt_bytes, decrypt_bytes
from stego.audio_stego import embed_lsb_audio, extract_lsb_audio, analyze_audio_security, calculate_audio_capacity
import zlib

def encode_data_into_audio(carrier_audio_path: str, payload: bytes, password: str,
                          output_audio_path: str, lsb_bits: int = 1, use_compression: bool = True) -> dict:
    """Full audio encode pipeline with compression & encryption."""

    # Check capacity
    capacity_info = calculate_audio_capacity(carrier_audio_path, lsb_bits)
    required_space = len(payload) + 100
    if required_space > capacity_info['capacity_bytes']:
        raise ValueError(
            f"Data too large for audio. Capacity: {capacity_info['capacity_bytes']} bytes, Required: {required_space} bytes."
        )

    original_payload_size = len(payload)

    # 1. Compress (optional)
    if use_compression:
        compressed_payload = zlib.compress(payload)
        compression_ratio = original_payload_size / len(compressed_payload)
    else:
        compressed_payload = payload
        compression_ratio = 1.0

    # 2. Encrypt
    encrypted_payload = encrypt_bytes(compressed_payload, password)

    # 3. Embed into audio
    embed_lsb_audio(carrier_audio_path, encrypted_payload, output_audio_path, lsb_bits)

    # 4. Analyze security
    security_score = analyze_audio_security(output_audio_path)

    return {
        'success': True,
        'original_size': original_payload_size,
        'compressed_size': len(compressed_payload),
        'encrypted_size': len(encrypted_payload),
        'compression_ratio': round(compression_ratio, 2),
        'capacity_used_percent': round((len(encrypted_payload) / capacity_info['capacity_bytes']) * 100, 1),
        'security_score': security_score,
        'output_path': output_audio_path,
        'message': f"✅ Successfully encoded {original_payload_size} bytes into {output_audio_path}"
    }

def decode_data_from_audio(stego_audio_path: str, password: str, expected_lsb_bits: int = 1) -> dict:
    """Full audio decode pipeline with error handling."""

    try:
        # 1. Extract
        encrypted_payload = extract_lsb_audio(stego_audio_path, expected_lsb_bits)
        if encrypted_payload is None:
            return {'success': False, 'error': "No data found in audio"}

        # 2. Decrypt
        try:
            compressed_payload = decrypt_bytes(encrypted_payload, password)
        except ValueError as e:
            return {'success': False, 'error': f"Decryption failed: {e}"}

        # 3. Decompress
        try:
            original_payload = zlib.decompress(compressed_payload)
            was_compressed = True
        except zlib.error:
            original_payload = compressed_payload
            was_compressed = False

        security_score = analyze_audio_security(stego_audio_path)

        return {
            'success': True,
            'data': original_payload,
            'data_size': len(original_payload),
            'was_compressed': was_compressed,
            'security_score': security_score,
            'message': f"✅ Successfully decoded {len(original_payload)} bytes"
        }

    except Exception as e:
        return {'success': False, 'error': f"Decoding failed: {e}"}
from crypto.aes_gcm import encrypt_bytes, decrypt_bytes
from stego.video_stego import embed_lsb_video, extract_lsb_video, analyze_video_security, calculate_video_capacity
import zlib

def encode_data_into_video(carrier_video_path: str, payload: bytes, password: str,
                          output_video_path: str, lsb_bits: int = 1, use_compression: bool = True) -> dict:
    """Full video encode pipeline with compression & encryption."""

    capacity_info = calculate_video_capacity(carrier_video_path, lsb_bits)
    required_space = len(payload) + 100
    if required_space > capacity_info['capacity_bytes']:
        raise ValueError(
            f"Data too large for video. Capacity: {capacity_info['capacity_bytes']} bytes, Required: {required_space} bytes."
        )

    original_payload_size = len(payload)

    if use_compression:
        compressed_payload = zlib.compress(payload)
        compression_ratio = original_payload_size / len(compressed_payload)
    else:
        compressed_payload = payload
        compression_ratio = 1.0

    encrypted_payload = encrypt_bytes(compressed_payload, password)

    embed_lsb_video(carrier_video_path, encrypted_payload, output_video_path, lsb_bits)

    security_score = analyze_video_security(output_video_path)

    return {
        'success': True,
        'original_size': original_payload_size,
        'compressed_size': len(compressed_payload),
        'encrypted_size': len(encrypted_payload),
        'compression_ratio': round(compression_ratio, 2),
        'capacity_used_percent': round((len(encrypted_payload) / capacity_info['capacity_bytes']) * 100, 1),
        'security_score': security_score,
        'output_path': output_video_path,
        'message': f"✅ Successfully encoded {original_payload_size} bytes into {output_video_path}"
    }

def decode_data_from_video(stego_video_path: str, password: str, expected_lsb_bits: int = 1) -> dict:
    """Full video decode pipeline."""

    try:
        encrypted_payload = extract_lsb_video(stego_video_path, expected_lsb_bits)
        if encrypted_payload is None:
            return {'success': False, 'error': "No data found in video"}

        try:
            compressed_payload = decrypt_bytes(encrypted_payload, password)
        except ValueError as e:
            return {'success': False, 'error': f"Decryption failed: {e}"}

        try:
            original_payload = zlib.decompress(compressed_payload)
            was_compressed = True
        except zlib.error:
            original_payload = compressed_payload
            was_compressed = False

        security_score = analyze_video_security(stego_video_path)

        return {
            'success': True,
            'data': original_payload,
            'data_size': len(original_payload),
            'was_compressed': was_compressed,
            'security_score': security_score,
            'message': f"✅ Successfully decoded {len(original_payload)} bytes"
        }

    except Exception as e:
        return {'success': False, 'error': f"Decoding failed: {e}"}
