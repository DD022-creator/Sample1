# ai_model/train_model.py
import os
import sys
import numpy as np
import tensorflow as tf
from datetime import datetime
from sklearn.model_selection import train_test_split
import librosa

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_cnn_model(input_shape, num_classes):
    """Create CNN model for underwater sound classification"""
    model = tf.keras.Sequential([
        # First conv block
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Dropout(0.3),
        
        # Second conv block
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Dropout(0.3),
        
        # Third conv block
        tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Dropout(0.3),
        
        # Classifier
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

def compile_model(model, learning_rate=0.001):
    """Compile the model with appropriate settings"""
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy', 'precision', 'recall']
    )
    return model

class UnderwaterDataLoader:
    def __init__(self, sample_rate=22050, segment_duration=2.0, n_mels=128):
        self.sample_rate = sample_rate
        self.segment_duration = segment_duration
        self.segment_samples = int(sample_rate * segment_duration)
        self.n_mels = n_mels
        self.hop_length = 512
        self.n_fft = 2048
        
    def extract_features(self, audio_path):
        """Extract mel-spectrogram features from audio file"""
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            y = librosa.util.normalize(y)
            
            # Process in segments
            features = []
            for start_idx in range(0, len(y), self.segment_samples):
                end_idx = min(start_idx + self.segment_samples, len(y))
                segment = y[start_idx:end_idx]
                
                if len(segment) < self.segment_samples:
                    segment = np.pad(segment, (0, self.segment_samples - len(segment)), 'constant')
                
                # Extract mel-spectrogram
                mel_spec = librosa.feature.melspectrogram(
                    y=segment, sr=sr, n_fft=self.n_fft,
                    hop_length=self.hop_length, n_mels=self.n_mels
                )
                log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
                
                # Reshape for CNN (add channel dimension)
                log_mel_spec = log_mel_spec.reshape(log_mel_spec.shape[0], log_mel_spec.shape[1], 1)
                features.append(log_mel_spec)
                
            return np.array(features)
            
        except Exception as e:
            print(f"Error processing {audio_path}: {e}")
            return None
    
    def load_dataset(self, data_dir, test_size=0.2, val_size=0.1):
        """Load and preprocess entire dataset"""
        features = []
        labels = []
        
        # Walk through data directory
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.wav'):
                    file_path = os.path.join(root, file)
                    file_features = self.extract_features(file_path)
                    
                    if file_features is not None:
                        # Determine label from directory structure
                        label = self._get_label_from_path(file_path)
                        if label is not None:
                            features.extend(file_features)
                            labels.extend([label] * len(file_features))
        
        features = np.array(features)
        labels = np.array(labels)
        
        # Split dataset
        X_temp, X_test, y_temp, y_test = train_test_split(
            features, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        val_size_adjusted = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size_adjusted, random_state=42, stratify=y_temp
        )
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test)
    
    def _get_label_from_path(self, file_path):
        """Extract label from file path"""
        path = file_path.lower()
        if 'cargo' in path or 'tanker' in path or 'passenger' in path or 'vessel' in path:
            return 1  # Vessel
        elif 'marine' in path or 'whale' in path or 'dolphin' in path or 'fish' in path:
            return 2  # Marine Animal
        elif 'natural' in path or 'wave' in path or 'rain' in path:
            return 3  # Natural Sound
        elif 'anthropogenic' in path or 'sonar' in path or 'engine' in path:
            return 4  # Other Anthropogenic
        else:
            return 0  # Background/Unknown

class ModelTrainer:
    def __init__(self, input_shape=(128, 87, 1), num_classes=5):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.history = None
        
    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32, learning_rate=0.001):
        """Train the model"""
        # Create and compile model
        self.model = create_cnn_model(self.input_shape, self.num_classes)
        self.model = compile_model(self.model, learning_rate)
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3),
            tf.keras.callbacks.ModelCheckpoint(
                'models/best_model.h5', save_best_only=True, monitor='val_loss'
            )
        ]
        
        # Train model
        self.history = self.model.fit(
            X_train, y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=1
        )
        
        return self.history
    
    def save_model(self, model_path):
        """Save trained model"""
        if self.model:
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            self.model.save(model_path)
            print(f"Model saved to {model_path}")
    
    def evaluate(self, X_test, y_test):
        """Evaluate model on test set"""
        if self.model:
            results = self.model.evaluate(X_test, y_test, verbose=0)
            metrics = {
                'loss': results[0],
                'accuracy': results[1],
                'precision': results[2],
                'recall': results[3]
            }
            return metrics

def main():
    """Main training function"""
    print("Starting model training...")
    
    # Initialize data loader
    data_loader = UnderwaterDataLoader()
    
    # Load dataset (replace with your dataset path)
    dataset_path = "underwater\data\datasets"
    print(f"Loading dataset from: {dataset_path}")
    
    try:
        (X_train, y_train), (X_val, y_val), (X_test, y_test) = data_loader.load_dataset(dataset_path)
        
        print(f"Dataset loaded:")
        print(f"Train: {X_train.shape[0]} samples")
        print(f"Validation: {X_val.shape[0]} samples") 
        print(f"Test: {X_test.shape[0]} samples")
        
        # Train model
        trainer = ModelTrainer()
        history = trainer.train(X_train, y_train, X_val, y_val, epochs=30)
        
        # Evaluate model
        metrics = trainer.evaluate(X_test, y_test)
        print("\nModel Evaluation:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")
        
        # Save final model
        final_model_path = f"models/underwater_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.h5"
        trainer.save_model(final_model_path)
        
        print(f"\nTraining completed! Model saved to: {final_model_path}")
        
    except Exception as e:
        print(f"Error during training: {e}")
        print("Creating sample data for testing...")
        create_sample_data()

def create_sample_data():
    """Create sample data if no dataset is found"""
    print("Creating sample training data...")
    os.makedirs("data/sample_train", exist_ok=True)
    
    # Create sample WAV files for training
    sample_rate = 22050
    for i in range(20):
        duration = 3
        t = np.linspace(0, duration, sample_rate * duration)
        
        # Create different types of sounds
        if i < 5:
            audio = 0.7 * np.sin(2 * np.pi * 100 * t)  # Vessel
            label = "vessel"
        elif i < 10:
            audio = 0.6 * np.sin(2 * np.pi * 8000 * t)  # Marine animal
            label = "marine"
        elif i < 15:
            audio = 0.5 * np.sin(2 * np.pi * 0.5 * t)   # Natural sound
            label = "natural"
        else:
            audio = 0.8 * np.sin(2 * np.pi * 300 * t)   # Anthropogenic
            label = "anthropogenic"
        
        audio += 0.1 * np.random.normal(0, 1, len(t))
        audio = audio / np.max(np.abs(audio))
        audio_int16 = (audio * 32767).astype(np.int16)
        
        filename = f"data/sample_train/{label}_{i}.wav"
        with open(filename, 'wb') as f:
            import wave
            with wave.open(filename, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_int16.tobytes())
    
    print("Sample data created at: data/sample_train/")
    print("Run training again to use sample data")

if __name__ == "__main__":
    main()