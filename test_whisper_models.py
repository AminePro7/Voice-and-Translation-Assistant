#!/usr/bin/env python3
"""
Test script to compare Faster Whisper medium and small models
on test audio files containing different categories of French speech.
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.speech.whisper_transcriber import WhisperTranscriber

def test_model_performance(model_size, audio_files_dir):
    """Test a specific Whisper model on all audio files"""
    print(f"\n{'='*60}")
    print(f"Testing Whisper {model_size.upper()} model")
    print(f"{'='*60}")

    # Initialize transcriber
    transcriber = WhisperTranscriber(model_size=model_size)

    results = []
    audio_files = sorted([f for f in os.listdir(audio_files_dir) if f.endswith('.mp3')])

    for audio_file in audio_files:
        audio_path = os.path.join(audio_files_dir, audio_file)
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
            error_msg = str(e)
            print(f"Error processing {audio_file}: {error_msg}")

            # If memory error, try to continue with remaining files
            if "memory" in error_msg.lower():
                print("Memory allocation error - continuing with next file...")
                import gc
                gc.collect()

            results.append({
                'file': audio_file,
                'error': error_msg,
                'model': model_size
            })

    return results

def categorize_test_files():
    """Categorize test files based on expected content"""
    categories = {
        "Catégorie 1: Questions Techniques": ["test1.mp3", "test2.mp3", "test3.mp3"],
        "Catégorie 2: Phrases avec Chiffres/Nombres": ["test4.mp3", "test5.mp3", "test6.mp3", "test7.mp3"],
        "Catégorie 3: Phrases Simples/Conversationnelles": ["test8.mp3", "test9.mp3", "test10.mp3"],
        "Catégorie 4: Cas Spécifiques/Pièges": ["test11.mp3", "test12.mp3", "test13.mp3"]
    }
    return categories

def main():
    audio_dir = "test Faster Whisper/sounds"

    if not os.path.exists(audio_dir):
        print(f"Error: Audio directory '{audio_dir}' not found!")
        return

    print("Faster Whisper Model Comparison Test")
    print("Testing categories:")
    print("- Catégorie 1: Questions Techniques (Cœur de métier)")
    print("- Catégorie 2: Phrases avec des Chiffres et des Nombres")
    print("- Catégorie 3: Phrases Simples et Conversationnelles")
    print("- Catégorie 4: Cas Spécifiques et Pièges")

    # Test both models (one at a time to save memory)
    models_to_test = ["small", "medium"]
    all_results = {}

    for model in models_to_test:
        try:
            print(f"\nStarting {model} model test...")
            all_results[model] = test_model_performance(model, audio_dir)
            # Force garbage collection to free memory
            import gc
            gc.collect()
        except Exception as e:
            print(f"Failed to test {model} model: {e}")
            all_results[model] = []

    # Print comparison summary
    print(f"\n{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}")

    categories = categorize_test_files()

    for category, files in categories.items():
        print(f"\n{category}:")
        print("-" * len(category))

        for file in files:
            print(f"\n{file}:")
            for model in models_to_test:
                result = next((r for r in all_results[model] if r['file'] == file), None)
                if result and 'text' in result:
                    print(f"  {model.upper()}: {result['text']}")
                    print(f"    Time: {result['processing_time']:.2f}s | Confidence: {result['confidence']:.3f}")
                elif result and 'error' in result:
                    print(f"  {model.upper()}: ERROR - {result['error']}")

    # Performance summary
    print(f"\n{'='*80}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*80}")

    for model in models_to_test:
        successful_results = [r for r in all_results[model] if 'processing_time' in r]
        if successful_results:
            avg_time = sum(r['processing_time'] for r in successful_results) / len(successful_results)
            avg_confidence = sum(r['confidence'] for r in successful_results) / len(successful_results)
            print(f"\n{model.upper()} Model:")
            print(f"  Average processing time: {avg_time:.2f}s")
            print(f"  Average confidence: {avg_confidence:.3f}")
            print(f"  Successful transcriptions: {len(successful_results)}/13")

if __name__ == "__main__":
    main()