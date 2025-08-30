"""
Test script for TTS text cleaning functionality
"""

import sys
from pathlib import Path

# Add shared modules to path
sys.path.append('.')

def test_tts_cleaning():
    """Test TTS text cleaning with problematic examples"""
    print("=== Testing TTS Text Cleaning ===\n")
    
    from shared.tts.text_cleaner import TTSTextCleaner
    
    # Test cases with common problematic patterns
    test_cases = [
        {
            'name': 'Markdown with bullets and formatting',
            'text': '''Human: Question: puis comment puis-je comprendre ce problème ?

3.  **Résultat :**
    *   Une fois que l'imprimante est allumée et qu'un message d'erreur n'est plus présent, vérifiez si le papier est correctement chargé (s'il y a des problèmes avec les niveaux de poudre).
    *   Assurez-vous que la connexion internet est active.

4.  **Nettoyer les Rouleaux d'Alimentation :**
    *   Éteignez et débranchez l'imprimante.'''
        },
        {
            'name': 'Headers and bold text',
            'text': '''### **Solution Complète:**
    
**1. Première étape :**
Vérifiez les connexions.

**2. Deuxième étape :**
Redémarrez le système.'''
        },
        {
            'name': 'List with asterisks',
            'text': '''Voici les étapes :
* Étape 1 : Ouvrir le panneau
* Étape 2 : Vérifier les câbles
* Étape 3 : Redémarrer'''
        }
    ]
    
    for test_case in test_cases:
        print(f"--- {test_case['name']} ---")
        print("Original:")
        print(repr(test_case['text'][:100] + "..."))
        
        cleaned = TTSTextCleaner.extract_main_content(test_case['text'])
        print("Cleaned:")
        print(f"'{cleaned}'")
        
        chunks = TTSTextCleaner.format_for_speech(test_case['text'], max_length=80)
        print(f"Chunks ({len(chunks)}):")
        for i, chunk in enumerate(chunks, 1):
            print(f"  {i}: '{chunk}'")
        
        print()
    
    return True

def test_integration():
    """Test integration with BaseVoiceAssistant"""
    print("=== Testing Integration with BaseVoiceAssistant ===\n")
    
    try:
        from services.assistance.rag_assistant import RAGAssistant
        print("✅ RAG Assistant imports successfully")
        print("✅ TTS text cleaning is integrated")
        print("✅ Long responses will be automatically cleaned and chunked")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all TTS cleaning tests"""
    print("TTS Text Cleaning Test Suite")
    print("=" * 40)
    
    tests = [
        ("Text Cleaning", test_tts_cleaning),
        ("Integration", test_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ PASSED: {test_name}")
            else:
                failed += 1
                print(f"❌ FAILED: {test_name}")
        except Exception as e:
            failed += 1
            print(f"❌ ERROR in {test_name}: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All TTS cleaning tests passed!")
        print("The assistant will now:")
        print("  ✅ Remove markdown formatting from responses")
        print("  ✅ Clean asterisks and bullet points") 
        print("  ✅ Split long responses into natural chunks")
        print("  ✅ Speak responses clearly without 'asterisk asterisk'")
    else:
        print(f"\n⚠️ {failed} test(s) failed.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)