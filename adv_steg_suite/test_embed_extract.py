from stego.image_stego import embed_lsb, extract_lsb
from PIL import Image
import os

# Create a simple test image
def create_test_image():
    img = Image.new('RGB', (100, 100), color='white')
    img.save('test_input.png')
    return 'test_input.png'

# Test basic embedding and extraction
def test_basic_stego():
    test_data = b"Hello, this is a test message!"
    input_image = create_test_image()
    output_image = 'test_output.png'
    
    # Embed data
    embed_lsb(input_image, test_data, output_image)
    print("Data embedded successfully")
    
    # Extract data
    extracted_data = extract_lsb(output_image)
    print(f"Extracted data: {extracted_data}")
    
    # Verify
    if extracted_data == test_data:
        print("✅ Test passed: Data matches!")
    else:
        print("❌ Test failed: Data doesn't match!")
    
    # Cleanup
    os.remove(input_image)
    os.remove(output_image)

if __name__ == '__main__':
    test_basic_stego()