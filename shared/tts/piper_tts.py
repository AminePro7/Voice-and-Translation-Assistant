"""
Piper TTS wrapper for text-to-speech functionality
"""

import subprocess
import tempfile
from pathlib import Path
from ..config.tts_config import TTS_MODELS, LANGUAGE_CODES, DEFAULT_MODELS_DIR, DEFAULT_PIPER_DIR

class PiperTTS:
    def __init__(self, models_dir=None, piper_dir=None):
        """
        Initialize Piper TTS with model and executable paths
        
        Args:
            models_dir: Path to TTS models directory
            piper_dir: Path to Piper executable directory
        """
        self.models_dir = Path(models_dir) if models_dir else DEFAULT_MODELS_DIR
        self.piper_dir = Path(piper_dir) if piper_dir else DEFAULT_PIPER_DIR
        
        # Set Piper executable path
        self.piper_exe = self.piper_dir / "piper.exe"
        
        # Verify Piper executable exists
        if not self.piper_exe.exists():
            raise FileNotFoundError(f"Piper executable not found at {self.piper_exe}")
    
    def get_model_paths(self, language):
        """Get model and config paths for a given language"""
        lang_code = LANGUAGE_CODES.get(language.lower(), language)
        
        if lang_code not in TTS_MODELS:
            raise ValueError(f"Unsupported language: {language}")
        
        model_info = TTS_MODELS[lang_code]
        model_path = self.models_dir / model_info["model"]
        config_path = self.models_dir / model_info["config"]
        
        # Verify model files exist
        if not model_path.exists():
            raise FileNotFoundError(f"TTS model not found at {model_path}")
        if not config_path.exists():
            raise FileNotFoundError(f"TTS config not found at {config_path}")
        
        return model_path, config_path
    
    def synthesize(self, text, language, output_path=None):
        """
        Convert text to speech using Piper TTS
        
        Args:
            text: Text to synthesize
            language: Language code (e.g., 'fr_FR', 'en_US', 'french', 'english')
            output_path: Output WAV file path (optional, creates temp file if not provided)
        
        Returns:
            Path to generated audio file
        """
        model_path, config_path = self.get_model_paths(language)
        
        # Create output file if not provided
        if output_path is None:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            output_path = Path(temp_file.name)
            temp_file.close()
        else:
            output_path = Path(output_path)
        
        # Build Piper command
        cmd = [
            str(self.piper_exe),
            "--model", str(model_path),
            "--config", str(config_path), 
            "--output_file", str(output_path)
        ]
        
        try:
            # Run Piper TTS
            result = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                check=True
            )
            
            # Verify output file was created
            if not output_path.exists():
                raise RuntimeError("Piper TTS failed to create output file")
            
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Piper TTS failed: {e.stderr if e.stderr else e}"
            raise RuntimeError(error_msg) from e
        except Exception as e:
            raise RuntimeError(f"TTS synthesis error: {e}") from e
    
    def is_language_supported(self, language):
        """Check if a language is supported"""
        lang_code = LANGUAGE_CODES.get(language.lower(), language)
        return lang_code in TTS_MODELS
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return list(TTS_MODELS.keys())