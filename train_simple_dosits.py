# train_simple_dosits.py
import os
import numpy as np
import tensorflow as tf
from datetime import datetime

print("=== SIMPLE DOSITS MODEL TRAINING ===")

def create_simple_dosits_model():
    """Create a simple model that will definitely work"""
    input_shape = (128, 44, 1)
    
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(16, (3, 3), activation='relu', input_shape=input_shape),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(5, activation='softmax')  # 5 classes
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def main():
    """Simple training that will definitely work"""
    # Create simple synthetic data
    print("Creating simple training data...")
    X_train = np.random.rand(100, 128, 44, 1).astype(np.float32)
    y_train = np.random.randint(0, 5, 100)
    
    X_val = np.random.rand(20, 128, 44, 1).astype(np.float32)
    y_val = np.random.randint(0, 5, 20)
    
    # Create and train model
    model = create_simple_dosits_model()
    
    print("Training simple model (5 epochs)...")
    history = model.fit(
        X_train, y_train,
        epochs=5,
        batch_size=16,
        validation_data=(X_val, y_val),
        verbose=1
    )
    
    # Save model
    os.makedirs('models', exist_ok=True)
    model_path = "models/dosits_model_simple.h5"
    model.save(model_path)
    
    print(f"\n✅ Simple DOSITS model created!")
    print(f"📍 Model saved to: {model_path}")
    print(f"📊 Final accuracy: {history.history['accuracy'][-1]:.3f}")

if __name__ == "__main__":
    main()