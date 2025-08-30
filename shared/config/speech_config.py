"""
Speech recognition configuration settings
"""

# Whisper model configuration
DEFAULT_WHISPER_MODEL = "small"  # Default model size
WHISPER_MODELS = ["tiny", "small", "medium", "large"]

# Device configuration for Whisper
COMPUTE_TYPE_MAPPING = {
    "cuda": "float16",
    "cpu": "float32"
}

# Transcription settings
DEFAULT_TRANSCRIPTION_LANGUAGE = None  # Auto-detect
TRANSCRIPTION_TASK = "transcribe"  # or "translate"

# Text processing settings
TEXT_CLEANUP_PATTERNS = [
    r'\s+',  # Multiple spaces
    r'[^\w\s\-\.\,\;\:\!\?\'\"]',  # Special characters (keep basic punctuation)
    r'^\s+|\s+$'  # Leading/trailing whitespace
]