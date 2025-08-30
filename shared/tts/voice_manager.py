"""
Voice management and TTS orchestration
"""

from .piper_tts import PiperTTS
from ..audio.player import AudioPlayer
from pathlib import Path
import tempfile

class VoiceManager:
    def __init__(self, models_dir=None, piper_dir=None):
        """Initialize voice manager with TTS and audio player"""
        self.tts = PiperTTS(models_dir, piper_dir)
        self.audio_player = AudioPlayer()
        self.temp_files = []  # Track temporary files for cleanup
    
    def speak(self, text, language="fr_FR", play_audio=True, save_path=None):
        """
        Convert text to speech and optionally play it
        
        Args:
            text: Text to speak
            language: Language for TTS
            play_audio: Whether to play the audio immediately
            save_path: Path to save the audio file (optional)
        
        Returns:
            Path to generated audio file
        """
        try:
            # Generate audio file
            if save_path:
                audio_path = self.tts.synthesize(text, language, save_path)
            else:
                audio_path = self.tts.synthesize(text, language)
                self.temp_files.append(audio_path)  # Track for cleanup
            
            # Play audio if requested
            if play_audio:
                success = self.audio_player.play_wav(audio_path)
                if not success:
                    print("Warning: Failed to play synthesized audio")
            
            return audio_path
            
        except Exception as e:
            print(f"Error in voice synthesis: {e}")
            return None
    
    def speak_file(self, file_path, language="fr_FR", play_audio=True):
        """
        Read text from file and speak it
        
        Args:
            file_path: Path to text file
            language: Language for TTS
            play_audio: Whether to play the audio
        
        Returns:
            Path to generated audio file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            
            if not text:
                print("Warning: Text file is empty")
                return None
            
            return self.speak(text, language, play_audio)
            
        except Exception as e:
            print(f"Error reading text file: {e}")
            return None
    
    def get_supported_languages(self):
        """Get list of supported TTS languages"""
        return self.tts.get_supported_languages()
    
    def is_language_supported(self, language):
        """Check if language is supported"""
        return self.tts.is_language_supported(language)
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception as e:
                print(f"Warning: Failed to delete temp file {temp_file}: {e}")
        
        self.temp_files.clear()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup_temp_files()