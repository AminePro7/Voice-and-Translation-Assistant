#!/usr/bin/env python3
"""
Simple test script for Faster Whisper models - tests a few files to avoid memory issues
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.speech.whisper_transcriber import WhisperTranscriber

def test_single_model(model_size, test_files):
    """Test a single model on selected files"""
    print(f"\n{'='*60}")
    print(f"Testing Whisper {model_size.upper()} model")
    print(f"{'='*60}")

    try:
        # Initialize transcriber
        transcriber = WhisperTranscriber(model_size=model_size)
        results = []

        for audio_file in test_files:
            audio_path = f"test Faster Whisper/sounds/{audio_file}"
            if not os.path.exists(audio_path):
                print(f"File not found: {audio_path}")
                continue

            print(f"\nProcessing: {audio_file}")
            print("-" * 40)

            try:
                start_time = time.time()
                result = transcriber.transcribe_with_info(audio_path, language="fr")
                end_time = time.time()

                processing_time = end_time - start_time

                print(f"Transcription: {result['text']}")
                print(f"Language: {result['language']} (confidence: {result['language_probability']:.3f})")
                print(f"Processing time: {processing_time:.2f}s")

                results.append({
                    'file': audio_file,
                    'text': result['text'],
                    'language': result['language'],
                    'confidence': result['language_probability'],
                    'processing_time': processing_time,
                    'model': model_size
                })

            except Exception as e:
                print(f"Error processing {audio_file}: {e}")
                results.append({
                    'file': audio_file,
                    'error': str(e),
                    'model': model_size
                })

        return results

    except Exception as e:
        print(f"Failed to initialize {model_size} model: {e}")
        return []

def main():
    # Test with a subset of files first
    test_files = [
        "test1.mp3",   # Catégorie 1: Questions Techniques
        "test4.mp3",   # Catégorie 2: Chiffres/Nombres
        "test8.mp3",   # Catégorie 3: Simples/Conversationnelles
        "test11.mp3"   # Catégorie 4: Cas Spécifiques
    ]

    print("Faster Whisper Model Test (Subset)")
    print("Testing files from each category:")
    print("- test1.mp3: Questions Techniques")
    print("- test4.mp3: Phrases avec Chiffres/Nombres")
    print("- test8.mp3: Phrases Simples/Conversationnelles")
    print("- test11.mp3: Cas Spécifiques/Pièges")

    # Test models one at a time
    models = ["small", "medium"]
    all_results = {}

    for model in models:
        all_results[model] = test_single_model(model, test_files)

        # Force cleanup between models
        import gc
        gc.collect()

    # Compare results
    print(f"\n{'='*80}")
    print("COMPARISON RESULTS")
    print(f"{'='*80}")

    for test_file in test_files:
        print(f"\n{test_file}:")
        print("-" * len(test_file))

        for model in models:
            result = next((r for r in all_results[model] if r['file'] == test_file), None)
            if result:
                if 'text' in result:
                    print(f"  {model.upper()}: {result['text']}")
                    print(f"    Time: {result['processing_time']:.2f}s | Confidence: {result['confidence']:.3f}")
                else:
                    print(f"  {model.upper()}: ERROR - {result.get('error', 'Unknown error')}")

    # Performance summary
    print(f"\n{'='*80}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*80}")

    for model in models:
        successful = [r for r in all_results[model] if 'processing_time' in r]
        if successful:
            avg_time = sum(r['processing_time'] for r in successful) / len(successful)
            avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
            print(f"\n{model.upper()} Model:")
            print(f"  Average processing time: {avg_time:.2f}s")
            print(f"  Average confidence: {avg_confidence:.3f}")
            print(f"  Success rate: {len(successful)}/{len(test_files)}")

if __name__ == "__main__":
    main()