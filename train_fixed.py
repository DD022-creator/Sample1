# train_fixed.py
import os
import numpy as np
import tensorflow as tf
from datetime import datetime
import librosa

print("=== UNDERWATER SOUND MODEL TRAINING ===")

# Create directories
os.makedirs('models', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

def create_synthetic_dataset():
    """Create synthetic training data if no real dataset exists"""
    print("Creating synthetic training dataset...")
    
    sample_rate = 22050
    segment_duration = 2.0
    segment_samples = int(sample_rate * segment_duration)
    n_mels = 128
    n_fft = 2048
    hop_length = 512
    
    # Calculate feature shape
    n_frames = int(segment_duration * sample_rate / hop_length) + 1
    input_shape = (n_mels, n_frames, 1)
    
    # Create synthetic data for 4 classes + background
    X_train, y_train = [], []
    
    for class_id in range(5):  # 0-4 (0=background, 1-4=actual classes)
        num_samples = 100 if class_id == 0 else 200  # More samples for actual classes
        
        for i in range(num_samples):
            # Create synthetic audio segment
            if class_id == 0:  # Background noise
                audio = 0.1 * np.random.normal(0, 1, segment_samples)
            elif class_id == 1:  # Vessel (low frequency)
                t = np.linspace(0, segment_duration, segment_samples)
                audio = 0.7 * np.sin(2 * np.pi * 100 * t) + 0.3 * np.sin(2 * np.pi * 200 * t)
                audio += 0.1 * np.random.normal(0, 1, segment_samples)
            elif class_id == 2:  # Marine animal (high frequency)
                t = np.linspace(0, segment_duration, segment_samples)
                audio = 0.6 * np.sin(2 * np.pi * 8000 * t) + 0.2 * np.sin(2 * np.pi * 12000 * t)
                audio += 0.1 * np.random.normal(0, 1, segment_samples)
            elif class_id == 3:  # Natural sound (very low frequency)
                t = np.linspace(0, segment_duration, segment_samples)
                audio = 0.5 * np.sin(2 * np.pi * 0.5 * t) + 0.3 * np.sin(2 * np.pi * 2 * t)
                audio += 0.1 * np.random.normal(0, 1, segment_samples)
            else:  # Other anthropogenic (medium frequency)
                t = np.linspace(0, segment_duration, segment_samples)
                audio = 0.8 * np.sin(2 * np.pi * 300 * t) + 0.4 * np.sin(2 * np.pi * 600 * t)
                audio += 0.1 * np.random.normal(0, 1, segment_samples)
            
            # Normalize
            audio = audio / np.max(np.abs(audio))
            
            # Create mel-spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=audio, sr=sample_rate, n_fft=n_fft,
                hop_length=hop_length, n_mels=n_mels
            )
            log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
            log_mel_spec = log_mel_spec.reshape(n_mels, n_frames, 1)
            
            X_train.append(log_mel_spec)
            y_train.append(class_id)
    
    return np.array(X_train), np.array(y_train), input_shape

def create_and_train_model():
    """Create and train the model"""
    print("Creating and training model...")
    
    # Create synthetic data
    X_train, y_train, input_shape = create_synthetic_dataset()
    num_classes = 5
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Labels shape: {y_train.shape}")
    print(f"Number of classes: {num_classes}")
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
    )
    
    # Create model
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Dropout(0.3),
        
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Dropout(0.3),
        
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Dropout(0.3),
        
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )
    
    # Train model
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=15,
        batch_size=32,
        validation_data=(X_val, y_val),
        verbose=1
    )
    
    return model, history

def main():
    """Main training function"""
    # Train model
    model, history = create_and_train_model()
    
    # Save model
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