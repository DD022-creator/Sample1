# check_prediction_script.py
import re

try:
    with open('ai_model/predict_fixed.py', 'r') as f:
        content = f.read()
    
    print('Looking for class-related code in predict_fixed.py:')
    
    # Look for class definitions
    class_patterns = [
        r'class_[a-z_]*\s*=\s*\[[^\]]*\]',
        r'CLASSES\s*=\s*\[[^\]]*\]', 
        r'class_names\s*=\s*\[[^\]]*\]'
    ]
    
    for pattern in class_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches[:3]:
            print(f'  Found: {match}')
    
    # Look for class filtering
    print('\nLooking for class filtering logic:')
    filter_lines = []
    for line in content.split('\n'):
        if any(keyword in line.lower() for keyword in ['class', 'detection']) and any(op in line for op in ['==', '!=', 'in', 'not in']):
            filter_lines.append(line.strip())
    
    for line in filter_lines[:5]:
        print(f'  {line}')
            
    # Look for confidence threshold usage
    print('\nLooking for confidence threshold logic:')
    conf_matches = re.findall(r'confidence.*[><=].*\d\.\d', content)
    for match in conf_matches[:5]:
        print(f'  Found: {match}')
        
except Exception as e:
    print(f'Error reading prediction script: {e}')
    import traceback
    traceback.print_exc()