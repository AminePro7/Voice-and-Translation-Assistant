"""
Test and configure voice detection sensitivity
"""

import sys
from pathlib import Path

# Add shared modules to path
sys.path.append('.')

def test_sensitivity_levels():
    """Test different sensitivity levels"""
    from shared.audio.realtime_recorder import RealTimeRecorder
    from shared.audio.sensitivity_presets import list_presets, get_sensitivity_config
    
    print("Voice Detection Sensitivity Test")
    print("=" * 40)
    
    # Show available presets
    list_presets()
    
    print("\n" + "=" * 40)
    print("Choose a sensitivity level to test:")
    print("1. very_high - For whispers and very quiet speech")
    print("2. high - For quiet/normal speech (RECOMMENDED)")
    print("3. medium - For normal to loud speech") 
    print("4. low - For loud speech in noisy environments")
    print("5. very_low - For very loud speech")
    print("6. custom - Enter custom values")
    
    choice = input("\nEnter choice (1-6) or preset name: ").strip()
    
    # Map number choices to preset names
    preset_map = {
        '1': 'very_high',
        '2': 'high', 
        '3': 'medium',
        '4': 'low',
        '5': 'very_low'
    }
    
    if choice in preset_map:
        preset_name = preset_map[choice]
        config = get_sensitivity_config(preset_name)
        
        recorder = RealTimeRecorder(
            silence_threshold=config['threshold'],
            silence_duration=config['duration'],
            min_recording_time=config['min_recording']
        )
        
        print(f"\nTesting '{preset_name}' sensitivity:")
        print(f"- {config['description']}")
        print(f"- Threshold: {config['threshold']}")
        print(f"- Silence duration: {config['duration']}s")
        
    elif choice == '6':
        print("\nCustom sensitivity configuration:")
        threshold = float(input("Threshold (0.001-0.1, lower=more sensitive): "))
        duration = float(input("Silence duration in seconds (1.0-5.0): "))
        
        recorder = RealTimeRecorder(
            silence_threshold=threshold,
            silence_duration=duration,
            min_recording_time=0.5
        )
        
        print(f"\nTesting custom sensitivity:")
        print(f"- Threshold: {threshold}")
        print(f"- Silence duration: {duration}s")
        
    else:
        # Try as preset name
        try:
            config = get_sensitivity_config(choice)
            recorder = RealTimeRecorder(
                silence_threshold=config['threshold'],
                silence_duration=config['duration'],
                min_recording_time=config['min_recording']
            )
            print(f"\nTesting '{choice}' sensitivity:")
            print(f"- {config['description']}")
        except ValueError:
            print(f"Unknown preset: {choice}")
            return False
    
    # Test the recorder
    print("\n" + "="*60)
    print("🎤 VOICE DETECTION TEST")
    print("Talk normally at your usual volume level")
    print("The system will show when it detects your voice")
    print("Press Ctrl+C to stop the test")
    print("="*60)
    
    def volume_callback(volume):
        # Create volume bar
        bar_length = 30
        filled = int(volume * bar_length * 100)  # Scale up for better visibility
        bar = "█" * min(filled, bar_length) + "░" * (bar_length - min(filled, bar_length))
        
        # Determine status
        if volume > recorder.silence_threshold:
            status = "🗣️  DETECTED"
            color = ""
        else:
            status = "🤫 SILENCE "
            color = ""
        
        print(f"\r{status} [{bar}] {volume:.6f}", end="", flush=True)
    
    def speech_callback(event):
        if event == "listening":
            print("\n🎧 Listening for your voice...")
        elif event == "recording":
            print("\n🔴 Voice detected - Recording!")
        elif event == "stopped":
            print("\n✅ Recording stopped (silence detected)")
    
    try:
        # Just test the detection, don't actually save audio
        print("Monitoring audio levels... (speak to test detection)")
        print("When you see '🗣️  DETECTED', the system can hear you!")
        
        import time
        import pyaudio
        import numpy as np
        
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=recorder.audio_format,
            channels=recorder.channels,
            rate=recorder.rate,
            input=True,
            frames_per_buffer=recorder.chunk
        )
        
        print("🎧 Listening...")
        
        while True:
            try:
                data = stream.read(recorder.chunk, exception_on_overflow=False)
                volume = recorder._calculate_volume(data)
                volume_callback(volume)
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
            
        stream.stop_stream()
        stream.close()
        pa.terminate()
        
    except Exception as e:
        print(f"\nError during test: {e}")
        return False
    
    print(f"\n\n{'='*60}")
    print("Test completed!")
    
    # Ask if user wants to save this configuration
    save = input("Did this sensitivity level work well? (y/n): ").lower()
    if save == 'y':
        print(f"\n✅ Good! This sensitivity level is now your default.")
        print("Your services will automatically use these settings.")
        return True
    else:
        print("\n🔄 Try running the test again with different settings.")
        return False

def main():
    """Main sensitivity testing function"""
    print("🎤 Voice Detection Sensitivity Configuration Tool")
    print("This tool helps you find the best sensitivity settings for your voice and environment.")
    print("\nMake sure your microphone is working and positioned normally.")
    
    input("\nPress Enter when ready to start...")
    
    try:
        while True:
            success = test_sensitivity_levels()
            if success:
                break
            
            again = input("\nTry another sensitivity level? (y/n): ").lower()
            if again != 'y':
                break
                
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    
    print("\n🎉 Configuration complete!")
    print("You can now run the translation or assistant services with improved voice detection.")

if __name__ == "__main__":
    main()