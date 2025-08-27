import cv2
import numpy as np

def embed_lsb_video(video_path: str, secret_data: bytes, output_path: str) -> str:
    """
    Embed secret data into video frames using LSB on pixel values.
    Very basic implementation – works best on uncompressed/AVI video.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    # Get video properties
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out    = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Convert data to binary string
    data_bits = ''.join(format(byte, '08b') for byte in secret_data) + "1111111111111110"  
    data_index = 0
    total_bits = len(data_bits)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flatten frame pixels
        flat_frame = frame.flatten()

        for i in range(len(flat_frame)):
            if data_index < total_bits:
                flat_frame[i] = (flat_frame[i] & ~1) | int(data_bits[data_index])
                data_index += 1

        # Reshape and write frame
        frame = flat_frame.reshape(frame.shape)
        out.write(frame)

        if data_index >= total_bits:
            break

    cap.release()
    out.release()

    return f"Data embedded successfully into {output_path}"


def extract_lsb_video(stego_video_path: str) -> bytes:
    """
    Extract hidden data from stego video using LSB.
    """
    cap = cv2.VideoCapture(stego_video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {stego_video_path}")

    bits = ""
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        flat_frame = frame.flatten()
        for pixel in flat_frame:
            bits += str(pixel & 1)

            # Check for delimiter
            if bits.endswith("1111111111111110"):
                cap.release()
                # Remove delimiter and convert to bytes
                bits = bits[:-16]
                return int(bits, 2).to_bytes(len(bits) // 8, byteorder="big")

    cap.release()
    return b""
def analyze_video_security(video_path: str) -> dict:
    """
    Perform a simple security/capacity analysis for video steganography.
    Returns metadata and estimated hiding capacity.
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        # Get video properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps    = cap.get(cv2.CAP_PROP_FPS)
        channels = 3  # Assuming BGR video

        total_pixels = frame_count * width * height * channels
        capacity_bits = total_pixels  # 1 bit per channel per pixel
        capacity_bytes = capacity_bits // 8

        cap.release()

        return {
            "file": video_path,
            "frames": frame_count,
            "resolution": f"{width}x{height}",
            "fps": fps,
            "capacity_bits": capacity_bits,
            "capacity_bytes": capacity_bytes,
            "message": f"Max data that can be hidden: {capacity_bytes} bytes"
        }

    except Exception as e:
        return {
            "file": video_path,
            "error": str(e),
            "capacity_bytes": 0
        }
def calculate_video_capacity(video_path: str) -> int:
    """
    Calculate maximum embedding capacity (in bytes) of the video
    using 1 LSB per color channel.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    channels = 3  # BGR frames

    total_pixels = frame_count * width * height * channels
    capacity_bytes = total_pixels // 8

    cap.release()
    return capacity_bytes
