import numpy as np
import librosa
import tensorflow as tf
from tensorflow import keras
import os
import json

class DataGenerator(keras.utils.Sequence):
    def __init__(self, data_dir, batch_size=32, sample_rate=22050, segment_duration=2.0):
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.sample_rate = sample_rate
        self.segment_samples = int(sample_rate * segment_duration)
        self.fft_size = 2048
        self.hop_length = 512
        self.n_mels = 128
        
        self.annotations = self.load_annotations()
        self.audio_files = list(self.annotations.keys())
        
    def load_annotations(self):
        return {}
    
    def __len__(self):
        return int(np.ceil(len(self.audio_files) / self.batch_size))
    
    def __getitem__(self, index):
        batch_files = self.audio_files[index*self.batch_size:(index+1)*self.batch_size]
        X = []
        y = []
        
        for file in batch_files:
            audio_path = os.path.join(self.data_dir, file)
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            audio = librosa.util.normalize(audio)
            
            if len(audio) > self.segment_samples:
                start = np.random.randint(0, len(audio) - self.segment_samples)
                segment = audio[start:start+self.segment_samples]
            else:
                segment = np.pad(audio, (0, self.segment_samples - len(audio)), mode='constant')
            
            features = self.extract_features(segment)
            X.append(features)
            
            label = 0
            y.append(label)
        
        return np.array(X), np.array(y)
    
    def extract_features(self, audio_segment):
        mel_spec = librosa.feature.melspectrogram(
            y=audio_segment,
            sr=self.sample_rate,
            n_fft=self.fft_size,
            hop_length=self.hop_length,
            n_mels=self.n_mels
        )
        log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
        return log_mel_spec.reshape(log_mel_spec.shape[0], log_mel_spec.shape[1], 1)

def create_model(input_shape, num_classes):
    model = keras.Sequential([
        keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Dropout(0.25),
        
        keras.layers.Conv2D(64, (3, 3), activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Dropout(0.25),
        
        keras.layers.Conv2D(128, (3, 3), activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.MaxPooling2D((2, 2)),
        keras.layers.Dropout(0.25),
        
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(256, activation='relu'),
        keras.layers.BatchNormalization(),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

if __name__ == "__main__":
    sample_rate = 22050
    segment_duration = 2.0
    n_mels = 128
    hop_length = 512
    fft_size = 2048
    
    n_frames = int(segment_duration * sample_rate / hop_length) + 1
    input_shape = (n_mels, n_frames, 1)
    
    model = create_model(input_shape, num_classes=5)
    
    train_gen = DataGenerator('data/train', batch_size=32)
    val_gen = DataGenerator('data/val', batch_size=32)
    
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=50,
        verbose=1
    )
    
    os.makedirs('model', exist_ok=True)
    model.save('model/underwater_sound_model.h5')
    print("Model training complete and saved as 'model/underwater_sound_model.h5'")