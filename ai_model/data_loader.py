# ai_model/data_loader.py
import os
import numpy as np
import librosa
import tensorflow as tf
from sklearn.model_selection import train_test_split

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
    
    def load_dataset(self, data_dir, annotations=None, test_size=0.2, val_size=0.1):
        """Load and preprocess entire dataset"""
        features = []
        labels = []
        file_paths = []
        
        # Walk through data directory
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.wav'):
                    file_path = os.path.join(root, file)
                    file_features = self.extract_features(file_path)
                    
                    if file_features is not None:
                        # Determine label from directory structure or annotations
                        label = self._get_label_from_path(file_path, annotations)
                        if label is not None:
                            features.extend(file_features)
                            labels.extend([label] * len(file_features))
                            file_paths.extend([file_path] * len(file_features))
        
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
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test), file_paths
    
    def _get_label_from_path(self, file_path, annotations):
        """Extract label from file path or annotations"""
        # Default mapping based on directory names
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
            return None