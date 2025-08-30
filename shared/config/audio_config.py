"""
Audio configuration settings shared across all voice assistant services
"""

import pyaudio

# Audio recording configuration
AUDIO_FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 7  # Default recording duration
SILENCE_THRESHOLD = 0.005  # Lower threshold for better sensitivity
VOLUME_NORM = 0.3

# Audio device detection
def get_audio_device_info():
    """Get available audio devices"""
    pa = pyaudio.PyAudio()
    try:
        sample_width = pa.get_sample_size(AUDIO_FORMAT)
        return sample_width
    finally:
        pa.terminate()