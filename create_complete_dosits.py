# create_complete_dosits.py
import os
import numpy as np
import wave
import librosa

print("=== CREATING COMPLETE SYNTHETIC DOSITS DATASET ===")

def create_complete_dosits_dataset():
    """Create synthetic sounds for ALL DOSITS categories"""
    
    # DOSITS categories and their sub-types
    categories = {
        'marine_mammals': {
            'subtypes': ['humpback_whale', 'dolphin', 'orca', 'seal'],
            'class_id': 2  # Marine Animal
        },
        'fish': {
            'subtypes': ['grunting_fish', 'clicking_fish', 'drumming_fish'],
            'class_id': 2  # Marine Animal
        },
        'natural_sounds': {
            'subtypes': ['waves', 'rain', 'underwater_earthquake', 'ice_cracking'],
            'class_id': 3  # Natural Sound
        },
        'anthropogenic': {
            'subtypes': ['ship_engine', 'sonar', 'dredging', 'construction'],
            'class_id': 4  # Anthropogenic
        },
        'invertebrates': {
            'subtypes': ['snapping_shrimp', 'urchin', 'crab'],
            'class_id': 2  # Marine Animal
        }
    }
    
    sample_rate = 22050
    files_created = 0
    
    for category, info in categories.items():
        category_path = f"data/dosits_synthetic/{category}"
        os.makedirs(category_path, exist_ok=True)
        
        print(f"\nCreating {category} sounds...")
        
        for subtype in info['subtypes']:
            for i in range(5):  # 5 files per subtype
                duration = np.random.uniform(3.0, 8.0)
                filename = f"{category_path}/{subtype}_{i+1:02d}.wav"
                
                # Create sound based on category and subtype
                audio = create_sound_by_type(category, subtype, duration, sample_rate)
                
                # Save file
                audio_int16 = (audio * 32767).astype(np.int16)
                with wave.open(filename, 'w') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_int16.tobytes())
                
                files_created += 1
                if files_created % 10 == 0:
                    print(f"Created {files_created} files...")
    
    # Create background noise
    background_path = "data/dosits_synthetic/background"
    os.makedirs(background_path, exist_ok=True)
    print("\nCreating background ocean noise...")
    
    for i in range(20):
        duration = np.random.uniform(5.0, 10.0)
        audio = create_background_noise(duration, sample_rate)
        filename = f"{background_path}/ocean_background_{i+1:02d}.wav"
        
        audio_int16 = (audio * 32767).astype(np.int16)
        with wave.open(filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())
        
        files_created += 1
    
    print(f"\n✅ Created {files_created} synthetic DOSITS files!")
    print("📍 Location: data/dosits_synthetic/")

def create_sound_by_type(category, subtype, duration, sample_rate):
    """Create specific sound based on category and subtype"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)
    
    if category == 'marine_mammals':
        if subtype == 'humpback_whale':
            # Low frequency moans with harmonics
            base_freq = np.random.uniform(100, 300)
            audio = 0.7 * np.sin(2 * np.pi * base_freq * t)
            audio += 0.3 * np.sin(2 * np.pi * base_freq * 2 * t)
        elif subtype == 'dolphin':
            # High frequency clicks and whistles
            base_freq = np.random.uniform(8000, 12000)
            audio = 0.6 * np.sin(2 * np.pi * base_freq * t)
            # Add clicks
            for _ in range(5):
                click_pos = np.random.randint(0, len(t))
                click_dur = int(0.02 * sample_rate)
                if click_pos + click_dur < len(audio):
                    audio[click_pos:click_pos+click_dur] += 0.8
        
    elif category == 'fish':
        if 'grunting' in subtype:
            base_freq = np.random.uniform(200, 600)
            audio = 0.5 * np.sin(2 * np.pi * base_freq * t)
        elif 'clicking' in subtype:
            # Random clicks
            for _ in range(8):
                click_pos = np.random.randint(0, len(t))
                click_dur = int(0.01 * sample_rate)
                if click_pos + click_dur < len(audio):
                    audio[click_pos:click_pos+click_dur] += 0.7
        
    elif category == 'natural_sounds':
        if subtype == 'waves':
            # Wave-like sounds
            wave_freq = np.random.uniform(0.1, 0.5)
            audio = 0.4 * np.sin(2 * np.pi * wave_freq * t)
        elif subtype == 'rain':
            # Rain-like noise
            audio = 0.3 * np.random.normal(0, 1, len(t))
        
    elif category == 'anthropogenic':
        if 'ship' in subtype:
            # Engine rumble
            base_freq = np.random.uniform(80, 200)
            audio = 0.8 * np.sin(2 * np.pi * base_freq * t)
        elif 'sonar' in subtype:
            # Sonar pings
            ping_interval = duration / 8
            for ping in range(8):
                ping_time = ping * ping_interval
                ping_pos = int(ping_time * sample_rate)
                ping_dur = int(0.1 * sample_rate)
                if ping_pos + ping_dur < len(audio):
                    freq = np.random.uniform(5000, 10000)
                    audio[ping_pos:ping_pos+ping_dur] += 0.6 * np.sin(2 * np.pi * freq * t[ping_pos:ping_pos+ping_dur])
        
    elif category == 'invertebrates':
        if 'shrimp' in subtype:
            # Snapping shrimp clicks
            for _ in range(15):
                click_pos = np.random.randint(0, len(t))
                click_dur = int(0.005 * sample_rate)
                if click_pos + click_dur < len(audio):
                    audio[click_pos:click_pos+click_dur] += 0.9
    
    # Add background noise
    audio += 0.1 * np.random.normal(0, 1, len(t))
    
    # Normalize
    audio = audio / np.max(np.abs(audio))
    return audio

def create_background_noise(duration, sample_rate):
    """Create ocean background noise"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.1 * np.random.normal(0, 1, len(t))
    
    # Add some low frequency rumble
    low_freq = np.random.uniform(0.5, 2.0)
    audio += 0.05 * np.sin(2 * np.pi * low_freq * t)
    
    # Add some medium frequency content
    mid_freq = np.random.uniform(200, 500)
    audio += 0.02 * np.sin(2 * np.pi * mid_freq * t)
    
    return audio / np.max(np.abs(audio))

if __name__ == "__main__":
    create_complete_dosits_dataset()