#!/usr/bin/env python3
"""
Test all audio files with Faster Whisper tiny model
"""

import sys
import os
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.speech.whisper_transcriber import WhisperTranscriber

def categorize_files():
    """Return file categorization"""
    return {
        "Categorie 1: Questions Techniques (Coeur de metier)": ["test1.mp3", "test2.mp3", "test3.mp3"],
        "Categorie 2: Phrases avec des Chiffres et des Nombres": ["test4.mp3", "test5.mp3", "test6.mp3", "test7.mp3"],
        "Categorie 3: Phrases Simples et Conversationnelles": ["test8.mp3", "test9.mp3", "test10.mp3"],
        "Categorie 4: Cas Specifiques et Pieges": ["test11.mp3", "test12.mp3", "test13.mp3"]
    }

def test_all_files():
    """Test all files with tiny model"""
    print("Testing all 13 audio files with Faster Whisper TINY model")
    print("=" * 60)

    try:
        # Initialize transcriber
        transcriber = WhisperTranscriber(model_size="tiny")
        results = []

        audio_dir = "test Faster Whisper/sounds"
        audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])

        for audio_file in audio_files:
            audio_path = os.path.join(audio_dir, audio_file)
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
                    'processing_time': processing_time
                })

            except Exception as e:
                print(f"ERROR: {e}")
                results.append({
                    'file': audio_file,
                    'error': str(e)
                })

        return results

    except Exception as e:
        print(f"Failed to initialize tiny model: {e}")
        return []

def analyze_results(results):
    """Analyze results by category"""
    categories = categorize_files()

    print(f"\n{'='*80}")
    print("DETAILED RESULTS BY CATEGORY")
    print(f"{'='*80}")

    for category, files in categories.items():
        print(f"\n{category}:")
        print("-" * len(category))

        category_results = []
        for file in files:
            result = next((r for r in results if r['file'] == file), None)
            if result:
                category_results.append(result)
                if 'text' in result:
                    print(f"\n  {file}:")
                    print(f"    Text: {result['text']}")
                    print(f"    Time: {result['processing_time']:.2f}s | Confidence: {result['confidence']:.3f}")
                else:
                    print(f"\n  {file}: ERROR - {result.get('error', 'Unknown error')}")

        # Category statistics
        successful = [r for r in category_results if 'processing_time' in r]
        if successful:
            avg_time = sum(r['processing_time'] for r in successful) / len(successful)
            avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
            print(f"\n  Category Stats:")
            print(f"    Success rate: {len(successful)}/{len(files)}")
            print(f"    Avg time: {avg_time:.2f}s")
            print(f"    Avg confidence: {avg_confidence:.3f}")

    # Overall statistics
    successful_all = [r for r in results if 'processing_time' in r]
    if successful_all:
        print(f"\n{'='*80}")
        print("OVERALL STATISTICS")
        print(f"{'='*80}")

        total_time = sum(r['processing_time'] for r in successful_all)
        avg_time = total_time / len(successful_all)
        avg_confidence = sum(r['confidence'] for r in successful_all) / len(successful_all)

        print(f"Total files processed: {len(successful_all)}/13")
        print(f"Total processing time: {total_time:.2f}s")
        print(f"Average processing time: {avg_time:.2f}s")
        print(f"Average confidence: {avg_confidence:.3f}")
        print(f"Fastest transcription: {min(r['processing_time'] for r in successful_all):.2f}s")
        print(f"Slowest transcription: {max(r['processing_time'] for r in successful_all):.2f}s")

def main():
    results = test_all_files()
    if results:
        analyze_results(results)
    else:
        print("No results to analyze")

if __name__ == "__main__":
    main()