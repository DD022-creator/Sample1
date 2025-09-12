# ai_model/predict.py
import os
import sys
import numpy as np
import librosa
import tensorflow as tf
from datetime import datetime
import json

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

class SoundPredictor:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)
        self.data_loader = UnderwaterDataLoader()
        self.class_names = {
            0: "Background",
            1: "Vessel", 
            2: "Marine Animal",
            3: "Natural Sound",
            4: "Other Anthropogenic"
        }
    
    def predict_audio(self, audio_path, confidence_threshold=0.7):
        """Predict sounds in an audio file"""
        # Extract features
        features = self.data_loader.extract_features(audio_path)
        if features is None:
            return []
        
        # Predict
        predictions = self.model.predict(features, verbose=0)
        
        # Process predictions
        results = []
        for i, pred in enumerate(predictions):
            class_id = np.argmax(pred)
            confidence = pred[class_id]
            
            if confidence > confidence_threshold and class_id != 0:  # Skip background
                start_time = i * self.data_loader.segment_duration
                end_time = start_time + self.data_loader.segment_duration
                
                results.append({
                    'start_time': round(start_time),
                    'end_time': round(end_time),
                    'duration': round(self.data_loader.segment_duration),
                    'category_id': int(class_id),
                    'category_name': self.class_names[class_id],
                    'score': float(confidence)
                })
        
        return results
    
    def predict_directory(self, input_dir, output_file, confidence_threshold=0.7):
        """Predict sounds for all audio files in a directory"""
        all_results = []
        audio_files = []
        
        # Find all WAV files
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.endswith('.wav'):
                    audio_path = os.path.join(root, file)
                    audio_files.append(audio_path)
        
        print(f"Found {len(audio_files)} audio files for prediction")
        
        # Process each file
        for audio_id, audio_path in enumerate(audio_files, 1):
            print(f"Processing {os.path.basename(audio_path)} ({audio_id}/{len(audio_files)})")
            
            detections = self.predict_audio(audio_path, confidence_threshold)
            
            # Add to results
            for detection in detections:
                detection['audio_id'] = audio_id
                detection['file_path'] = audio_path
                detection['file_name'] = os.path.basename(audio_path)
                all_results.append(detection)
        
        # Save results
        self._save_results(all_results, audio_files, output_file)
        return all_results
    
    def _save_results(self, annotations, audio_files, output_file):
        """Save results to JSON file"""
        output_data = {
            "info": {
                "description": "Underwater Sound Detection Results",
                "version": "1.0",
                "generated_on": datetime.now().isoformat(),
                "confidence_threshold": 0.7
            },
            "audios": [
                {
                    "id": i + 1,
                    "file_name": os.path.basename(path),
                    "file_path": path,
                    "duration": self._get_audio_duration(path)
                }
                for i, path in enumerate(audio_files)
            ],
            "categories": [
                {"id": 1, "name": "vessel"},
                {"id": 2, "name": "marine_animal"},
                {"id": 3, "name": "natural_sound"},
                {"id": 4, "name": "other_anthropogenic"}
            ],
            "annotations": annotations
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Results saved to {output_file}")
    
    def _get_audio_duration(self, audio_path):
        """Get duration of audio file"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            return len(y) / sr
        except:
            return 0

def main():
    """Main prediction function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Underwater Sound Prediction')
    parser.add_argument('--input_dir', required=True, help='Input directory with audio files')
    parser.add_argument('--output_file', default='outputs/predictions.json', help='Output JSON file')
    parser.add_argument('--model_path', default='underwater/model/best_model.h5', help='Path to trained model')
    parser.add_argument('--confidence', type=float, default=0.7, help='Confidence threshold')
    
    args = parser.parse_args()
    
    print("Starting prediction...")
    
    # Check if model exists
    if not os.path.exists(args.model_path):
        print(f"Model not found at {args.model_path}")
        print("Please train the model first or provide a valid model path")
        return
    
    predictor = SoundPredictor(args.model_path)
    results = predictor.predict_directory(args.input_dir, args.output_file, args.confidence)
    
    print(f"\nPrediction completed!")
    print(f"Files processed: {len(set(r['audio_id'] for r in results)) if results else 0}")
    print(f"Anomalies detected: {len(results)}")

if __name__ == "__main__":
    main()