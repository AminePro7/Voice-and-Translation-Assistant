"""
Test script for real-time transcription features
"""

import sys
from pathlib import Path

# Add shared modules to path
sys.path.append('.')

def test_realtime_recorder():
    """Test the real-time recorder with silence detection"""
    print("=== Testing Real-Time Audio Recording ===\n")
    
    try:
        from shared.audio.realtime_recorder import RealTimeRecorder
        
        recorder = RealTimeRecorder(
            silence_threshold=0.005,  # Much more sensitive
            silence_duration=2.0,
            min_recording_time=0.5
        )
        
        print("Real-time recorder initialized")
        print("- Silence threshold: 0.005 (HIGH SENSITIVITY for normal speech)")
        print("- Silence duration: 2.0s")
        print("- Minimum recording: 0.5s")
        
        # Test recording with visual feedback
        def volume_callback(volume):
            # Simple volume bar with better sensitivity scaling
            bar_length = 20
            # Scale volume for better visibility of quiet speech
            scaled_volume = min(volume * 50, 1.0)  # Scale up quiet volumes
            filled = int(scaled_volume * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            status = "🗣️ " if volume > 0.005 else "🤫"  # Use same threshold as recorder
            print(f"\r{status} [{bar}] {volume:.4f}", end="", flush=True)
        
        def speech_callback(event):
            if event == "listening":
                print("\n🎧 Waiting for speech...")
            elif event == "recording":
                print("\n🔴 Recording speech...")
            elif event == "stopped":
                print("\n✅ Recording stopped")
        
        print("\n" + "="*50)
        print("🎤 SPEAK NOW - Recording will stop after 2 seconds of silence")
        print("="*50)
        
        audio_path = recorder.record_with_silence_detection(
            volume_callback=volume_callback,
            speech_callback=speech_callback,
            max_duration=15.0
        )
        
        if audio_path:
            print(f"\n✅ Audio recorded successfully: {audio_path}")
            return True
        else:
            print("\n❌ No audio recorded")
            return False
            
    except Exception as e:
        print(f"❌ Real-time recorder test failed: {e}")
        return False

def test_realtime_transcription():
    """Test the real-time transcription system"""
    print("\n=== Testing Real-Time Transcription ===\n")
    
    try:
        from shared.speech.realtime_transcriber import RealTimeTranscriber
        
        transcriber = RealTimeTranscriber(
            whisper_model="small",
            device=None  # Auto-detect
        )
        
        print("Real-time transcriber initialized")
        model_info = transcriber.get_model_info()
        print(f"- Model: {model_info['model_size']}")
        print(f"- Device: {model_info['device']}")
        
        print("\n" + "="*60)
        print("🎤 SPEAK NOW - Real-time transcription with visual feedback")
        print("Talk naturally, pause for 2 seconds when finished")
        print("="*60)
        
        # Perform transcription with visual feedback
        text = transcriber.transcribe_with_visual_feedback()
        
        if text:
            print(f"\n✅ Transcription successful: '{text}'")
            return True
        else:
            print("\n❌ No transcription result")
            return False
            
    except Exception as e:
        print(f"❌ Real-time transcription test failed: {e}")
        return False

def test_base_assistant_realtime():
    """Test the BaseVoiceAssistant real-time features"""
    print("\n=== Testing BaseVoiceAssistant Real-time Features ===\n")
    
    try:
        # Import a concrete implementation for testing
        from services.translation.translation_service import TranslationService
        
        print("Creating translation service for testing...")
        service = TranslationService(direction='en_to_fr', whisper_model='small')
        
        print("✅ Service initialized")
        
        # Test high sensitivity configuration
        service.set_sensitivity_preset('high')  # Use preset for better detection
        print("✅ High sensitivity configured for normal speech")
        
        print("\n" + "="*60)
        print("🎤 SPEAK ENGLISH - Will be transcribed in real-time")
        print("The service will automatically detect when you stop speaking")
        print("="*60)
        
        # Test real-time transcription
        text = service.transcribe_realtime(language='en', visual_feedback=True)
        
        if text:
            print(f"\n📝 You said: '{text}'")
            
            # Test translation
            translated = service.process_user_input(text)
            print(f"🔄 Translation: '{translated}'")
            
            service.cleanup()
            return True
        else:
            print("\n❌ No speech detected")
            service.cleanup()
            return False
            
    except Exception as e:
        print(f"❌ BaseVoiceAssistant test failed: {e}")
        return False

def main():
    """Run all real-time feature tests"""
    print("Real-Time Voice Transcription Features Test")
    print("=" * 60)
    
    tests = [
        ("Real-time Audio Recording", test_realtime_recorder),
        ("Real-time Transcription", test_realtime_transcription),
        ("BaseVoiceAssistant Real-time", test_base_assistant_realtime)
    ]
    
    print("🔊 IMPORTANT: Make sure your microphone is working!")
    print("Each test will require you to speak into your microphone.\n")
    
    input("Press Enter when ready to start testing...")
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Starting: {test_name}")
        print(f"{'='*60}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ PASSED: {test_name}")
            else:
                failed += 1
                print(f"❌ FAILED: {test_name}")
        except KeyboardInterrupt:
            print(f"\n⚠️  Test interrupted by user: {test_name}")
            break
        except Exception as e:
            failed += 1
            print(f"❌ ERROR in {test_name}: {e}")
        
        if test_name != tests[-1][0]:  # Not the last test
            input("\nPress Enter to continue to next test...")
    
    print(f"\n{'='*60}")
    print("REAL-TIME FEATURES TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All real-time features are working correctly!")
        print("Your voice assistant now supports:")
        print("  • Real-time audio recording")
        print("  • Intelligent silence detection")
        print("  • Live volume monitoring")
        print("  • Automatic speech endpoint detection")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check your microphone and audio settings.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)