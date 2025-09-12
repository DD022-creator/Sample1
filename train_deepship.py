# train_deepship.py
import os
import numpy as np
import tensorflow as tf
from datetime import datetime
import librosa
from sklearn.model_selection import train_test_split

print("=== TRAINING ON DEEPSHIP DATASET ===")

def load_deepship_dataset(data_path):
    """Load DeepShip dataset with proper labeling"""
    features = []
    labels = []
    file_count = 0
    
    # Class mapping
    class_mapping = {
        'Cargo': 1,      # Vessel
        'Passenger': 1,  # Vessel  
        'Tanker': 1,     # Vessel
        'Tug': 1         # Vessel
    }
    
    print("Loading DeepShip dataset...")
    
    for class_name, class_id in class_mapping.items():
        class_path = os.path.join(data_path, class_name)
        if os.path.exists(class_path):
            print(f"Loading {class_name} files...")
            
            for file in os.listdir(class_path):
                if file.endswith('.wav'):
                    file_path = os.path.join(class_path, file)
                    try:
                        # Load and process audio
                        y, sr = librosa.load(file_path, sr=22050)
                        y = librosa.util.normalize(y)
                        
                        # Extract features (simplified for now)
                        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512)
                        log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
                        
                        # Reshape and pad/truncate to fixed size
                        log_mel_spec = log_mel_spec.reshape(128, -1, 1)
                        if log_mel_spec.shape[1] > 44:
                            log_mel_spec = log_mel_spec[:, :44, :]
                        elif log_mel_spec.shape[1] < 44:
                            log_mel_spec = np.pad(log_mel_spec, ((0, 0), (0, 44 - log_mel_spec.shape[1]), (0, 0)), 'constant')
                        
                        features.append(log_mel_spec)
                        labels.append(class_id)
                        file_count += 1
                        
                        if file_count % 50 == 0:
                            print(f"Processed {file_count} files...")
                            
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
    
    return np.array(features), np.array(labels)

def create_deepship_model():
    """Create model for DeepShip dataset"""
    input_shape = (128, 44, 1)
    num_classes = 2  # Vessel vs Non-vessel (for DeepShip, all are vessels)
    
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
        metrics=['accuracy']
    )
    
    return model

def main():
    """Main training function"""
    deepship_path = "data/datasets/deepship"
    
    if not os.path.exists(deepship_path):
        print("❌ DeepShip dataset not found!")
        print("Please download from: https://github.com/irfankamboh/DeepShip")
        print("And place in: data/datasets/deepship/")
        return
    
    # Load dataset
    X, y = load_deepship_dataset(deepship_path)
    
    if len(X) == 0:
        print("❌ No files loaded! Check dataset structure.")
        return
    
    print(f"✅ Loaded {len(X)} samples")
    print(f"Class distribution: {np.bincount(y)}")
    
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
    model = create_deepship_model()
    
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=20,
        batch_size=32,
        validation_data=(X_val, y_val),
        verbose=1,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint(
                'models/deepship_best_model.h5', save_best_only=True, monitor='val_loss'
            )
        ]
    )
    
    # Evaluate
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n📊 Test accuracy: {test_acc:.4f}")
    print(f"📊 Test loss: {test_loss:.4f}")
    
    # Save final model
    final_model_path = f"models/deepship_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
    model.save(final_model_path)
    
    print(f"\n✅ DeepShip training completed!")
    print(f"📍 Model saved to: {final_model_path}")
    print(f"📍 Best model saved to: models/deepship_best_model.h5")

if __name__ == "__main__":
    main()