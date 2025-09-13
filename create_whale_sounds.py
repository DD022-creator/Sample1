# create_whale_sounds.py
import os
import numpy as np
import wave
import librosa

print("=== CREATING SYNTHETIC HUMPBACK WHALE SOUNDS ===")

def create_humpback_whale_sounds():
    """Create realistic synthetic humpback whale sounds"""
    os.makedirs('data/synthetic_whales', exist_ok=True)
    sample_rate = 22050
    
    # Humpback whale vocalizations characteristics
    whale_sounds = [
        # Moans (low frequency, long duration)
        {'type': 'moan', 'freq_range': (100, 300), 'duration': 3.0, 'count': 10},
        # Songs (complex patterns)
        {'type': 'song', 'freq_range': (200, 800), 'duration': 5.0, 'count': 8},
        # Clicks (short, high frequency)
        {'type': 'click', 'freq_range': (2000, 6000), 'duration': 0.5, 'count': 15},
        # Grunts (medium frequency)
        {'type': 'grunt', 'freq_range': (400, 1000), 'duration': 1.5, 'count': 12}
    ]
    
    file_count = 0
    
    for sound_type in whale_sounds:
        print(f"Creating {sound_type['count']} {sound_type['type']} sounds...")
        
        for i in range(sound_type['count']):
            duration = sound_type['duration']
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Create different whale sounds
            if sound_type['type'] == 'moan':
                # Low frequency moan with harmonics
                base_freq = np.random.uniform(sound_type['freq_range'][0], sound_type['freq_range'][1])
                audio = 0.7 * np.sin(2 * np.pi * base_freq * t)
                audio += 0.3 * np.sin(2 * np.pi * base_freq * 2 * t)  # harmonic
                audio += 0.1 * np.sin(2 * np.pi * base_freq * 3 * t)  # harmonic
                
            elif sound_type['type'] == 'song':
                # Complex song with frequency modulation
                base_freq = np.random.uniform(sound_type['freq_range'][0], sound_type['freq_range'][1])
                freq_mod = 0.5 * np.sin(2 * np.pi * 2 * t)  # Frequency modulation
                audio = 0.6 * np.sin(2 * np.pi * (base_freq + 50 * freq_mod) * t)
                
            elif sound_type['type'] == 'click':
                # Short click sounds
                audio = np.zeros_like(t)
                click_pos = int(len(t) * 0.3)  # Click at 30% of duration
                click_duration = int(0.1 * sample_rate)  # 100ms click
                freq = np.random.uniform(sound_type['freq_range'][0], sound_type['freq_range'][1])
                audio[click_pos:click_pos+click_duration] = 0.8 * np.sin(2 * np.pi * freq * t[click_pos:click_pos+click_duration])
                
            elif sound_type['type'] == 'grunt':
                # Medium frequency grunts
                base_freq = np.random.uniform(sound_type['freq_range'][0], sound_type['freq_range'][1])
                audio = 0.5 * np.sin(2 * np.pi * base_freq * t)
                # Add some amplitude modulation
                am_mod = 0.3 * np.sin(2 * np.pi * 5 * t)
                audio *= (1 + am_mod)
            
            # Add ocean background noise
            background_noise = 0.1 * np.random.normal(0, 1, len(t))
            audio += background_noise
            
            # Normalize and convert
            audio = audio / np.max(np.abs(audio))
            audio_int16 = (audio * 32767).astype(np.int16)
            
            # Save file
            filename = f"data/synthetic_whales/humpback_{sound_type['type']}_{i+1:02d}.wav"
            with wave.open(filename, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            file_count += 1
    
    print(f"\n✅ Created {file_count} synthetic humpback whale sounds!")
    print("📍 Location: data/synthetic_whales/")

def create_background_ocean_noise():
    """Create background ocean noise for training"""
    os.makedirs('data/synthetic_background', exist_ok=True)
    sample_rate = 22050
    
    print("Creating ocean background noise...")
    
    for i in range(20):  # Create 20 background files
        duration = np.random.uniform(4.0, 8.0)
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create ocean-like noise (low frequency rumble + some waves)
        audio = 0.05 * np.random.normal(0, 1, len(t))  # Basic noise
        
        # Add some wave-like low frequency content
        wave_freq = np.random.uniform(0.1, 0.5)
        audio += 0.03 * np.sin(2 * np.pi * wave_freq * t)
        
        # Add some medium frequency content
        mid_freq = np.random.uniform(200, 800)
        audio += 0.01 * np.sin(2 * np.pi * mid_freq * t)
        
        # Normalize and convert
        audio = audio / np.max(np.abs(audio))
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Save file
        filename = f"data/synthetic_background/ocean_noise_{i+1:02d}.wav"
        with wave.open(filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())
    
    print("✅ Created 20 ocean background noise files!")
    print("📍 Location: data/synthetic_background/")

if __name__ == "__main__":
    create_humpback_whale_sounds()
    create_background_ocean_noise()