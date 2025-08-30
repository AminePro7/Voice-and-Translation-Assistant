"""
Cross-platform audio playback functionality
"""

import sys
from pathlib import Path

# Import platform-specific audio libraries
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except (ImportError, Exception):
    PYGAME_AVAILABLE = False

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

class AudioPlayer:
    def __init__(self):
        self.pygame_available = PYGAME_AVAILABLE
        self.winsound_available = WINSOUND_AVAILABLE
        
        if not (self.pygame_available or self.winsound_available):
            print("Warning: No audio playback library available")
    
    def play_wav(self, wav_path):
        """Play WAV file using available audio library"""
        wav_path = Path(wav_path)
        
        if not wav_path.exists():
            print(f"Audio file not found: {wav_path}")
            return False
            
        try:
            # Try winsound first (Windows-specific, more reliable for WAV)
            if self.winsound_available and sys.platform == "win32":
                winsound.PlaySound(str(wav_path), winsound.SND_FILENAME)
                return True
            
            # Fall back to pygame (cross-platform)
            elif self.pygame_available:
                pygame.mixer.music.load(str(wav_path))
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                return True
            
            else:
                print("No audio playback method available")
                return False
                
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False
    
    def play_mp3(self, mp3_path):
        """Play MP3 file using pygame"""
        if not self.pygame_available:
            print("MP3 playback requires pygame")
            return False
            
        mp3_path = Path(mp3_path)
        
        if not mp3_path.exists():
            print(f"Audio file not found: {mp3_path}")
            return False
            
        try:
            pygame.mixer.music.load(str(mp3_path))
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            return True
            
        except Exception as e:
            print(f"Error playing MP3: {e}")
            return False