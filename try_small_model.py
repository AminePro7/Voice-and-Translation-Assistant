#!/usr/bin/env python3
"""
Try to get small model working with optimized settings
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def try_small_model_optimized():
    """Try small model with optimized settings"""
    print("Attempting to run Faster Whisper SMALL model with optimized settings")
    print("=" * 70)

    try:
        # Import locally to avoid early model loading
        from faster_whisper import WhisperModel

        # Try with more conservative settings
        print("Trying small model with conservative memory settings...")

        model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8",  # Use int8 instead of float32 to save memory
            num_workers=1  # Use single worker
        )

        print("Small model initialized successfully!")

        # Test on one file
        test_file = "test Faster Whisper/sounds/test1.mp3"
        if os.path.exists(test_file):
            print(f"\nTesting on {test_file}...")

            start_time = time.time()
            segments, info = model.transcribe(test_file, language="fr")

            # Get transcription
            text = " ".join([segment.text for segment in segments])
            end_time = time.time()

            print(f"SUCCESS!")
            print(f"Transcription: {text}")
            print(f"Language: {info.language} (confidence: {info.language_probability:.3f})")
            print(f"Processing time: {end_time - start_time:.2f}s")

            return True
        else:
            print(f"Test file not found: {test_file}")
            return False

    except Exception as e:
        print(f"Failed to initialize/use small model: {e}")
        return False

def try_alternative_approach():
    """Try using the transcriber with modified config"""
    print(f"\n{'='*70}")
    print("Trying alternative approach with modified transcriber")
    print("=" * 70)

    try:
        # Modify the config temporarily
        from shared.config import speech_config

        # Backup original setting
        original_compute_type = speech_config.COMPUTE_TYPE_MAPPING.get("cpu", "float32")

        # Try with int8
        speech_config.COMPUTE_TYPE_MAPPING["cpu"] = "int8"

        from shared.speech.whisper_transcriber import WhisperTranscriber

        print("Trying small model with int8 compute type...")
        transcriber = WhisperTranscriber(model_size="small")

        # Test on one file
        test_file = "test Faster Whisper/sounds/test1.mp3"
        if os.path.exists(test_file):
            result = transcriber.transcribe_with_info(test_file, language="fr")
            print(f"SUCCESS!")
            print(f"Transcription: {result['text']}")
            print(f"Language: {result['language']} (confidence: {result['language_probability']:.3f})")

            # Restore original setting
            speech_config.COMPUTE_TYPE_MAPPING["cpu"] = original_compute_type
            return True
        else:
            # Restore original setting
            speech_config.COMPUTE_TYPE_MAPPING["cpu"] = original_compute_type
            return False

    except Exception as e:
        print(f"Alternative approach failed: {e}")
        # Restore original setting
        try:
            speech_config.COMPUTE_TYPE_MAPPING["cpu"] = original_compute_type
        except:
            pass
        return False

def main():
    print("Attempting to run SMALL model with various optimizations")

    # Try direct approach first
    success1 = try_small_model_optimized()

    if not success1:
        # Try alternative approach
        success2 = try_alternative_approach()

        if not success2:
            print(f"\n{'='*70}")
            print("CONCLUSION")
            print("=" * 70)
            print("Small model cannot run on this system due to memory constraints.")
            print("The TINY model works perfectly and provides good transcription quality.")
            print("For production use, consider:")
            print("1. Using the TINY model (fast, low memory)")
            print("2. Adding more RAM to the system")
            print("3. Using a machine with GPU acceleration")
        else:
            print(f"\n{'='*70}")
            print("SUCCESS with alternative approach!")
            print("=" * 70)
    else:
        print(f"\n{'='*70}")
        print("SUCCESS with optimized settings!")
        print("=" * 70)

if __name__ == "__main__":
    main()