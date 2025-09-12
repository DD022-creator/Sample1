import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import os

def create_sample_model():
    """Create a sample pre-trained model for demonstration"""
    sample_rate = 22050
    segment_duration = 2.0
    hop_length = 512
    n_mels = 128
    
    # Calculate input shape
    n_frames = int(segment_duration * sample_rate / hop_length) + 1
    input_shape = (n_mels, n_frames, 1)
    
    # Build model
    model = keras.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(5, activation='softmax')  # 4 classes + background
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Create dummy weights (in real scenario, these would be trained on actual data)
    return model

if __name__ == "__main__":
    # Create and save sample model
    model = create_sample_model()
    
    # Create model directory if it doesn't exist
    os.makedirs('model', exist_ok=True)
    
    # Save the model
    model.save('model/underwater_sound_model.h5')
    print("Sample model created and saved as 'model/underwater_sound_model.h5'")
    
    # Save model summary
    with open('model/model_summary.txt', 'w') as f:
        model.summary(print_fn=lambda x: f.write(x + '\n'))
    
    print("Model summary saved as 'model/model_summary.txt'")