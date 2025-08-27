"""
Audio steganography functions for 16-bit PCM WAV files.
"""

import wave
import numpy as np

def embed_lsb_audio(audio_path, data: bytes, output_path: str):
    """Embed data into WAV audio using LSB method (basic version)."""
    try:
        # Open audio file
        with wave.open(audio_path, 'rb') as audio:
            params = audio.getparams()
            frames = bytearray(list(audio.readframes(audio.getnframes())))

        # Convert data to bits
        data_bits = ''.join(format(byte, '08b') for byte in data)
        data_bits += '1111111111111110'  # EOF marker

        if len(data_bits) > len(frames):
            raise ValueError("Data too large for audio file")

        # Embed bits into LSB of audio samples
        for i, bit in enumerate(data_bits):
            frames[i] = (frames[i] & 254) | int(bit)

        # Save stego audio
        with wave.open(output_path, 'wb') as stego:
            stego.setparams(params)
            stego.writeframes(bytes(frames))

        return {"success": True, "message": f"✅ Data embedded into {output_path}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_lsb_audio(stego_audio_path: str) -> bytes:
    """Extract hidden data from WAV audio."""
    try:
        with wave.open(stego_audio_path, 'rb') as audio:
            frames = bytearray(list(audio.readframes(audio.getnframes())))

        # Extract LSBs
        extracted_bits = [str(frames[i] & 1) for i in range(len(frames))]
        extracted_bits = ''.join(extracted_bits)

        # Split into bytes until EOF marker
        all_bytes = [extracted_bits[i:i+8] for i in range(0, len(extracted_bits), 8)]
        data_bytes = bytearray()
        for byte in all_bytes:
            data_bytes.append(int(byte, 2))
            if data_bytes[-2:] == b'\xff\xfe':  # EOF marker
                return bytes(data_bytes[:-2])

        return bytes(data_bytes)

    except Exception as e:
        return b""
def analyze_audio_security(audio_path: str) -> dict:
    """
    Analyze the security/robustness of the audio stego file.
    Placeholder implementation.
    """
    try:
        # In a real implementation, we would check:
        # - Noise levels
        # - Bit depth changes
        # - Possible distortion
        # For now, just return a dummy analysis.
        return {
            "file": audio_path,
            "status": "ok",
            "message": "Audio security analysis not yet implemented"
        }
    except Exception as e:
        return {
            "file": audio_path,
            "status": "error",
            "message": str(e)
        }
import wave

def calculate_audio_capacity(audio_path: str) -> dict:
    """
    Calculate maximum data capacity of an audio file using LSB steganography.
    Works for 16-bit PCM WAV files.
    """
    try:
        with wave.open(audio_path, 'rb') as audio:
            num_frames = audio.getnframes()
            num_channels = audio.getnchannels()
            sample_width = audio.getsampwidth()  # usually 2 bytes (16-bit)

            # Each sample (per channel) gives us 1 bit capacity in LSB
            total_samples = num_frames * num_channels
            capacity_bits = total_samples  # 1 bit per sample
            capacity_bytes = capacity_bits // 8

            return {
                "file": audio_path,
                "frames": num_frames,
                "channels": num_channels,
                "sample_width": sample_width,
                "capacity_bits": capacity_bits,
                "capacity_bytes": capacity_bytes,
                "message": f"Max data that can be hidden: {capacity_bytes} bytes"
            }

    except Exception as e:
        return {
            "file": audio_path,
            "error": str(e),
            "capacity_bytes": 0
        }
