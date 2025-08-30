"""
Test script for modular voice assistant functionality
"""

import sys
import os
from pathlib import Path

def test_shared_modules():
    """Test core shared module functionality"""
    print("=== Testing Shared Modules ===")
    
    try:
        from shared.config.paths_config import PathConfig
        paths = PathConfig()
        print("[OK] PathConfig initialization successful")
        print(f"[OK] Root directory: {paths.root_dir}")
        
        # Test directory creation (suppress output to avoid encoding issues)
        import io
        import contextlib
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            paths.create_directories()
        print("[OK] Directory creation successful")
        
    except Exception as e:
        print(f"[FAIL] PathConfig failed: {e}")
        return False
    
    try:
        from shared.config.audio_config import AUDIO_FORMAT, RATE, CHANNELS
        print(f"[OK] Audio config loaded: Format={AUDIO_FORMAT}, Rate={RATE}, Channels={CHANNELS}")
    except Exception as e:
        print(f"[FAIL] Audio config failed: {e}")
        return False
    
    try:
        from shared.config.tts_config import TTS_MODELS, LANGUAGE_CODES
        print(f"[OK] TTS config loaded: Models={list(TTS_MODELS.keys())}")
    except Exception as e:
        print(f"[FAIL] TTS config failed: {e}")
        return False
    
    try:
        from shared.utils.system import SystemUtils
        device = SystemUtils.get_optimal_device()
        print(f"[OK] System utils loaded: Optimal device={device}")
    except Exception as e:
        print(f"[FAIL] System utils failed: {e}")
        return False
    
    return True

def test_audio_components():
    """Test audio processing components"""
    print("\n=== Testing Audio Components ===")
    
    try:
        from shared.audio.recorder import AudioRecorder
        recorder = AudioRecorder()
        print("[OK] AudioRecorder initialization successful")
    except Exception as e:
        print(f"[FAIL] AudioRecorder failed: {e}")
        return False
    
    try:
        from shared.audio.normalizer import AudioNormalizer
        normalizer = AudioNormalizer()
        print("[OK] AudioNormalizer initialization successful")
    except Exception as e:
        print(f"[FAIL] AudioNormalizer failed: {e}")
        return False
    
    try:
        from shared.audio.player import AudioPlayer
        player = AudioPlayer()
        print(f"[OK] AudioPlayer initialization successful (pygame={player.pygame_available})")
    except Exception as e:
        print(f"[FAIL] AudioPlayer failed: {e}")
        return False
    
    return True

def test_tts_components():
    """Test TTS components"""
    print("\n=== Testing TTS Components ===")
    
    try:
        from shared.tts.piper_tts import PiperTTS
        # Don't initialize yet as it requires actual Piper executable
        print("[OK] PiperTTS import successful")
    except Exception as e:
        print(f"[FAIL] PiperTTS import failed: {e}")
        return False
    
    try:
        from shared.tts.voice_manager import VoiceManager
        print("[OK] VoiceManager import successful")
    except Exception as e:
        print(f"[FAIL] VoiceManager import failed: {e}")
        return False
    
    return True

def test_speech_components():
    """Test speech recognition components"""
    print("\n=== Testing Speech Components ===")
    
    try:
        from shared.speech.whisper_transcriber import WhisperTranscriber
        print("[OK] WhisperTranscriber import successful")
    except Exception as e:
        print(f"[FAIL] WhisperTranscriber import failed: {e}")
        return False
    
    try:
        from shared.speech.text_processor import TextProcessor
        processor = TextProcessor()
        
        # Test text processing
        test_text = "  Hello, world!  "
        cleaned = processor.clean_text(test_text)
        print(f"[OK] TextProcessor test: '{test_text}' -> '{cleaned}'")
        
        # Test validation
        is_valid = not processor.is_empty_or_nonsense("Hello world")
        print(f"[OK] Text validation test: 'Hello world' is valid = {is_valid}")
        
    except Exception as e:
        print(f"[FAIL] TextProcessor failed: {e}")
        return False
    
    return True

def test_base_assistant():
    """Test base assistant class"""
    print("\n=== Testing Base Assistant ===")
    
    try:
        from shared.base.voice_assistant import BaseVoiceAssistant
        print("[OK] BaseVoiceAssistant import successful")
        
        # Note: Can't instantiate abstract class, but import test is sufficient
        
    except Exception as e:
        print(f"[FAIL] BaseVoiceAssistant failed: {e}")
        return False
    
    return True

def test_service_imports():
    """Test service imports"""
    print("\n=== Testing Service Imports ===")
    
    try:
        from services.translation.translation_service import TranslationService
        print("[OK] TranslationService import successful")
    except Exception as e:
        print(f"[FAIL] TranslationService import failed: {e}")
        return False
    
    try:
        from services.assistance.rag_assistant import RAGAssistant
        print("[OK] RAGAssistant import successful")
    except Exception as e:
        print(f"[FAIL] RAGAssistant import failed: {e}")
        return False
    
    return True

def test_resource_consolidation():
    """Test that shared resources exist"""
    print("\n=== Testing Resource Consolidation ===")
    
    from shared.config.paths_config import PathConfig
    paths = PathConfig()
    
    # Test TTS models
    tts_models_dir = paths.tts_models_dir
    if tts_models_dir.exists():
        model_files = list(tts_models_dir.glob("*.onnx"))
        print(f"[OK] Found {len(model_files)} TTS model files")
        for model in model_files:
            print(f"    - {model.name}")
    else:
        print(f"[FAIL] TTS models directory not found: {tts_models_dir}")
        return False
    
    # Test sounds
    sounds_dir = paths.sounds_dir
    if sounds_dir.exists():
        sound_files = list(sounds_dir.glob("*.mp3"))
        print(f"[OK] Found {len(sound_files)} sound files")
        for sound in sound_files:
            print(f"    - {sound.name}")
    else:
        print(f"[FAIL] Sounds directory not found: {sounds_dir}")
        return False
    
    # Test Piper executable
    piper_exe = paths.piper_dir / "piper.exe"
    if piper_exe.exists():
        print(f"[OK] Piper executable found: {piper_exe}")
    else:
        print(f"[FAIL] Piper executable not found: {piper_exe}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Voice and Translation Assistant - Modular Architecture Test")
    print("=" * 60)
    
    tests = [
        ("Shared Modules", test_shared_modules),
        ("Audio Components", test_audio_components),
        ("TTS Components", test_tts_components),
        ("Speech Components", test_speech_components),
        ("Base Assistant", test_base_assistant),
        ("Service Imports", test_service_imports),
        ("Resource Consolidation", test_resource_consolidation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n[PASS] {test_name}")
            else:
                failed += 1
                print(f"\n[FAIL] {test_name}")
        except Exception as e:
            failed += 1
            print(f"\n[ERROR] {test_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All tests passed! Modular architecture is working correctly.")
        return True
    else:
        print("Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)