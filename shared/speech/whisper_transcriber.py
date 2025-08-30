"""
Whisper-based speech recognition wrapper
"""

import torch
from faster_whisper import WhisperModel
from pathlib import Path
from ..config.speech_config import *

class WhisperTranscriber:
    def __init__(self, model_size=DEFAULT_WHISPER_MODEL, device=None):
        """
        Initialize Whisper transcriber
        
        Args:
            model_size: Whisper model size (tiny, small, medium, large)
            device: Device to use (cuda/cpu), auto-detected if None
        """
        self.model_size = model_size
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # Set compute type based on device
        self.compute_type = COMPUTE_TYPE_MAPPING.get(self.device, "float32")
        
        print(f"Initializing Whisper model: {self.model_size} on {self.device} with {self.compute_type}")
        
        # Initialize Whisper model
        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            print("Whisper model loaded successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Whisper model: {e}")
    
    def transcribe(self, audio_path, language=DEFAULT_TRANSCRIPTION_LANGUAGE, task=TRANSCRIPTION_TASK):
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code for transcription (None for auto-detect)
            task: Task type ('transcribe' or 'translate')
        
        Returns:
            Transcribed text as string
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            print(f"Transcribing audio: {audio_path}")
            
            # Perform transcription
            segments, info = self.model.transcribe(
                str(audio_path),
                language=language,
                task=task
            )
            
            # Combine all segments into single text
            transcribed_text = " ".join([segment.text for segment in segments])
            
            print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            print(f"Transcription: {transcribed_text}")
            
            return transcribed_text.strip()
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")
    
    def transcribe_with_info(self, audio_path, language=DEFAULT_TRANSCRIPTION_LANGUAGE, task=TRANSCRIPTION_TASK):
        """
        Transcribe audio and return detailed information
        
        Returns:
            Dictionary with text, language, probability, and segments
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            segments, info = self.model.transcribe(
                str(audio_path),
                language=language,
                task=task
            )
            
            # Convert segments to list for JSON serialization
            segment_list = []
            transcribed_text = ""
            
            for segment in segments:
                segment_info = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                }
                segment_list.append(segment_info)
                transcribed_text += segment.text + " "
            
            result = {
                "text": transcribed_text.strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "segments": segment_list
            }
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")
    
    def set_model_size(self, model_size):
        """Change Whisper model size"""
        if model_size not in WHISPER_MODELS:
            raise ValueError(f"Unsupported model size: {model_size}")
        
        self.model_size = model_size
        
        # Reinitialize model with new size
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type
        )
        print(f"Switched to Whisper model: {model_size}")
    
    def is_cuda_available(self):
        """Check if CUDA is available"""
        return torch.cuda.is_available()
    
    def get_model_info(self):
        """Get current model information"""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "cuda_available": self.is_cuda_available()
        }