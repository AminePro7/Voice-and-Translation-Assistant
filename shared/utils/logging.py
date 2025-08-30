"""
Logging utilities for voice assistant services
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

class VoiceAssistantLogger:
    def __init__(self, name="VoiceAssistant", log_dir=None, log_level=logging.INFO):
        """
        Initialize logger for voice assistant services
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            log_level: Logging level
        """
        self.name = name
        self.log_level = log_level
        
        # Set up log directory
        if log_dir is None:
            log_dir = Path.cwd() / "logs"
        else:
            log_dir = Path(log_dir)
        
        log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Console handler (simple format)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (detailed format)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = log_dir / f"{name}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info(f"Logger initialized: {name}")
        self.logger.info(f"Log file: {log_filename}")
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)
    
    def exception(self, message):
        """Log exception with traceback"""
        self.logger.exception(message)
    
    def log_system_info(self):
        """Log system information"""
        from .system import SystemUtils
        
        self.info("=== System Information ===")
        platform_info = SystemUtils.get_platform_info()
        for key, value in platform_info.items():
            self.info(f"{key}: {value}")
        
        cuda_info = SystemUtils.get_cuda_info()
        self.info("=== Device Information ===")
        for key, value in cuda_info.items():
            self.info(f"{key}: {value}")
    
    def log_service_start(self, service_name, config=None):
        """Log service startup"""
        self.info(f"=== Starting {service_name} ===")
        if config:
            self.info(f"Configuration: {config}")
    
    def log_service_stop(self, service_name):
        """Log service shutdown"""
        self.info(f"=== Stopping {service_name} ===")
    
    def log_audio_event(self, event_type, details=None):
        """Log audio-related events"""
        message = f"Audio Event: {event_type}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_transcription(self, text, language=None, confidence=None):
        """Log speech transcription results"""
        message = f"Transcription: '{text}'"
        if language:
            message += f" (Language: {language}"
            if confidence:
                message += f", Confidence: {confidence:.2f}"
            message += ")"
        self.info(message)
    
    def log_tts(self, text, language, output_path):
        """Log text-to-speech synthesis"""
        self.info(f"TTS Synthesis: '{text}' -> {output_path} (Language: {language})")
    
    def log_error_with_context(self, error, context=None):
        """Log error with contextual information"""
        message = f"Error: {error}"
        if context:
            message += f" (Context: {context})"
        self.error(message)