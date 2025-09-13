# check_json_structure.py
import json

try:
    with open('outputs/test_best_model.json', 'r') as f:
        data = json.load(f)
    
    print('JSON structure analysis:')
    print(f'Total audio entries: {len(data.get("audios", []))}')
    
    # Check first few entries
    print('\nFirst few entries:')
    for i, audio in enumerate(data['audios'][:3]):
        print(f'File {i+1}: {audio.get("filename", "N/A")}')
        print(f'  Keys: {list(audio.keys())}')
        print(f'  Detections: {audio.get("detections", "NONE")}')
        print(f'  Anomalies: {audio.get("anomalies", "NONE")}')
        print()
    
    # Count files with detections vs anomalies
    files_with_detections = sum(1 for audio in data['audios'] if audio.get('detections'))
    files_with_anomalies = sum(1 for audio in data['audios'] if audio.get('anomalies'))
    
    print(f'Files with detections: {files_with_detections}')
    print(f'Files with anomalies: {files_with_anomalies}')
    
    # Show example of anomalies if they exist
    anomalous_files = [audio for audio in data['audios'] if audio.get('anomalies')]
    if anomalous_files:
        print('\nFirst anomaly example:')
        print(anomalous_files[0]['anomalies'])
        
except Exception as e:
    print(f'Error reading JSON file: {e}')
    import traceback
    traceback.print_exc()