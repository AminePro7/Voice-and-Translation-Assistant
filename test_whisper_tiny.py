#!/usr/bin/env python3
"""
Test script for Faster Whisper with tiny model first to verify setup
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.speech.whisper_transcriber import WhisperTranscriber

def test_single_file(model_size, audio_file):
    """Test a single model on one file"""
    print(f"\nTesting {model_size} model on {audio_file}")
    print("-" * 50)

    try:
        # Initialize transcriber
        transcriber = WhisperTranscriber(model_size=model_size)

        audio_path = f"test Faster Whisper/sounds/{audio_file}"
        if not os.path.exists(audio_path):
            print(f"File not found: {audio_path}")
            return None

        start_time = time.time()
        result = transcriber.transcribe_with_info(audio_path, language="fr")
        end_time = time.time()

        processing_time = end_time - start_time

        print(f"SUCCESS!")
        print(f"Transcription: {result['text']}")
        print(f"Language: {result['language']} (confidence: {result['language_probability']:.3f})")
        print(f"Processing time: {processing_time:.2f}s")

        return {
            'file': audio_file,
            'text': result['text'],
            'language': result['language'],
            'confidence': result['language_probability'],
            'processing_time': processing_time,
            'model': model_size
        }

    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    print("Faster Whisper Memory Test")
    print("Testing models starting with tiny to check memory constraints")

    # Start with tiny model on one file
    test_file = "test1.mp3"
    models_to_try = ["tiny", "small", "medium"]

    successful_models = []

    for model in models_to_try:
        print(f"\n{'='*60}")
        print(f"TESTING {model.upper()} MODEL")
        print(f"{'='*60}")

        result = test_single_file(model, test_file)
        if result:
            successful_models.append(result)
            print(f"\n{model.upper()} model works!")
        else:
            print(f"\n{model.upper()} model failed - stopping here")
            break

        # Clean up memory between tests
        import gc
        gc.collect()

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    if successful_models:
        print(f"Working models for {test_file}:")
        for result in successful_models:
            print(f"  {result['model'].upper()}: {result['processing_time']:.2f}s")
            print(f"    \"{result['text']}\"")
    else:
        print("No models worked successfully!")

    # If any model worked, test it on more files
    if successful_models:
        best_model = successful_models[-1]['model']  # Use the largest working model
        print(f"\nTesting {best_model.upper()} model on more files...")

        additional_files = ["test4.mp3", "test8.mp3", "test11.mp3"]
        all_results = [successful_models[-1]]  # Include the first test

        for audio_file in additional_files:
            result = test_single_file(best_model, audio_file)
            if result:
                all_results.append(result)

        # Final summary
        if len(all_results) > 1:
            print(f"\n{'='*60}")
            print(f"FINAL RESULTS - {best_model.upper()} MODEL")
            print(f"{'='*60}")

            categories = {
                "test1.mp3": "Questions Techniques",
                "test4.mp3": "Phrases avec Chiffres/Nombres",
                "test8.mp3": "Phrases Simples/Conversationnelles",
                "test11.mp3": "Cas Spécifiques/Pièges"
            }

            for result in all_results:
                category = categories.get(result['file'], "Unknown")
                print(f"\n{result['file']} ({category}):")
                print(f"  Text: {result['text']}")
                print(f"  Time: {result['processing_time']:.2f}s | Confidence: {result['confidence']:.3f}")

            avg_time = sum(r['processing_time'] for r in all_results) / len(all_results)
            avg_confidence = sum(r['confidence'] for r in all_results) / len(all_results)

            print(f"\nAverage processing time: {avg_time:.2f}s")
            print(f"Average confidence: {avg_confidence:.3f}")
            print(f"Success rate: {len(all_results)}/4 files")

if __name__ == "__main__":
    main()