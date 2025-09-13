# train_synthetic_whales.py
import os
import numpy as np
import tensorflow as tf
from datetime import datetime
import librosa
from sklearn.model_selection import train_test_split

print("=== TRAINING ON SYNTHETIC WHALE SOUNDS ===")

def load_synthetic_dataset(whale_path, background_path):
    """Load synthetic whale sounds and background noise"""
    features = []
    labels = []
    
    # Load whale sounds (class 2 - Marine Animal)
    print("Loading whale sounds...")
    whale_files = [os.path.join(whale_path, f) for f in os.listdir(whale_path) if f.endswith('.wav')]
    
    for i, file_path in enumerate(whale_files):
        try:
            y, sr = librosa.load(file_path, sr=22050)
            y = librosa.util.normalize(y)
            
            # Extract mel-spectrogram
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512)
            log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Reshape to fixed size (128, 44, 1)
            log_mel_spec = log_mel_spec.reshape(128, -1, 1)
            if log_mel_spec.shape[1] > 44:
                log_mel_spec = log_mel_spec[:, :44, :]
            elif log_mel_spec.shape[1] < 44:
                log_mel_spec = np.pad(log_mel_spec, ((0, 0), (0, 44 - log_mel_spec.shape[1]), (0, 0)), 'constant')
            
            features.append(log_mel_spec)
            labels.append(2)  # Marine Animal class
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Load background noise (class 0 - Background)
    print("Loading background noise...")
    background_files = [os.path.join(background_path, f) for f in os.listdir(background_path) if f.endswith('.wav')]
    
    for i, file_path in enumerate(background_files):
        try:
            y, sr = librosa.load(file_path, sr=22050)
            y = librosa.util.normalize(y)
            
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512)
            log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
            
            log_mel_spec = log_mel_spec.reshape(128, -1, 1)
            if log_mel_spec.shape[1] > 44:
                log_mel_spec = log_mel_spec[:, :44, :]
            elif log_mel_spec.shape[1] < 44:
                log_mel_spec = np.pad(log_mel_spec, ((0, 0), (0, 44 - log_mel_spec.shape[1]), (0, 0)), 'constant')
            
            features.append(log_mel_spec)
            labels.append(0)  # Background class
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return np.array(features), np.array(labels)

def create_whale_detection_model():
    """Create model for whale sound detection"""
    input_shape = (128, 44, 1)
    num_classes = 3  # Background, Marine Animal, Other
    
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Dropout(0.3),
        
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Dropout(0.3),
        
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def main():
    """Main training function"""
    whale_path = "data/synthetic_whales"
    background_path = "data/synthetic_background"
    
    if not os.path.exists(whale_path) or not os.path.exists(background_path):
        print("❌ Synthetic data not found! Run create_whale_sounds.py first")
        return
    
    # Load dataset
    X, y = load_synthetic_dataset(whale_path, background_path)
    
    if len(X) == 0:
        print("❌ No features could be extracted!")
        return
    
    print(f"✅ Loaded {X.shape[0]} samples")
    print(f"Class distribution: Background={sum(y == 0)}, Marine Animal={sum(y == 2)}")
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.1, random_state=42, stratify=y_train
    )
    
    print(f"Train: {X_train.shape[0]} samples")
    print(f"Validation: {X_val.shape[0]} samples")
    print(f"Test: {X_test.shape[0]} samples")
    
    # Create and train model
    model = create_whale_detection_model()
    
    print("Training whale detection model...")
    history = model.fit(
        X_train, y_train,
        epochs=20,
        batch_size=16,
        validation_data=(X_val, y_val),
        verbose=1,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint(
                'models/whale_detector.h5', save_best_only=True, monitor='val_loss'
            )
        ]
    )
    
    # Evaluate
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n📊 Test accuracy: {test_acc:.4f}")
    
    # Save final model
    final_model_path = f"models/whale_detector_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
    model.save(final_model_path)
    
    print(f"\n✅ Whale detection training completed!")
    print(f"📍 Model saved to: {final_model_path}")
    print(f"📍 Best model saved to: models/whale_detector.h5")

if __name__ == "__main__":
    main()