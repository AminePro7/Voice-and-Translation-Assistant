"""
Audio recording functionality shared across services
"""

import pyaudio
import numpy as np
import wave
import tempfile
from pathlib import Path
from ..config.audio_config import *

class AudioRecorder:
    def __init__(self):
        self.audio_format = AUDIO_FORMAT
        self.channels = CHANNELS
        self.rate = RATE
        self.chunk = CHUNK
        self.record_seconds = RECORD_SECONDS
        self.silence_threshold = SILENCE_THRESHOLD
        
        pa = pyaudio.PyAudio()
        try:
            self.sample_width = pa.get_sample_size(self.audio_format)
        finally:
            pa.terminate()
    
    def record_audio(self, temp_dir=None):
        """Record audio from microphone and return the file path"""
        if temp_dir is None:
            temp_dir = Path(tempfile.gettempdir())
        
        temp_audio_path = temp_dir / "temp_audio.wav"
        
        pa = pyaudio.PyAudio()
        
        try:
            stream = pa.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print(f"Recording... (Speak now for {self.record_seconds} seconds)")
            frames = []
            
            for _ in range(int(self.rate / self.chunk * self.record_seconds)):
                data = stream.read(self.chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Save audio to WAV file
            with wave.open(str(temp_audio_path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.sample_width)
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
            
            return temp_audio_path
            
        finally:
            pa.terminate()
    
    def set_recording_duration(self, seconds):
        """Set custom recording duration"""
        self.record_seconds = seconds