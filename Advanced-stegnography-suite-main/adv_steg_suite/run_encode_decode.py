from stego.advanced_stego import encode_data_into_image, decode_data_from_image

# Configuration
CARRIER_IMAGE = "input.png"
STEGO_IMAGE = "stego_image.png"
SECRET_MESSAGE = "This is my hidden secret.".encode()
PASSWORD = "ultra_secure_password"

# Encode the secret into the image
encode_data_into_image(CARRIER_IMAGE, SECRET_MESSAGE, PASSWORD, STEGO_IMAGE)

# Decode the secret from the image
decoded_secret = decode_data_from_image(STEGO_IMAGE, PASSWORD)

if decoded_secret:
    print(f"Decoded secret message: {decoded_secret.decode()}")