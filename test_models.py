# test_models.py
import json
import subprocess
import os

# List of models to test
models_to_test = [
    ("dosits_model_simple.h5", "test_simple_model.json"),
    ("trained_model_20250912_154213.h5", "test_trained_model.json"),
    ("underwater_model_20250912_145433.h5", "test_underwater_model.json")
]

for model_file, output_file in models_to_test:
    model_path = f"models/{model_file}"
    output_path = f"outputs/{output_file}"
    
    if os.path.exists(model_path):
        print(f"\n=== Testing {model_file} ===")
        
        # Run prediction
        cmd = [
            "python", "ai_model/predict_fixed.py",
            "--input_dir", "data/dosits_synthetic",
            "--output_file", output_path,
            "--model_path", model_path,
            "--confidence", "0.1"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Command output: {result.stdout}")
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        # Check results
        if os.path.exists(output_path):
            try:
                with open(output_path, 'r') as f:
                    data = json.load(f)
                annotations = len(data.get("annotations", []))
                print(f"Detections found: {annotations}")
                
                if 'categories' in data:
                    categories = [f'{c["id"]}:{c["name"]}' for c in data['categories']]
                    print(f"Categories: {categories}")
                
                # Count detections by class if any
                if annotations > 0:
                    class_counts = {}
                    for ann in data.get("annotations", []):
                        class_id = ann.get("category_id")
                        class_counts[class_id] = class_counts.get(class_id, 0) + 1
                    print(f"Detections by class: {class_counts}")
                    
            except Exception as e:
                print(f"Error reading results: {e}")
        else:
            print("Output file not created")
    else:
        print(f"Model not found: {model_file}")