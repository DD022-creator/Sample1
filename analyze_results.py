# analyze_results.py
import json
import os
import sys

def analyze_results():
    print('=== COMPLETE DOSITS MODEL RESULTS ===')
    
    files_to_check = [
        ('outputs/complete_dosits_test.json', 'Synthetic DOSITS Test'),
        ('outputs/real_audio_complete_test.json', 'Real Audio Test')
    ]
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f'\n{description}:')
            print(f'  Files processed: {len(data["audios"])}')
            
            # Count total detections (handle missing 'detections' key)
            total_detections = 0
            class_counts = {}
            
            for audio in data['audios']:
                # Check if 'detections' key exists and is a list
                if 'detections' in audio and isinstance(audio['detections'], list):
                    total_detections += len(audio['detections'])
                    
                    # Count detections by class
                    for detection in audio['detections']:
                        if 'class' in detection:
                            class_name = detection['class']
                            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            print(f'  Total detections: {total_detections}')
            
            if class_counts:
                print('  Detections by class:')
                for class_name, count in class_counts.items():
                    print(f'    {class_name}: {count}')
            else:
                print('  No detections found')
                
            # Count files with and without detections
            files_with_detections = sum(1 for audio in data['audios'] if 'detections' in audio and audio['detections'])
            files_without_detections = len(data['audios']) - files_with_detections
            print(f'  Files with detections: {files_with_detections}')
            print(f'  Files without detections: {files_without_detections}')
            
        else:
            print(f'\n{description}: File not found - {file_path}')

if __name__ == "__main__":
    analyze_results()