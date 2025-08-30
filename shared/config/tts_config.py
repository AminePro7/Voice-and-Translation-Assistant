"""
Text-to-Speech configuration settings
"""

from pathlib import Path

# Default TTS model paths (relative to project root)
DEFAULT_MODELS_DIR = Path("shared/models/tts")
DEFAULT_PIPER_DIR = Path("shared/resources/piper")

# Supported TTS models
TTS_MODELS = {
    "fr_FR": {
        "model": "fr_FR-upmc-medium.onnx",
        "config": "fr_FR-upmc-medium.onnx.json"
    },
    "en_US": {
        "model": "en_US-amy-medium.onnx", 
        "config": "en_US-amy-medium.onnx.json"
    }
}

# Language mappings
LANGUAGE_CODES = {
    "french": "fr_FR",
    "english": "en_US",
    "fr": "fr_FR",
    "en": "en_US"
}