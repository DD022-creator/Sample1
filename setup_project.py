#!/usr/bin/env python3
"""
Setup script for the Underwater Sound Analyzer project.
This script creates the necessary directory structure and sample files.
"""

import os
import subprocess
import sys

def create_directory_structure():
    """Create the required directory structure"""
    directories = [
        'model',
        'data/input',
        'data/output',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create __init__.py files
    for init_file in ['model/__init__.py', 'data/__init__.py']:
        with open(init_file, 'w') as f:
            f.write('# Package initialization\n')
        print(f"Created: {init_file}")

def generate_sample_files():
    """Generate sample model and data files"""
    print("\nGenerating sample files...")
    
    # Generate sample model
    try:
        from model.create_sample_model import create_sample_model
        model = create_sample_model()
        model.save('model/underwater_sound_model.h5')
        print("Generated sample model: model/underwater_sound_model.h5")
    except Exception as e:
        print(f"Error generating model: {e}")
    
    # Generate sample audio files
    try:
        from data.input.generate_sample_audio import generate_sample_audio
        generate_sample_audio()
    except Exception as e:
        print(f"Error generating audio samples: {e}")
    
    # Generate sample output
    try:
        from data.output.generate_sample_output import generate_sample_output
        generate_sample_output()
    except Exception as e:
        print(f"Error generating sample output: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\nChecking dependencies...")
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow: {tf.__version__}")
    except ImportError:
        print("✗ TensorFlow not installed")
    
    try:
        import librosa
        print(f"✓ Librosa: {librosa.__version__}")
    except ImportError:
        print("✗ Librosa not installed")
    
    try:
        import numpy as np
        print(f"✓ NumPy: {np.__version__}")
    except ImportError:
        print("✗ NumPy not installed")

def main():
    """Main setup function"""
    print("Setting up Underwater Sound Analyzer project...")
    
    create_directory_structure()
    generate_sample_files()
    check_dependencies()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Place your .wav files in data/input/")
    print("2. Build the Docker image: docker build -t underwater-sound-analyzer .")
    print("3. Run the analyzer: docker run -v $(pwd)/data/input:/data/input -v $(pwd)/data/output:/data/output underwater-sound-analyzer")
    print("4. Check results in data/output/results.json")

if __name__ == "__main__":
    main()