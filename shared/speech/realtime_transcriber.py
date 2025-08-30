"""
Real-time speech transcription with streaming capabilities
"""

import threading
import time
import queue
from pathlib import Path
from .whisper_transcriber import WhisperTranscriber
from .text_processor import TextProcessor
from ..audio.realtime_recorder import RealTimeRecorder

class RealTimeTranscriber:
    def __init__(self, whisper_model="small", device=None):
        """
        Initialize real-time transcriber
        
        Args:
            whisper_model: Whisper model size
            device: Device to use (cuda/cpu)
        """
        self.transcriber = WhisperTranscriber(whisper_model, device)
        self.text_processor = TextProcessor()
        self.recorder = RealTimeRecorder()
        
        # Threading and queue management
        self.transcription_queue = queue.Queue()
        self.is_active = False
        self.current_transcription = ""
        
        # Callbacks
        self.on_partial_result = None
        self.on_final_result = None
        self.on_volume_update = None
        self.on_speech_event = None
    
    def set_callbacks(self, on_partial_result=None, on_final_result=None, 
                     on_volume_update=None, on_speech_event=None):
        """
        Set callback functions for real-time events
        
        Args:
            on_partial_result: Called with partial transcription updates
            on_final_result: Called with final transcription result
            on_volume_update: Called with current audio volume level
            on_speech_event: Called with speech detection events
        """
        self.on_partial_result = on_partial_result
        self.on_final_result = on_final_result
        self.on_volume_update = on_volume_update
        self.on_speech_event = on_speech_event
    
    def _volume_callback(self, volume):
        """Handle volume updates from recorder"""
        if self.on_volume_update:
            self.on_volume_update(volume)
    
    def _speech_callback(self, event):
        """Handle speech detection events from recorder"""
        if self.on_speech_event:
            self.on_speech_event(event)
    
    def _transcription_worker(self, audio_path):
        """Worker thread for audio transcription"""
        try:
            if audio_path and audio_path.exists():
                # Transcribe the audio
                text = self.transcriber.transcribe(audio_path)
                
                # Clean the text
                cleaned_text = self.text_processor.clean_text(text)
                
                # Check if text is meaningful
                if self.text_processor.is_empty_or_nonsense(cleaned_text):
                    cleaned_text = ""
                
                # Put result in queue
                self.transcription_queue.put({
                    'type': 'final',
                    'text': cleaned_text,
                    'raw_text': text
                })
                
        except Exception as e:
            self.transcription_queue.put({
                'type': 'error',
                'error': str(e)
            })
    
    def start_continuous_transcription(self, temp_dir=None, max_duration=30.0):
        """
        Start continuous transcription with real-time feedback
        
        Args:
            temp_dir: Directory for temporary files
            max_duration: Maximum recording duration
        
        Returns:
            Final transcribed text or None
        """
        self.is_active = True
        
        try:
            # Start recording with silence detection
            audio_path = self.recorder.record_with_silence_detection(
                temp_dir=temp_dir,
                max_duration=max_duration,
                volume_callback=self._volume_callback,
                speech_callback=self._speech_callback
            )
            
            if not audio_path:
                if self.on_final_result:
                    self.on_final_result("")
                return ""
            
            # Start transcription in background
            transcription_thread = threading.Thread(
                target=self._transcription_worker,
                args=(audio_path,),
                daemon=True
            )
            transcription_thread.start()
            
            # Show processing indicator
            if self.on_speech_event:
                self.on_speech_event("processing")
            
            # Wait for transcription result
            try:
                result = self.transcription_queue.get(timeout=30.0)
                
                if result['type'] == 'final':
                    final_text = result['text']
                    
                    if self.on_final_result:
                        self.on_final_result(final_text)
                    
                    return final_text
                    
                elif result['type'] == 'error':
                    print(f"Transcription error: {result['error']}")
                    if self.on_final_result:
                        self.on_final_result("")
                    return ""
                
            except queue.Empty:
                print("Transcription timed out")
                if self.on_final_result:
                    self.on_final_result("")
                return ""
        
        except Exception as e:
            print(f"Real-time transcription error: {e}")
            if self.on_final_result:
                self.on_final_result("")
            return ""
        
        finally:
            self.is_active = False
    
    def transcribe_with_visual_feedback(self, temp_dir=None):
        """
        Transcribe with visual feedback showing audio levels and speech detection
        
        Returns:
            Transcribed text
        """
        print("\n" + "="*60)
        print("🎤 REAL-TIME SPEECH TRANSCRIPTION")
        print("="*60)
        
        # Visual feedback state
        volume_bar_length = 30
        last_volume = 0
        
        def volume_callback(volume):
            nonlocal last_volume
            last_volume = volume
            
            # Create volume bar
            bar_level = int(volume * volume_bar_length)
            volume_bar = "█" * bar_level + "░" * (volume_bar_length - bar_level)
            
            # Color coding based on volume
            if volume > 0.1:
                status = "🗣️  SPEAKING"
            elif volume > 0.05:
                status = "🤏 LOW VOICE"
            else:
                status = "🤫 SILENCE"
            
            # Update display (overwrite previous line)
            print(f"\r{status} [{volume_bar}] {volume:.3f}", end="", flush=True)
        
        def speech_callback(event):
            if event == "listening":
                print("🎧 Listening for speech...")
            elif event == "recording":
                print("\n🔴 Recording in progress...")
            elif event == "stopped":
                print(f"\n✅ Recording completed")
            elif event == "processing":
                print("🔄 Processing audio...")
        
        def final_callback(text):
            print(f"\n📝 Transcription: '{text}'")
        
        # Set callbacks
        self.set_callbacks(
            on_volume_update=volume_callback,
            on_speech_event=speech_callback,
            on_final_result=final_callback
        )
        
        # Start transcription
        result = self.start_continuous_transcription(temp_dir)
        
        print("="*60)
        return result
    
    def get_model_info(self):
        """Get transcriber model information"""
        return self.transcriber.get_model_info()
    
    def set_silence_params(self, threshold=0.01, duration=2.0):
        """
        Update silence detection parameters
        
        Args:
            threshold: Volume threshold for silence detection
            duration: Duration of silence before stopping
        """
        self.recorder.silence_threshold = threshold
        self.recorder.silence_duration = duration