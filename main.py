import numpy as np
import librosa
import tensorflow as tf
from tensorflow import keras
import json
import os
from datetime import datetime
import argparse

class UnderwaterSoundAnalyzer:
    def __init__(self, model_path=None, confidence_threshold=0.7):
        self.sample_rate = 22050
        self.fft_size = 2048
        self.hop_length = 512
        self.n_mels = 128
        self.segment_duration = 2.0
        self.segment_samples = int(self.sample_rate * self.segment_duration)
        self.confidence_threshold = confidence_threshold
        
        if model_path and os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.model = self.build_model()
    
    def build_model(self):
        input_shape = (self.n_mels, 87, 1)  # Fixed shape for 2-second segments
        model = keras.Sequential([
            keras.layers.Conv2D(16, (3, 3), activation='relu', input_shape=input_shape),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(32, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(5, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def preprocess_audio(self, audio_path):
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            y = librosa.util.normalize(y)
            return y, sr
        except Exception as e:
            print(f'Error loading audio: {e}')
            return None, None
    
    def extract_features(self, audio_segment):
        mel_spec = librosa.feature.melspectrogram(
            y=audio_segment, sr=self.sample_rate,
            n_fft=self.fft_size, hop_length=self.hop_length, n_mels=self.n_mels
        )
        log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
        return log_mel_spec.reshape(log_mel_spec.shape[0], log_mel_spec.shape[1], 1)
    
    def detect_anomalies(self, audio_path):
        y, sr = self.preprocess_audio(audio_path)
        if y is None:
            return []
        
        segments = []
        
        # Process audio in segments
        for start_idx in range(0, len(y), self.segment_samples):
            end_idx = min(start_idx + self.segment_samples, len(y))
            segment = y[start_idx:end_idx]
            
            if len(segment) < self.segment_samples:
                segment = np.pad(segment, (0, self.segment_samples - len(segment)), 'constant')
            
            features = self.extract_features(segment)
            features = np.expand_dims(features, axis=0)
            
            # Predict (using mock predictions for demo)
            prediction = np.array([[0.1, 0.7, 0.1, 0.05, 0.05]])  # Mock: class 1 (vessel) with 70% confidence
            class_id = np.argmax(prediction)
            confidence = prediction[0][class_id]
            
            if confidence > self.confidence_threshold and class_id != 0:
                start_time = start_idx / sr
                end_time = end_idx / sr
                
                segments.append({
                    'start_time': round(start_time),
                    'end_time': round(end_time),
                    'duration': round(end_time - start_time),
                    'category_id': int(class_id),
                    'score': float(confidence)
                })
        
        return segments
    
    def generate_output_json(self, audio_files, output_path):
        output_data = {
            'info': {
                'description': 'Grand Challenge UDA',
                'version': '1.0',
                'year': 2025,
                'generated_on': datetime.now().isoformat()
            },
            'audios': [],
            'categories': [
                {'id': 1, 'name': 'vessel'},
                {'id': 2, 'name': 'marine_animal'},
                {'id': 3, 'name': 'natural_sound'},
                {'id': 4, 'name': 'other_anthropogenic'}
            ],
            'annotations': []
        }
        
        annotation_id = 1
        
        for audio_id, audio_path in enumerate(audio_files, 1):
            y, sr = self.preprocess_audio(audio_path)
            if y is None:
                continue
                
            duration = len(y) / sr
            file_name = os.path.basename(audio_path)
            
            output_data['audios'].append({
                'id': audio_id,
                'file_name': file_name,
                'file_path': audio_path,
                'duration': duration
            })
            
            # Detect anomalies
            segments = self.detect_anomalies(audio_path)
            
            for seg in segments:
                output_data['annotations'].append({
                    'id': annotation_id,
                    'audio_id': audio_id,
                    'category_id': seg['category_id'],
                    'start_time': seg['start_time'],
                    'end_time': seg['end_time'],
                    'duration': seg['duration'],
                    'score': seg['score']
                })
                annotation_id += 1
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        return output_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Underwater Sound Detection')
    parser.add_argument('--input_dir', type=str, required=True, help='Input directory with audio files')
    parser.add_argument('--output_file', type=str, default='results.json', help='Output JSON file')
    parser.add_argument('--model_path', type=str, help='Path to model')
    parser.add_argument('--confidence', type=float, default=0.7, help='Confidence threshold')
    
    args = parser.parse_args()
    
    analyzer = UnderwaterSoundAnalyzer(
        model_path=args.model_path,
        confidence_threshold=args.confidence
    )
    
    audio_files = []
    for file in os.listdir(args.input_dir):
        if file.lower().endswith('.wav'):
            audio_files.append(os.path.join(args.input_dir, file))
    
    if not audio_files:
        print('No WAV files found!')
        exit(1)
    
    print(f'Processing {len(audio_files)} audio files...')
    results = analyzer.generate_output_json(audio_files, args.output_file)
    print(f'Detection complete! Results saved to {args.output_file}')
    print(f'Found {len(results["annotations"])} anomalies')
