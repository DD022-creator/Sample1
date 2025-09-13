# check_annotations.py
import json

with open('outputs/test_best_model.json', 'r') as f:
    data = json.load(f)
    
print('JSON structure:')
print(f'Root keys: {list(data.keys())}')
print(f'Number of audio files: {len(data.get("audios", []))}')
print(f'Number of annotations: {len(data.get("annotations", []))}')
print(f'Number of categories: {len(data.get("categories", []))}')

# Show categories (classes)
if 'categories' in data:
    print('\nCategories (classes):')
    for category in data['categories']:
        print(f'  {category["id"]}: {category["name"]}')

# Show first few annotations (detections)
if 'annotations' in data and data['annotations']:
    print('\nFirst few annotations (detections):')
    for i, ann in enumerate(data['annotations'][:5]):
        print(f'Annotation {i+1}:')
        print(f'  Audio ID: {ann.get("audio_id")}')
        print(f'  Category: {ann.get("category_id")}')
        print(f'  Confidence: {ann.get("score", 0):.3f}')
        print(f'  Time: {ann.get("bbox", [])}')  # bbox might be [start_time, duration]
        print()
else:
    print('\nNo annotations found in JSON')

# Count total detections
if 'annotations' in data:
    print(f'Total detections: {len(data["annotations"])}')

# Check if this matches the 365 anomalies
total_annotations = len(data.get('annotations', []))
print(f'\nTotal annotations: {total_annotations}')

if total_annotations == 365:
    print('This matches the "Anomalies detected: 365" message!')
    print('So "anomalies" = "annotations" = detections')
else:
    print('The count doesn\'t match - there might be another explanation')