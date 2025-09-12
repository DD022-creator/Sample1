# train_simple_working.py
import os
import numpy as np
import tensorflow as tf
from datetime import datetime

print("=== SIMPLE WORKING MODEL TRAINING ===")

# Create directories
os.makedirs('models', exist_ok=True)

def create_simple_model():
    """Create a simple model that will definitely work"""
    print("Creating simple model...")
    
    # Simple fixed input shape that will work
    input_shape = (128, 44, 1)  # Fixed compatible shape
    num_classes = 5
    
    # Very simple model architecture
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(16, (3, 3), activation='relu', input_shape=input_shape),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    # Simple compile without problematic metrics
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']  # Only accuracy to avoid shape issues
    )
    
    return model, input_shape

def create_simple_data(input_shape):
    """Create simple synthetic data"""
    print("Creating synthetic data...")
    
    num_samples = 500
    X_train = np.random.rand(num_samples, *input_shape).astype(np.float32)
    y_train = np.random.randint(0, 5, num_samples)
    
    # Create validation data
    X_val = np.random.rand(100, *input_shape).astype(np.float32)
    y_val = np.random.randint(0, 5, 100)
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Validation data shape: {X_val.shape}")
    
    return X_train, y_train, X_val, y_val

def main():
    """Main training function"""
    # Create simple model and data
    model, input_shape = create_simple_model()
    X_train, y_train, X_val, y_val = create_simple_data(input_shape)
    
    # Train for just a few epochs
    print("Training model (5 epochs)...")
    history = model.fit(
        X_train, y_train,
        epochs=5,
        batch_size=32,
        validation_data=(X_val, y_val),
        verbose=1
    )
    
    # Save models
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = f"models/underwater_model_{timestamp}.h5"
    best_model_path = "models/best_model.h5"
    
    model.save(model_path)
    model.save(best_model_path)
    
    print(f"\n✅ Training completed successfully!")
    print(f"📍 Model saved to: {model_path}")
    print(f"📍 Best model saved to: {best_model_path}")
    print(f"📊 Final accuracy: {history.history['accuracy'][-1]:.3f}")
    print(f"📊 Validation accuracy: {history.history['val_accuracy'][-1]:.3f}")
    
    # Show model summary
    print("\nModel architecture:")
    model.summary()

if __name__ == "__main__":
    main()