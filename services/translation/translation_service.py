"""
Translation Service using shared voice assistant modules
"""

import sys
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.base.voice_assistant import BaseVoiceAssistant
import random

# Translation engine imports
try:
    import argostranslate.package
    import argostranslate.translate
    ARGOSTRANSLATE_AVAILABLE = True
except ImportError:
    print("ERROR: 'argostranslate' library is missing.")
    print("Install it with: pip install argostranslate")
    ARGOSTRANSLATE_AVAILABLE = False
    sys.exit(1)

class TranslationService(BaseVoiceAssistant):
    """
    Voice translation service that extends BaseVoiceAssistant
    Provides English to French and French to English translation
    """
    
    # Service configuration
    SUPPORTED_DIRECTIONS = {
        'en_to_fr': {
            'input_language': 'en',
            'output_language': 'fr', 
            'assistant_voice': 'en_US',
            'result_voice': 'fr_FR',
            'welcome_msg': "Hello, I am your voice translation assistant. Tell me what you want to translate from English to French.",
            'recording_msg': "Recording... (Speak English now for translation)",
            'direction_display': "English to French"
        },
        'fr_to_en': {
            'input_language': 'fr',
            'output_language': 'en',
            'assistant_voice': 'fr_FR', 
            'result_voice': 'en_US',
            'welcome_msg': "Bonjour, je suis votre assistant de traduction vocal. Dites-moi ce que vous voulez traduire du français vers l'anglais.",
            'recording_msg': "Enregistrement... (Parlez français maintenant pour la traduction)",
            'direction_display': "Français vers Anglais"
        }
    }
    
    def __init__(self, direction='en_to_fr', whisper_model='small'):
        """
        Initialize translation service
        
        Args:
            direction: Translation direction ('en_to_fr' or 'fr_to_en')
            whisper_model: Whisper model size
        """
        if direction not in self.SUPPORTED_DIRECTIONS:
            raise ValueError(f"Unsupported direction: {direction}. Choose from {list(self.SUPPORTED_DIRECTIONS.keys())}")
        
        self.direction = direction
        self.config = self.SUPPORTED_DIRECTIONS[direction]
        
        # Initialize base voice assistant
        super().__init__(f"TranslationService-{direction}", whisper_model)
        
        # Verify Argos Translate availability
        if not ARGOSTRANSLATE_AVAILABLE:
            raise RuntimeError("Argos Translate is not available. The service cannot start.")
        
        self.logger.info(f"Translation service initialized for {self.config['direction_display']}")
        
        # Set high sensitivity for better voice detection
        self.set_sensitivity_preset('high')  # Good for normal/quiet speech
        
        # Error messages based on language
        if direction == 'en_to_fr':
            self.no_speech_msg = "I didn't quite catch that. Could you please repeat more clearly in English?"
            self.empty_transcription_msg = "I couldn't understand what you said in English. Can you please rephrase?"
            self.translation_error_msg = "Sorry, an error occurred during translation. Please try again."
        else:
            self.no_speech_msg = "Je n'ai pas bien compris. Pourriez-vous répéter plus clairement en français ?"
            self.empty_transcription_msg = "Je n'ai pas réussi à comprendre ce que vous avez dit en français. Pouvez-vous reformuler ?"
            self.translation_error_msg = "Désolé, une erreur est survenue lors de la traduction. Veuillez réessayer."
    
    def process_user_input(self, text):
        """
        Translate user input text
        
        Args:
            text: Text to translate
        
        Returns:
            Translated text
        """
        try:
            self.logger.info(f"Translating: '{text}' ({self.config['input_language']} -> {self.config['output_language']})")
            
            # Perform translation
            translated_text = argostranslate.translate.translate(
                text,
                self.config['input_language'],
                self.config['output_language']
            )
            
            self.logger.info(f"Translation result: '{translated_text}'")
            return translated_text
            
        except Exception as e:
            self.logger.error(f"Translation failed: {e}")
            return self.translation_error_msg
    
    def run_interactive_session(self):
        """Run the main translation service loop"""
        try:
            self.logger.info("Starting interactive translation session")
            
            # Welcome message
            print(f"\n=== {self.config['direction_display']} Translation Service ===")
            print(self.config['welcome_msg'])
            
            # Speak welcome message
            self.speak(self.config['welcome_msg'], self.config['assistant_voice'])
            
            while True:
                try:
                    print(f"\n{self.config['recording_msg']}")
                    print("🎤 Real-time transcription with intelligent silence detection")
                    
                    # Use real-time transcription instead of traditional record->transcribe
                    transcribed_text = self.transcribe_realtime(
                        language=self.config['input_language'],
                        visual_feedback=True
                    )
                    
                    if not self.is_text_valid(transcribed_text):
                        print("No valid speech detected.")
                        self.speak(self.no_speech_msg, self.config['assistant_voice'])
                        continue
                    
                    print(f"You said: {transcribed_text}")
                    
                    # Check for exit commands
                    if self._is_exit_command(transcribed_text):
                        break
                    
                    # Play thinking sound
                    self.play_sound_file('model_is_thinking.mp3')
                    
                    # Translate text
                    translated_text = self.process_user_input(transcribed_text)
                    
                    print(f"Translation: {translated_text}")
                    
                    # Play result sound
                    self.play_sound_file('result.mp3')
                    
                    # Speak translation result
                    self.speak(translated_text, self.config['result_voice'])
                    
                except KeyboardInterrupt:
                    print("\nSession interrupted by user")
                    break
                except Exception as e:
                    self.logger.exception(f"Error in session loop: {e}")
                    print(f"An error occurred: {e}")
                    continue
            
        except Exception as e:
            self.logger.exception(f"Fatal error in interactive session: {e}")
            print(f"Service failed: {e}")
        
        finally:
            print("\nGoodbye!")
            if self.direction == 'en_to_fr':
                self.speak("Goodbye!", self.config['assistant_voice'])
            else:
                self.speak("Au revoir !", self.config['assistant_voice'])
    
    def _is_exit_command(self, text):
        """Check if text contains exit command"""
        exit_commands_en = ['quit', 'exit', 'stop', 'goodbye', 'bye']
        exit_commands_fr = ['quitter', 'sortir', 'arrêter', 'au revoir', 'bye']
        
        text_lower = text.lower()
        
        if self.direction == 'en_to_fr':
            return any(cmd in text_lower for cmd in exit_commands_en)
        else:
            return any(cmd in text_lower for cmd in exit_commands_fr)

def main():
    """Main entry point for translation service"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Voice Translation Service')
    parser.add_argument(
        '--direction', 
        choices=['en_to_fr', 'fr_to_en'],
        default='en_to_fr',
        help='Translation direction (default: en_to_fr)'
    )
    parser.add_argument(
        '--model',
        choices=['tiny', 'small', 'medium', 'large'],
        default='small', 
        help='Whisper model size (default: small)'
    )
    
    args = parser.parse_args()
    
    print("Initializing Translation Service...")
    
    try:
        with TranslationService(args.direction, args.model) as service:
            service.run_interactive_session()
    except KeyboardInterrupt:
        print("\nService stopped by user")
    except Exception as e:
        print(f"Service failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()