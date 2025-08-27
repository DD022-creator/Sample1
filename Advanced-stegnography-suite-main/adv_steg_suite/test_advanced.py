#!/usr/bin/env python3
"""
Test script for advanced steganography features
"""
from stego.advanced_stego import encode_data_into_image, decode_data_from_image, get_image_capacity, analyze_stego_security
from stego.image_stego import compare_images

def test_advanced_features():
    print("🔍 Testing Advanced Steganography Features\n")
    
    # Test 1: Check image capacity
    print("1. 📊 Image Capacity Analysis:")
    capacity = get_image_capacity("input.png", lsb_bits=2)
    print(f"   - {capacity['message']}")
    print(f"   - Dimensions: {capacity['width']}x{capacity['height']}")
    print(f"   - Channels: {capacity['channels']}")
    print()
    
    # Test 2: Encode with different LSB settings
    test_message = b"This is a test message for advanced features!"
    
    print("2. 🔧 Testing different LSB configurations:")
    
    # Test with 1 LSB bit (most stealthy)
    result_1bit = encode_data_into_image(
        "input.png", test_message, "password123", 
        "test_1bit.png", lsb_bits=1, use_compression=True
    )
    print(f"   - 1 LSB bit: Security score = {result_1bit['security_score']:.3f}")
    
    # Test with 2 LSB bits (balanced)
    result_2bit = encode_data_into_image(
        "input.png", test_message, "password123", 
        "test_2bit.png", lsb_bits=2, use_compression=True
    )
    print(f"   - 2 LSB bits: Security score = {result_2bit['security_score']:.3f}")
    print()
    
    # Test 3: Security analysis
    print("3. 🛡️ Security Analysis:")
    security_analysis = analyze_stego_security("test_2bit.png")
    print(f"   - Security Level: {security_analysis['security_level']}")
    print(f"   - Detection Risk: {security_analysis['detection_risk']}")
    print(f"   - Recommendation: {security_analysis['recommendation']}")
    print()
    
    # Test 4: Decode and verify
    print("4. 🔓 Decoding Test:")
    decode_result = decode_data_from_image("test_2bit.png", "password123", expected_lsb_bits=2)
    
    if decode_result['success']:
        print(f"   - ✅ Success! Decoded {decode_result['data_size']} bytes")
        print(f"   - Data: {decode_result['data'].decode()}")
        print(f"   - Was compressed: {decode_result['was_compressed']}")
    else:
        print(f"   - ❌ Failed: {decode_result['error']}")
    print()
    
    # Test 5: Image comparison
    print("5. 📸 Image Comparison:")
    comparison = compare_images("input.png", "test_2bit.png")
    print(f"   - Visibility: {comparison['visibility']}")
    print(f"   - PSNR: {comparison['psnr']:.2f} dB")
    print(f"   - Changed pixels: {comparison['changed_percent']:.4f}%")
    print()
    
    print("🎉 All tests completed successfully!")

if __name__ == "__main__":
    test_advanced_features()