"""
Base class for all voice assistant services
"""

from abc import ABC, abstractmethod
import tempfile
from pathlib import Path

from ..config.paths_config import PathConfig
from ..config.audio_config import *
from ..audio.recorder import AudioRecorder
from ..audio.normalizer import AudioNormalizer
from ..audio.player import AudioPlayer
from ..tts.voice_manager import VoiceManager
from ..tts.text_cleaner import TTSTextCleaner
from ..speech.whisper_transcriber import WhisperTranscriber
from ..speech.text_processor import TextProcessor
from ..speech.realtime_transcriber import RealTimeTranscriber
from ..utils.system import SystemUtils
from ..utils.logging import VoiceAssistantLogger

class BaseVoiceAssistant(ABC):
    """
    Abstract base class for voice assistant services
    
    Provides common functionality for:
    - Audio recording and playback
    - Speech recognition (Whisper)
    - Text-to-speech (Piper)
    - Configuration management
    - Logging and cleanup
    """
    
    def __init__(self, service_name="VoiceAssistant", whisper_model="small"):
        """
        Initialize base voice assistant
        
        Args:
            service_name: Name of the service (for logging)
            whisper_model: Whisper model size to use
        """
        self.service_name = service_name
        
        # Initialize configuration
        self.paths = PathConfig()
        self.paths.create_directories()
        
        # Initialize logging
        self.logger = VoiceAssistantLogger(
            name=service_name,
            log_dir=self.paths.logs_dir
        )
        
        self.logger.log_service_start(service_name)
        self.logger.log_system_info()
        
        # Initialize components
        self._init_audio_components()
        self._init_speech_components(whisper_model)
        self._init_tts_components()
        
        # Create temporary directory
        self.temp_dir = self.paths.get_temp_dir(service_name)
        self.logger.info(f"Temporary directory: {self.temp_dir}")
        
        self.logger.info(f"{service_name} initialization completed")
    
    def _init_audio_components(self):
        """Initialize audio recording and playback components"""
        self.logger.info("Initializing audio components...")
        
        self.audio_recorder = AudioRecorder()
        self.audio_normalizer = AudioNormalizer()
        self.audio_player = AudioPlayer()
        
        self.logger.info("Audio components initialized")
    
    def _init_speech_components(self, whisper_model):
        """Initialize speech recognition components"""
        self.logger.info(f"Initializing speech recognition with Whisper {whisper_model}...")
        
        device = SystemUtils.get_optimal_device()
        self.transcriber = WhisperTranscriber(whisper_model, device)
        self.text_processor = TextProcessor()
        
        # Initialize real-time transcriber
        self.realtime_transcriber = RealTimeTranscriber(whisper_model, device)
        
        self.logger.info("Speech recognition initialized")
    
    def _init_tts_components(self):
        """Initialize text-to-speech components"""
        self.logger.info("Initializing text-to-speech components...")
        
        self.voice_manager = VoiceManager(
            models_dir=self.paths.tts_models_dir,
            piper_dir=self.paths.piper_dir
        )
        
        self.logger.info("Text-to-speech components initialized")
    
    def record_audio(self, duration=None):
        """
        Record audio from microphone
        
        Args:
            duration: Recording duration in seconds (uses default if None)
        
        Returns:
            Path to recorded audio file
        """
        if duration:
            self.audio_recorder.set_recording_duration(duration)
        
        self.logger.log_audio_event("Recording started")
        audio_path = self.audio_recorder.record_audio(self.temp_dir)
        self.logger.log_audio_event("Recording completed", str(audio_path))
        
        return audio_path
    
    def transcribe_audio(self, audio_path, language=None):
        """
        Transcribe audio to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (None for auto-detect)
        
        Returns:
            Transcribed text string
        """
        try:
            # Normalize audio before transcription
            self.audio_normalizer.normalize_audio(audio_path)
            
            # Transcribe
            text = self.transcriber.transcribe(audio_path, language)
            
            # Clean text
            cleaned_text = self.text_processor.clean_text(text)
            
            self.logger.log_transcription(cleaned_text, language)
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return ""
    
    def transcribe_realtime(self, language=None, visual_feedback=True):
        """
        Perform real-time transcription with silence detection
        
        Args:
            language: Language code for transcription
            visual_feedback: Whether to show visual feedback
        
        Returns:
            Transcribed text string
        """
        try:
            self.logger.log_audio_event("Real-time transcription started")
            
            # Configure language if specified
            # Note: Whisper auto-detects language, but we can log the expected language
            if language:
                self.logger.info(f"Expected language: {language}")
            
            if visual_feedback:
                # Use visual feedback version
                text = self.realtime_transcriber.transcribe_with_visual_feedback(self.temp_dir)
            else:
                # Use standard real-time transcription
                text = self.realtime_transcriber.start_continuous_transcription(self.temp_dir)
            
            if text:
                # Clean text
                cleaned_text = self.text_processor.clean_text(text)
                self.logger.log_transcription(cleaned_text, language)
                return cleaned_text
            else:
                self.logger.info("No speech detected in real-time transcription")
                return ""
            
        except Exception as e:
            self.logger.error(f"Real-time transcription failed: {e}")
            return ""
    
    def configure_silence_detection(self, threshold=0.005, duration=2.0, preset=None):
        """
        Configure silence detection parameters
        
        Args:
            threshold: Volume threshold for silence detection (0.0-1.0)
            duration: Duration of silence in seconds before stopping
            preset: Sensitivity preset name ('very_high', 'high', 'medium', 'low', 'very_low')
        """
        if preset:
            from ..audio.sensitivity_presets import auto_configure_sensitivity
            config = auto_configure_sensitivity(self.realtime_transcriber.recorder, preset)
            self.logger.info(f"Applied sensitivity preset '{preset}': {config}")
        else:
            self.realtime_transcriber.set_silence_params(threshold, duration)
            self.logger.info(f"Silence detection configured: threshold={threshold}, duration={duration}s")
    
    def set_sensitivity_preset(self, preset_name):
        """
        Set sensitivity using a predefined preset
        
        Args:
            preset_name: Preset name ('very_high', 'high', 'medium', 'low', 'very_low')
                       or environment ('quiet_room', 'normal_room', 'office', 'cafe_restaurant', 'street_outdoor')
        """
        self.configure_silence_detection(preset=preset_name)
    
    def speak(self, text, language="fr_FR", play_audio=True):
        """
        Convert text to speech and optionally play it
        
        Args:
            text: Text to speak
            language: TTS language code
            play_audio: Whether to play the audio
        
        Returns:
            Path to generated audio file
        """
        try:
            # Clean text for better TTS pronunciation
            cleaned_text = TTSTextCleaner.extract_main_content(text)
            
            if not cleaned_text:
                self.logger.warning("Text is empty after cleaning for TTS")
                return None
            
            audio_path = self.voice_manager.speak(cleaned_text, language, play_audio)
            
            if audio_path:
                self.logger.log_tts(f"Original: '{text[:100]}...' | Cleaned: '{cleaned_text}'", language, audio_path)
            
            return audio_path
            
        except Exception as e:
            self.logger.error(f"TTS failed: {e}")
            return None
    
    def speak_chunks(self, text, language="fr_FR", max_chunk_length=150):
        """
        Speak long text in smaller, more natural chunks
        
        Args:
            text: Long text to speak
            language: TTS language code
            max_chunk_length: Maximum length per chunk
        
        Returns:
            List of audio file paths generated
        """
        try:
            chunks = TTSTextCleaner.format_for_speech(text, max_chunk_length)
            audio_paths = []
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    self.logger.info(f"Speaking chunk {i+1}/{len(chunks)}: '{chunk[:50]}...'")
                    audio_path = self.voice_manager.speak(chunk, language, True)
                    if audio_path:
                        audio_paths.append(audio_path)
                    
                    # Small pause between chunks for natural flow
                    if i < len(chunks) - 1:
                        import time
                        time.sleep(0.5)
            
            return audio_paths
            
        except Exception as e:
            self.logger.error(f"Chunked TTS failed: {e}")
            return []
    
    def play_sound_file(self, sound_name):
        """
        Play a sound file from the shared sounds directory
        
        Args:
            sound_name: Name of sound file (e.g., 'model_is_thinking.mp3')
        
        Returns:
            True if successful, False otherwise
        """
        sound_path = self.paths.sounds_dir / sound_name
        
        if not sound_path.exists():
            self.logger.warning(f"Sound file not found: {sound_path}")
            return False
        
        try:
            if sound_path.suffix.lower() == '.mp3':
                return self.audio_player.play_mp3(sound_path)
            else:
                return self.audio_player.play_wav(sound_path)
        except Exception as e:
            self.logger.error(f"Failed to play sound {sound_name}: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files and resources"""
        self.logger.info("Cleaning up resources...")
        
        try:
            # Clean up voice manager temp files
            if hasattr(self, 'voice_manager'):
                self.voice_manager.cleanup_temp_files()
            
            # Remove temporary directory
            if hasattr(self, 'temp_dir') and self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                self.logger.info(f"Removed temporary directory: {self.temp_dir}")
        
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
        
        self.logger.log_service_stop(self.service_name)
    
    def get_supported_languages(self):
        """Get list of supported TTS languages"""
        return self.voice_manager.get_supported_languages()
    
    def is_text_valid(self, text):
        """Check if transcribed text is valid and meaningful"""
        return not self.text_processor.is_empty_or_nonsense(text)
    
    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def process_user_input(self, text):
        """
        Process user input text and generate response
        
        Args:
            text: User input text
        
        Returns:
            Response text to be spoken
        """
        pass
    
    @abstractmethod
    def run_interactive_session(self):
        """
        Run the main interactive session loop
        """
        pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()