# check_categories.py
import json

with open('outputs/test_best_model.json', 'r') as f:
    data = json.load(f)
    
if 'categories' in data:
    print('Categories:')
    for category in data['categories']:
        print(f'  {category["id"]}: {category["name"]}')
        
    # Check if class 1 exists
    class_1 = next((cat for cat in data['categories'] if cat['id'] == 1), None)
    if class_1:
        print(f'\nClass 1 is: {class_1["name"]}')
    else:
        print('\nClass 1 not found in categories')
else:
    print('No categories found in JSON')