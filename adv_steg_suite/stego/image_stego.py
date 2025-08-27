from PIL import Image
import struct
import numpy as np
from scipy import stats

def embed_lsb(image_path: str, data: bytes, output_path: str, lsb_bits: int = 1) -> None:
    """
    Embeds data into the LSB of an image with configurable bits.
    
    Args:
        image_path: Path to carrier image
        data: Data to hide
        output_path: Path to save stego image
        lsb_bits: Number of LSB bits to use (1-4)
    """
    if lsb_bits < 1 or lsb_bits > 4:
        raise ValueError("lsb_bits must be between 1 and 4")
    
    img = Image.open(image_path)
    pixels = np.array(img)
    
    if len(pixels.shape) == 2:  # Grayscale
        height, width = pixels.shape
        channels = 1
    else:  # Color (RGB/RGBA)
        height, width, channels = pixels.shape
        if channels > 3:  # If RGBA, use only RGB
            pixels = pixels[:, :, :3]
            channels = 3
    
    # Calculate capacity and validate
    total_bits = width * height * channels * lsb_bits
    required_bits = (len(data) + 4) * 8  # +4 for length header
    
    if required_bits > total_bits:
        raise ValueError(
            f"Data too large for image. "
            f"Capacity: {total_bits//8} bytes, "
            f"Required: {len(data)+4} bytes. "
            f"Try using more LSB bits or a larger image."
        )
    
    # Prepend data length header
    data_with_header = struct.pack('>I', len(data)) + data
    data_bits = ''.join(format(byte, '08b') for byte in data_with_header)
    data_index = 0
    
    # Create bit mask for LSB manipulation
    lsb_mask = (1 << lsb_bits) - 1
    clear_mask = 0xFF ^ lsb_mask
    
    # Flatten image for easier processing
    flat_pixels = pixels.flatten()
    
    for i in range(len(flat_pixels)):
        if data_index >= len(data_bits):
            break
            
        # Get the next lsb_bits from our data
        if data_index + lsb_bits <= len(data_bits):
            current_bits = data_bits[data_index:data_index + lsb_bits]
        else:
            # Pad with zeros if needed
            current_bits = data_bits[data_index:].ljust(lsb_bits, '0')
        
        data_bits_value = int(current_bits, 2)
        
        # Clear the LSB bits and set them to our data bits
        current_pixel = flat_pixels[i]
        new_pixel = (current_pixel & clear_mask) | data_bits_value
        flat_pixels[i] = new_pixel
        
        data_index += lsb_bits
    
    # Reshape back to original dimensions
    if len(pixels.shape) == 2:
        pixels = flat_pixels.reshape((height, width))
    else:
        pixels = flat_pixels.reshape((height, width, channels))
    
    # Save the result
    result_img = Image.fromarray(pixels)
    result_img.save(output_path, 'PNG')

def extract_lsb(stego_image_path: str, lsb_bits: int = 1) -> bytes:
    """
    Extracts data hidden with embed_lsb from a stego image.
    
    Args:
        stego_image_path: Path to stego image
        lsb_bits: Number of LSB bits used during embedding
    
    Returns:
        Extracted data bytes
    """
    img = Image.open(stego_image_path)
    pixels = np.array(img)
    
    if len(pixels.shape) == 2:  # Grayscale
        height, width = pixels.shape
        channels = 1
    else:  # Color
        height, width, channels = pixels.shape
        if channels > 3:  # Use only RGB
            pixels = pixels[:, :, :3]
            channels = 3
    
    # Flatten for processing
    flat_pixels = pixels.flatten()
    
    extracted_bits = []
    data_length = None
    extracted_data = b''
    lsb_mask = (1 << lsb_bits) - 1
    
    for pixel in flat_pixels:
        # Extract the LSB bits
        lsb_value = pixel & lsb_mask
        bits = format(lsb_value, f'0{lsb_bits}b')
        extracted_bits.extend(list(bits))
        
        # Process when we have enough bits for bytes
        while len(extracted_bits) >= 8:
            byte_bits = ''.join(extracted_bits[:8])
            extracted_bits = extracted_bits[8:]
            
            byte_value = int(byte_bits, 2)
            extracted_data += bytes([byte_value])
            
            # Check for length header
            if len(extracted_data) == 4 and data_length is None:
                data_length = struct.unpack('>I', extracted_data)[0]
                extracted_data = b''  # Reset for payload
            
            # Check if we have the full payload
            if data_length is not None and len(extracted_data) == data_length:
                return extracted_data
    
    return extracted_data if data_length is not None else None

