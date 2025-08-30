"""
Audio normalization functionality
"""

import numpy as np
import wave
from pathlib import Path
from ..config.audio_config import VOLUME_NORM

class AudioNormalizer:
    @staticmethod
    def normalize_audio(audio_path, target_volume=VOLUME_NORM):
        """Normalize audio volume to target level"""
        try:
            with wave.open(str(audio_path), 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                sample_width = wf.getsampwidth()
                framerate = wf.getframerate()
                channels = wf.getnchannels()
            
            # Convert to numpy array
            if sample_width == 2:  # 16-bit
                audio_data = np.frombuffer(frames, dtype=np.int16)
            elif sample_width == 4:  # 32-bit
                audio_data = np.frombuffer(frames, dtype=np.int32)
            else:
                print(f"Unsupported sample width: {sample_width}")
                return False
            
            # Calculate current volume (RMS)
            current_volume = np.sqrt(np.mean(audio_data.astype(float) ** 2))
            
            if current_volume > 0:
                # Normalize to target volume
                max_val = np.iinfo(audio_data.dtype).max
                target_rms = target_volume * max_val
                scaling_factor = target_rms / current_volume
                normalized_audio = (audio_data * scaling_factor).astype(audio_data.dtype)
                
                # Save normalized audio
                with wave.open(str(audio_path), 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(sample_width)
                    wf.setframerate(framerate)
                    wf.writeframes(normalized_audio.tobytes())
                
                return True
            else:
                print("Audio appears to be silent, skipping normalization")
                return False
                
        except Exception as e:
            print(f"Error normalizing audio: {e}")
            return False