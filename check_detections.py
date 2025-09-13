import json

try:
    with open('outputs/test_best_model.json', 'r') as f:
        data = json.load(f)
    
    print(f'Files processed: {len(data["audios"])}')
    total_dets = 0
    for audio in data['audios']:
        total_dets += len(audio.get('detections', []))
    print(f'Total detections with best_model: {total_dets}')
    
    # Show first few detections if any
    if total_dets > 0:
        print('First few detections:')
        count = 0
        for audio in data['audios']:
            if 'detections' in audio and audio['detections']:
                print(f'  {audio["filename"]}: {len(audio["detections"])} detections')
                for det in audio['detections'][:2]:  # Show first 2 detections per file
                    print(f'    - {det["class"]}: {det["confidence"]:.3f}')
                count += 1
                if count >= 3:  # Show only first 3 files with detections
                    break
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()