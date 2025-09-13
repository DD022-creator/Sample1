# train_humpback.py
import os
import numpy as np
import tensorflow as tf
from datetime import datetime
import librosa
from sklearn.model_selection import train_test_split

print("=== TRAINING ON HUMPBACK WHALE SOUNDS ===")

def load_humpback_dataset(data_path):
    """Load humpback whale sounds and create synthetic background noise"""
    features = []
    labels = []
    
    # Load humpback whale sounds (class 2 - Marine Animal)
    humpback_files = []
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.lower().endswith('.wav'):
                humpback_files.append(os.path.join(root, file))
    
    print(f"Found {len(humpback_files)} humpback whale sound files")
    
    # Process humpback sounds
    for i, file_path in enumerate(humpback_files):
        try:
            # Extract features
            y, sr = librosa.load(file_path, sr=22050)
            y = librosa.util.normalize(y)
            
            # Create mel-spectrogram
            mel_spec = librosa.feature.melspectrogram(
                y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512
            )
            log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
            
            # Reshape to fixed size (128, 44, 1)
            log_mel_spec = log_mel_spec.reshape(128, -1, 1)
            if log_mel_spec.shape[1] > 44:
                log_mel_spec = log_mel_spec[:, :44, :]
            elif log_mel_spec.shape[1] < 44:
                log_mel_spec = np.pad(
                    log_mel_spec, 
                    ((0, 0), (0, 44 - log_mel_spec.shape[1]), (0, 0)), 
                    'constant'
                )
            
            features.append(log_mel_spec)
            labels.append(2)  # Marine Animal class
            
            if (i + 1) % 5 == 0:
                print(f"Processed {i + 1}/{len(humpback_files)} humpback files...")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Create synthetic background noise (class 0)
    print("Creating synthetic background noise...")
    num_background = len(humpback_files)  # Same number as humpback files
    for i in range(num_background):
        # Create random noise
        noise = 0.1 * np.random.normal(0, 1, (128, 44, 1))
        features.append(noise)
        labels.append(0)  # Background class
    
    return np.array(features), np.array(labels)

def create_whale_model():
    """Create model optimized for whale sound detection"""
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
        
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Dropout(0.3),
        
        tf.keras.layers.GlobalAveragePooling2D(),
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
    """Main training function for humpback sounds"""
    humpback_path = "data/datasets/dosits"
    
    if not os.path.exists(humpback_path):
        print("❌ Humpback sounds not found!")
        print("Please place humpback whale sounds in: data/datasets/dosits/")
        return
    
    # Load dataset
    X, y = load_humpback_dataset(humpback_path)
    
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
    model = create_whale_model()
    
    print("Training model for whale sound detection...")
    history = model.fit(
        X_train, y_train,
        epochs=15,
        batch_size=16,
        validation_data=(X_val, y_val),
        verbose=1,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint(
                'models/whale_model.h5', save_best_only=True, monitor='val_loss'
            )
        ]
    )
    
    # Evaluate
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n📊 Test accuracy: {test_acc:.4f}")
    
    # Save final model
    final_model_path = f"models/humpback_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
    model.save(final_model_path)
    
    print(f"\n✅ Humpback whale training completed!")
    print(f"📍 Model saved to: {final_model_path}")
    print(f"📍 Best model saved to: models/whale_model.h5")

if __name__ == "__main__":
    main()