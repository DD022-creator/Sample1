"""
Command-Line Interface (CLI) for the Advanced Steganography Suite.
Handles user arguments for encoding and decoding operations.
"""
import argparse
from stego.advanced_stego import encode_data_into_image, decode_data_from_image

def main():
    """Main CLI entry point. Parses arguments and executes the chosen command."""
    parser = argparse.ArgumentParser(
        description="Advanced Steganography Suite - Hide and extract secret messages in images securely.",
        epilog="Example:\n  %(prog)s encode -c input.png -p \"secret\" -o stego.png\n  %(prog)s decode -s stego.png -p \"secret\"",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute', required=True)

    # Parser for the 'encode' command
    encode_parser = subparsers.add_parser('encode', help='Encode a secret message into an image')
    encode_parser.add_argument('-c', '--carrier', required=True, help='Path to the carrier image (input.png)')
    encode_parser.add_argument('-d', '--data', help='Text message to hide or path to text file.')
    encode_parser.add_argument('-f', '--file', help='Binary file to hide (alternative to --data)')
    encode_parser.add_argument('-p', '--password', required=True, help='Password for encryption')
    encode_parser.add_argument('-o', '--output', required=True, help='Path to save the stego image (output.png)')

    # Parser for the 'decode' command
    decode_parser = subparsers.add_parser('decode', help='Decode a secret message from an image')
    decode_parser.add_argument('-s', '--stego', required=True, help='Path to the stego image (stego.png)')
    decode_parser.add_argument('-p', '--password', required=True, help='Password used during encoding')
    decode_parser.add_argument('-o', '--output', help='File to save the decoded output (optional)')

    args = parser.parse_args()

    # Execute the encode command
    if args.command == 'encode':
        # Handle the payload input (either text, file, or error)
        payload = None
        if args.data:
            # Check if the argument is a file path that exists
            try:
                with open(args.data, 'rb') as f:
                    payload = f.read()
                print(f"Reading data from file: {args.data}")
            except (FileNotFoundError, OSError):
                # If file doesn't exist, treat it as text
                payload = args.data.encode()
                print("Using provided text data")
        elif args.file:
            try:
                with open(args.file, 'rb') as f:
                    payload = f.read()
                print(f"Reading data from file: {args.file}")
            except FileNotFoundError:
                print(f"Error: File {args.file} not found.")
                return
        else:
            print("Error: You must provide either --data or --file to encode.")
            return

        # Perform the encoding
        try:
            encode_data_into_image(args.carrier, payload, args.password, args.output)
            print(f"Encoding successful. Stego image saved to: {args.output}")
        except Exception as e:
            print(f"Encoding failed: {e}")

    # Execute the decode command
    elif args.command == 'decode':
        try:
            decoded_data = decode_data_from_image(args.stego, args.password)
            if decoded_data is None:
                return  # Decryption failed, error already printed

            # Handle the output (print to screen or save to file)
            if args.output:
                try:
                    with open(args.output, 'wb') as f:
                        f.write(decoded_data)
                    print(f"Decoding successful. Output saved to: {args.output}")
                except IOError as e:
                    print(f"Error writing to file {args.output}: {e}")
            else:
                # Try to decode as text (try multiple encodings)
                text_output = None
                for encoding in ['utf-8', 'utf-16', 'latin-1']:
                    try:
                        text_output = decoded_data.decode(encoding)
                        print(f"Decoded message ({encoding}):")
                        print(text_output)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if text_output is None:
                    print("Decoded binary data (first 100 bytes in hex):")
                    print(decoded_data[:100].hex(' '))
        except Exception as e:
            print(f"Decoding failed: {e}")

if __name__ == '__main__':
    main()