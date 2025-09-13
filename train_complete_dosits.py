# train_complete_dosits.py
import os
import numpy as np
import tensorflow as tf
from datetime import datetime
import librosa
from sklearn.model_selection import train_test_split

print("=== TRAINING ON COMPLETE SYNTHETIC DOSITS ===")

def load_complete_dosits_dataset(data_path):
    """Load the complete synthetic DOSITS dataset"""
    features = []
    labels = []
    
    # Class mapping
    class_mapping = {
        'marine_mammals': 2,  # Marine Animal
        'fish': 2,            # Marine Animal
        'natural_sounds': 3,  # Natural Sound
        'anthropogenic': 4,   # Anthropogenic
        'invertebrates': 2,   # Marine Animal
        'background': 0       # Background
    }
    
    print("Loading complete DOSITS dataset...")
    
    for category, class_id in class_mapping.items():
        category_path = os.path.join(data_path, category)
        if os.path.exists(category_path):
            files = [f for f in os.listdir(category_path) if f.endswith('.wav')]
            print(f"  {category}: {len(files)} files")
            
            for file in files:
                file_path = os.path.join(category_path, file)
                try:
                    # Extract features
                    y, sr = librosa.load(file_path, sr=22050)
                    y = librosa.util.normalize(y)
                    
                    mel_spec = librosa.feature.melspectrogram(
                        y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512
                    )
                    log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
                    
                    # Reshape to fixed size
                    log_mel_spec = log_mel_spec.reshape(128, -1, 1)
                    if log_mel_spec.shape[1] > 44:
                        log_mel_spec = log_mel_spec[:, :44, :]
                    elif log_mel_spec.shape[1] < 44:
                        log_mel_spec = np.pad(log_mel_spec, ((0, 0), (0, 44 - log_mel_spec.shape[1]), (0, 0)), 'constant')
                    
                    features.append(log_mel_spec)
                    labels.append(class_id)
                    
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return np.array(features), np.array(labels)

def create_dosits_model():
    """Create model for complete DOSITS classification"""
    input_shape = (128, 44, 1)
    num_classes = 5  # 0-4 classes
    
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
    dosits_path = "data/dosits_synthetic"
    
    if not os.path.exists(dosits_path):
        print("❌ DOSITS dataset not found! Run create_complete_dosits.py first")
        return
    
    # Load dataset
    X, y = load_complete_dosits_dataset(dosits_path)
    
    if len(X) == 0:
        print("❌ No features could be extracted!")
        return
    
    print(f"✅ Loaded {X.shape[0]} samples")
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
    model = create_dosits_model()
    
    print("Training complete DOSITS model...")
    history = model.fit(
        X_train, y_train,
        epochs=15,
        batch_size=32,
        validation_data=(X_val, y_val),
        verbose=1,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint(
                'models/dosits_complete_model.h5', save_best_only=True, monitor='val_loss'
            )
        ]
    )
    
    # Evaluate
    test_loss, test_acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n📊 Test accuracy: {test_acc:.4f}")
    
    # Save final model
    final_model_path = f"models/dosits_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
    model.save(final_model_path)
    
    print(f"\n✅ Complete DOSITS training completed!")
    print(f"📍 Model saved to: {final_model_path}")
    print(f"📍 Best model saved to: models/dosits_complete_model.h5")
    
    # Show class mapping
    print("\n🎯 CLASS MAPPING FOR COMPLETE DOSITS:")
    class_mapping = {
        0: "Background",
        1: "Vessel", 
        2: "Marine Animal (whales, dolphins, fish, invertebrates)",
        3: "Natural Sound (waves, rain, earthquakes)",
        4: "Anthropogenic (ships, sonar, construction)"
    }
    for class_id, description in class_mapping.items():
        print(f"  {class_id}: {description}")

if __name__ == "__main__":
    main()