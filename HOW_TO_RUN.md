# How to Run the Voice and Translation Assistant

## 🚀 Quick Start Guide

This modular voice assistant provides two main services:
1. **Translation Service** - Real-time voice translation (English ↔ French)
2. **RAG Assistant Service** - AI-powered voice assistant with document knowledge

## 📋 Prerequisites

### **System Requirements**
- **Python 3.8+** (recommended: Python 3.9-3.11)
- **Microphone** - for voice input
- **Speakers/Headphones** - for audio output
- **Windows/Linux/macOS** - cross-platform compatible

### **Hardware Recommendations**
- **RAM**: 4GB minimum, 8GB+ recommended (for LLM models)
- **Storage**: 2GB free space for models and dependencies
- **CPU**: Any modern processor (GPU optional for faster processing)

## ⚡ Installation

### **Step 1: Clone and Setup**
```bash
# Clone the repository
git clone <repository-url>
cd Voice-and-Translation-Assistant

# Install core dependencies
pip install -r requirements.txt
```

### **Step 2: Install Service-Specific Dependencies**

**For Translation Service:**
```bash
pip install -r services/translation/requirements.txt
```

**For RAG Assistant Service:**
```bash
pip install -r services/assistance/requirements.txt
```

**Or install everything at once:**
```bash
pip install -e .[all]
```

### **Step 3: Verify Installation**
```bash
# Test all components
python test_modular.py

# Test real-time features
python test_realtime.py
```

## 🎤 Voice Detection Setup

### **Test Your Microphone**
```bash
# Run sensitivity test to optimize voice detection
python test_sensitivity.py
```

This will help you:
- ✅ Test if your microphone works
- ✅ Find the right sensitivity level for your voice
- ✅ Configure optimal settings for your environment

## 🌍 Translation Service

### **Basic Usage**
```bash
# English to French translation
python services/translation/translation_service.py --direction en_to_fr

# French to English translation  
python services/translation/translation_service.py --direction fr_to_en
```

### **Advanced Options**
```bash
# Use different Whisper model sizes
python services/translation/translation_service.py --direction en_to_fr --model medium
python services/translation/translation_service.py --direction en_to_fr --model large

# Available models: tiny, small, medium, large
# Larger models = better accuracy, slower processing
```

### **What to Expect**
```
=== English to French Translation Service ===
Hello, I am your voice translation assistant.

Recording... (Speak English now for translation)
🎤 Real-time transcription with intelligent silence detection

🎤 REAL-TIME SPEECH TRANSCRIPTION
🎧 Listening for speech...
🗣️  SPEAKING [██████████████░░░░░░░░░░░░░░░░] 0.342
✅ Recording completed
📝 Transcription: 'Good morning, how are you?'
🔄 Translation: 'Bonjour, comment allez-vous ?'
[Speaks French translation aloud]
```

### **Supported Language Pairs**
- **English → French** (`--direction en_to_fr`)  
- **French → English** (`--direction fr_to_en`)

## 🤖 RAG Assistant Service

### **Basic Usage**
```bash
# Start the RAG assistant (French language)
python services/assistance/rag_assistant.py
```

### **Advanced Options**
```bash
# Specify custom knowledge base document
python services/assistance/rag_assistant.py --doc-path /path/to/your/document.md

# Use different LLM model
python services/assistance/rag_assistant.py --llm-model /path/to/your/model.gguf

# Use different Whisper model
python services/assistance/rag_assistant.py --whisper-model medium
```

### **What to Expect**
```
=== RAG Voice Assistant ===
Bonjour, je suis votre assistant vocal RAG, prêt à vous aider.

Écoute... (Parlez maintenant)
🎤 Transcription temps réel avec détection intelligente du silence

🎧 Listening for speech...
🗣️  SPEAKING [████████████░░░░░░░░░░░░░░░░] 0.234
📝 Transcription: 'Comment résoudre un problème de réseau ?'
Assistant: [Processes your question using RAG knowledge base]
🔄 AI Response: 'Pour résoudre un problème de réseau...'
[Speaks response in French]
```

### **Knowledge Base**
The assistant uses `backup_important_files/doc_resolutions.md` as its knowledge base. You can:
- ✅ Replace with your own documentation
- ✅ Add technical manuals, FAQs, guides
- ✅ Include company policies, procedures

## ⚙️ Configuration Options

### **Voice Sensitivity**
Adjust voice detection for your environment:

```python
from services.translation.translation_service import TranslationService

service = TranslationService('en_to_fr')

# Environment presets
service.set_sensitivity_preset('quiet_room')      # Very sensitive
service.set_sensitivity_preset('normal_room')     # High sensitivity (default)
service.set_sensitivity_preset('office')          # Medium sensitivity  
service.set_sensitivity_preset('cafe_restaurant') # Low sensitivity
service.set_sensitivity_preset('street_outdoor')  # Very low sensitivity

# Manual configuration
service.configure_silence_detection(threshold=0.005, duration=2.0)
```