def calculate_capacity(image_path: str, lsb_bits: int = 1) -> dict:
    """
    Calculate the data hiding capacity of an image.
    
    Args:
        image_path: Path to the image
        lsb_bits: Number of LSB bits to use
    
    Returns:
        Dictionary with capacity information
    """
    img = Image.open(image_path)
    pixels = np.array(img)
    
    if len(pixels.shape) == 2:  # Grayscale
        height, width = pixels.shape
        channels = 1
    else:  # Color
        height, width, channels = pixels.shape
        if channels > 3:  # Use only RGB
            channels = 3
    
    total_pixels = width * height
    total_bits = total_pixels * channels * lsb_bits
    usable_bits = total_bits - 32  # Reserve 32 bits for length header
    
    return {
        'width': width,
        'height': height,
        'channels': channels,
        'total_pixels': total_pixels,
        'lsb_bits': lsb_bits,
        'total_bits': total_bits,
        'usable_bits': usable_bits,
        'capacity_bytes': usable_bits // 8,
        'capacity_kb': usable_bits // (8 * 1024),
        'message': f"Capacity: {usable_bits//8} bytes ({usable_bits//(8*1024)} KB) using {lsb_bits} LSB bits"
    }

def analyze_security(image_path: str) -> float:
    """
    Analyze how detectable the steganography is.
    Returns a security score between 0 (easily detectable) and 1 (very stealthy).
    
    Args:
        image_path: Path to the image to analyze
    
    Returns:
        Security score (0.0 to 1.0)
    """
    try:
        img = Image.open(image_path)
        pixels = np.array(img.convert('L'))  # Convert to grayscale for analysis
        
        # Calculate statistical features that might indicate steganography
        mean = np.mean(pixels)
        std_dev = np.std(pixels)
        entropy = stats.entropy(np.histogram(pixels, bins=256, density=True)[0])
        
        # Analyze LSB distribution (steganography often makes LSBs more random)
        lsb = pixels & 1
        lsb_entropy = stats.entropy(np.histogram(lsb, bins=2, density=True)[0])
        
        # Normalize features to 0-1 range
        normalized_std = min(std_dev / 50, 1.0)  # Assuming std_dev < 50 is normal
        normalized_entropy = entropy / 8  # Max entropy for 8-bit is ~8
        normalized_lsb_entropy = lsb_entropy / 1.0  # Max entropy for binary is 1.0
        
        # Weighted combination of features
        security_score = (
            0.3 * normalized_std +
            0.3 * normalized_entropy +
            0.4 * normalized_lsb_entropy
        )
        
        return min(max(security_score, 0.0), 1.0)
        
    except Exception:
        # Return neutral score if analysis fails
        return 0.5

def compare_images(original_path: str, stego_path: str) -> dict:
    """
    Compare original and stego images to analyze changes.
    
    Args:
        original_path: Path to original image
        stego_path: Path to stego image
    
    Returns:
        Dictionary with comparison metrics
    """
    original = np.array(Image.open(original_path).convert('RGB'))
    stego = np.array(Image.open(stego_path).convert('RGB'))
    
    if original.shape != stego.shape:
        raise ValueError("Images must have the same dimensions")
    
    # Calculate differences
    diff = np.abs(original.astype(int) - stego.astype(int))
    max_diff = np.max(diff)
    avg_diff = np.mean(diff)
    changed_pixels = np.sum(diff > 0)
    total_pixels = original.size // 3  # RGB has 3 channels
    
    # Calculate PSNR (Peak Signal-to-Noise Ratio)
    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        psnr = float('inf')
    else:
        psnr = 20 * np.log10(255.0 / np.sqrt(mse))
    
    return {
        'max_pixel_difference': int(max_diff),
        'average_pixel_difference': float(avg_diff),
        'changed_pixels': int(changed_pixels),
        'changed_percent': float((changed_pixels / total_pixels) * 100),
        'psnr': float(psnr),
        'mse': float(mse),
        'visibility': (
            "Imperceptible" if psnr > 40 else
            "Very slight" if psnr > 30 else
            "Noticeable" if psnr > 20 else
            "Very visible"
        )
    }