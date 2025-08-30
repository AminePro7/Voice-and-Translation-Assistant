"""
Real-time audio recording with intelligent silence detection
"""

import pyaudio
import numpy as np
import wave
import tempfile
import threading
import time
from pathlib import Path
from collections import deque
from ..config.audio_config import *

class RealTimeRecorder:
    def __init__(self, silence_threshold=0.005, silence_duration=2.0, min_recording_time=0.5):
        """
        Initialize real-time recorder with silence detection
        
        Args:
            silence_threshold: Volume threshold below which is considered silence
            silence_duration: Seconds of silence before stopping recording
            min_recording_time: Minimum recording time in seconds
        """
        self.audio_format = AUDIO_FORMAT
        self.channels = CHANNELS
        self.rate = RATE
        self.chunk = CHUNK
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.min_recording_time = min_recording_time
        
        # Recording state
        self.is_recording = False
        self.audio_frames = []
        self.silence_start = None
        self.recording_start = None
        
        # Audio level monitoring
        self.audio_levels = deque(maxlen=50)  # Keep last 50 chunks for smoothing
        
        # Get sample width
        pa = pyaudio.PyAudio()
        try:
            self.sample_width = pa.get_sample_size(self.audio_format)
        finally:
            pa.terminate()
    
    def _calculate_volume(self, audio_data):
        """Calculate RMS volume of audio data"""
        if len(audio_data) == 0:
            return 0.0
        
        # Convert to numpy array
        if self.audio_format == pyaudio.paInt16:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
        else:
            audio_array = np.frombuffer(audio_data, dtype=np.float32)
        
        # Calculate RMS
        rms = np.sqrt(np.mean(audio_array.astype(float) ** 2))
        
        # Normalize to 0-1 range
        if self.audio_format == pyaudio.paInt16:
            rms = rms / 32768.0
        
        return rms
    
    def _get_smoothed_volume(self, current_volume):
        """Get smoothed volume using recent history"""
        self.audio_levels.append(current_volume)
        
        if len(self.audio_levels) < 5:
            return current_volume
        
        # Use weighted average with more weight on recent samples
        weights = np.exp(np.linspace(-1, 0, len(self.audio_levels)))
        smoothed = np.average(self.audio_levels, weights=weights)
        
        return smoothed
    
    def _is_speech_detected(self, volume):
        """Detect if current audio contains speech"""
        smoothed_volume = self._get_smoothed_volume(volume)
        
        # Dynamic threshold adjustment based on ambient noise
        if len(self.audio_levels) > 20:
            ambient_level = np.percentile(list(self.audio_levels)[-20:], 10)  # Lower percentile for better sensitivity
            # Use more conservative multiplier to avoid being too aggressive
            adjusted_threshold = max(self.silence_threshold, ambient_level * 1.2)
        else:
            adjusted_threshold = self.silence_threshold
        
        # Additional sensitivity boost for quiet voices
        if smoothed_volume > self.silence_threshold * 0.5:  # Even very quiet speech
            return True
        
        return smoothed_volume > adjusted_threshold
    
    def record_with_silence_detection(self, temp_dir=None, max_duration=30.0, 
                                    volume_callback=None, speech_callback=None):
        """
        Record audio with intelligent silence detection
        
        Args:
            temp_dir: Directory for temporary files
            max_duration: Maximum recording duration in seconds
            volume_callback: Callback function for volume updates
            speech_callback: Callback function for speech detection events
        
        Returns:
            Path to recorded audio file, or None if no speech detected
        """
        if temp_dir is None:
            temp_dir = Path(tempfile.gettempdir())
        
        temp_audio_path = temp_dir / "realtime_audio.wav"
        
        pa = pyaudio.PyAudio()
        
        try:
            stream = pa.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print("🎤 Listening... (speak now)")
            if speech_callback:
                speech_callback("listening")
            
            self.audio_frames = []
            self.silence_start = None
            self.recording_start = time.time()
            self.is_recording = False
            speech_detected = False
            
            while True:
                current_time = time.time()
                elapsed_time = current_time - self.recording_start
                
                # Check maximum duration
                if elapsed_time > max_duration:
                    print("⏰ Maximum recording time reached")
                    break
                
                try:
                    # Read audio chunk
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    volume = self._calculate_volume(data)
                    
                    # Update volume callback
                    if volume_callback:
                        volume_callback(volume)
                    
                    # Check for speech
                    has_speech = self._is_speech_detected(volume)
                    
                    if has_speech:
                        # Speech detected
                        if not self.is_recording:
                            print("🗣️  Speech detected - Recording started")
                            if speech_callback:
                                speech_callback("recording")
                            self.is_recording = True
                            speech_detected = True
                        
                        # Reset silence timer
                        self.silence_start = None
                        self.audio_frames.append(data)
                        
                    else:
                        # Silence detected
                        if self.is_recording:
                            # We're recording but now have silence
                            if self.silence_start is None:
                                self.silence_start = current_time
                            
                            silence_duration = current_time - self.silence_start
                            
                            # Continue recording during brief silence
                            self.audio_frames.append(data)
                            
                            # Check if silence duration exceeded threshold
                            recording_duration = elapsed_time
                            if (silence_duration >= self.silence_duration and 
                                recording_duration >= self.min_recording_time):
                                print("🤫 Silence detected - Recording stopped")
                                if speech_callback:
                                    speech_callback("stopped")
                                break
                        
                        else:
                            # Not recording and still silence - just waiting
                            if not speech_detected and elapsed_time > 10.0:
                                print("⏳ No speech detected in 10 seconds")
                                break
                
                except OSError as e:
                    # Handle audio buffer overflow
                    print(f"Audio buffer overflow: {e}")
                    continue
            
            stream.stop_stream()
            stream.close()
            
            # Check if we have recorded audio
            if not speech_detected or len(self.audio_frames) == 0:
                print("❌ No speech recorded")
                return None
            
            # Save recorded audio
            with wave.open(str(temp_audio_path), 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.sample_width)
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.audio_frames))
            
            recording_duration = len(self.audio_frames) * self.chunk / self.rate
            print(f"✅ Recording completed: {recording_duration:.2f}s")
            
            return temp_audio_path
            
        except Exception as e:
            print(f"Recording error: {e}")
            return None
            
        finally:
            pa.terminate()
    
    def start_background_recording(self, temp_dir=None, result_callback=None):
        """
        Start recording in background thread with callback
        
        Args:
            temp_dir: Directory for temporary files
            result_callback: Function to call with recording result
        """
        def recording_thread():
            result = self.record_with_silence_detection(temp_dir)
            if result_callback:
                result_callback(result)
        
        thread = threading.Thread(target=recording_thread, daemon=True)
        thread.start()
        return thread
    
    def get_recording_stats(self):
        """Get current recording statistics"""
        if not self.is_recording:
            return None
        
        current_time = time.time()
        recording_duration = current_time - self.recording_start if self.recording_start else 0
        silence_duration = current_time - self.silence_start if self.silence_start else 0
        
        return {
            'recording_duration': recording_duration,
            'silence_duration': silence_duration,
            'frames_recorded': len(self.audio_frames),
            'is_recording': self.is_recording
        }