### **Audio Settings**
Located in `shared/config/audio_config.py`:
```python
RATE = 16000          # Sample rate (Hz)
CHUNK = 1024          # Buffer size
SILENCE_THRESHOLD = 0.005  # Voice detection sensitivity
RECORD_SECONDS = 7    # Maximum recording duration
```

## 🎯 Usage Tips

### **For Best Voice Recognition:**
- ✅ **Speak clearly** at normal conversational volume
- ✅ **Pause briefly** when finished speaking (system auto-detects silence)
- ✅ **Use consistent distance** from microphone
- ✅ **Minimize background noise** when possible

### **Translation Tips:**
- ✅ **Speak naturally** - no need to shout or whisper
- ✅ **Use complete sentences** for better translation accuracy  
- ✅ **Wait for visual feedback** showing recording status
- ✅ **Say "quit", "exit", or "au revoir"** to end session

### **RAG Assistant Tips:**
- ✅ **Ask specific questions** related to your knowledge base
- ✅ **Use French language** for queries
- ✅ **Reference document topics** for better responses
- ✅ **Ask follow-up questions** - the assistant remembers context
- ✅ **Long responses are automatically chunked** for better speech clarity

## 🔧 Troubleshooting

### **Voice Not Detected**
```bash
# Test and adjust sensitivity
python test_sensitivity.py

# Try higher sensitivity preset
service.set_sensitivity_preset('very_high')

# Check microphone permissions and settings
```

### **Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.8+
```

### **Audio Issues**
```bash
# Test audio components
python -c "
from shared.audio.player import AudioPlayer
player = AudioPlayer()
print(f'Pygame available: {player.pygame_available}')
print(f'Winsound available: {player.winsound_available}')
"
```

### **Memory Issues (RAG Assistant)**
- Use smaller LLM model (e.g., smaller .gguf file)
- Close other applications to free RAM
- Use `medium` or `small` Whisper model instead of `large`

### **Translation Errors**
```bash
# Check Argos Translate installation
python -c "import argostranslate; print('Argos Translate OK')"

# Reinstall translation dependencies
pip install -r services/translation/requirements.txt --force-reinstall
```

## 📁 File Structure

```
Voice-and-Translation-Assistant/
├── shared/                        # Shared components
│   ├── audio/                    # Audio processing
│   ├── speech/                   # Speech recognition  
│   ├── tts/                      # Text-to-speech
│   └── resources/                # Models, sounds, executables
├── services/                     # Applications
│   ├── translation/              # Translation service
│   └── assistance/               # RAG assistant
├── backup_important_files/       # LLM models, knowledge base
│   ├── llm_models/               # Local LLM files
│   ├── vectorstore_faiss_md/     # RAG database
│   └── doc_resolutions.md        # Knowledge base document
├── output/                       # Generated audio files
├── logs/                         # Application logs
└── test_*.py                     # Testing tools
```

## 🎪 Demo Commands

### **Quick Demo - Translation**
```bash
# Start English to French translator
python services/translation/translation_service.py --direction en_to_fr

# Say: "Hello, how are you today?"
# Hear: "Bonjour, comment allez-vous aujourd'hui ?"
```

### **Quick Demo - RAG Assistant** 
```bash
# Start French AI assistant
python services/assistance/rag_assistant.py

# Say (in French): "Bonjour, comment ça va ?"
# Hear: AI response in French based on knowledge base
```

## 🆘 Support Commands

### **Full System Test**
```bash
# Test everything
python test_modular.py      # Architecture test
python test_realtime.py     # Voice features test  
python test_sensitivity.py  # Microphone calibration
```

### **Check Installation**
```bash
# Verify all dependencies
python -c "
try:
    import torch, pyaudio, faster_whisper, pygame
    print('✅ Core dependencies OK')
    
    import argostranslate
    print('✅ Translation dependencies OK')
    
    import langchain, faiss
    print('✅ RAG dependencies OK')
    
except ImportError as e:
    print(f'❌ Missing: {e}')
"
```

### **Performance Monitoring**
```bash
# Check system resources
python -c "
from shared.utils.system import SystemUtils
SystemUtils.print_system_info()
"
```

## 🎉 Ready to Go!

Your modular voice assistant is ready to use! Choose your preferred service:

- **🌍 Translation**: Real-time voice translation between English and French
- **🤖 AI Assistant**: Intelligent voice assistant with document knowledge

Both services feature real-time voice detection, professional audio processing, and hands-free operation. Enjoy your enhanced voice assistant experience! 🎊