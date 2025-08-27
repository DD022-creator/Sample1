from stego.advanced_stego import encode_data_into_image, decode_data_from_image, get_image_capacity

def test_complete_workflow():
    print("Testing complete encode/decode workflow...")
    
    # Test message
    message = "This is a secret message for testing the complete workflow!"
    
    # Get capacity
    capacity = get_image_capacity("input.png", lsb_bits=2)
    print(f"Image capacity: {capacity['capacity_bytes']} bytes")
    print(f"Message size: {len(message.encode())} bytes")
    
    # Encode
    print("\nEncoding...")
    encode_result = encode_data_into_image(
        "input.png", 
        message.encode(), 
        "testpassword", 
        "complete_test.png",
        lsb_bits=2,
        use_compression=True
    )
    
    print(f"✅ {encode_result['message']}")
    print(f"Security score: {encode_result['security_score']:.3f}")
    
    # Decode
    print("\nDecoding...")
    decode_result = decode_data_from_image("complete_test.png", "testpassword", expected_lsb_bits=2)
    
    if decode_result['success']:
        print(f"✅ {decode_result['message']}")
        print(f"Decoded message: {decode_result['data'].decode()}")
    else:
        print(f"❌ {decode_result['error']}")

if __name__ == "__main__":
    test_complete_workflow()