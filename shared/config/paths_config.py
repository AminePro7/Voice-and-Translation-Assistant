"""
Path configuration management for shared resources
"""

from pathlib import Path

class PathConfig:
    def __init__(self, root_dir=None):
        """Initialize path configuration with project root"""
        if root_dir is None:
            # Auto-detect project root (where this package is located)
            self.root_dir = Path(__file__).parent.parent.parent
        else:
            self.root_dir = Path(root_dir)
        
        # Define shared resource directories
        self.shared_dir = self.root_dir / "shared"
        self.models_dir = self.shared_dir / "models"
        self.resources_dir = self.shared_dir / "resources"
        
        # Specific resource subdirectories
        self.tts_models_dir = self.models_dir / "tts"
        self.whisper_models_dir = self.models_dir / "whisper"
        self.piper_dir = self.resources_dir / "piper"
        self.sounds_dir = self.resources_dir / "sounds"
        
        # Output and temporary directories
        self.output_dir = self.root_dir / "output"
        self.logs_dir = self.root_dir / "logs"
        
        # Service directories
        self.services_dir = self.root_dir / "services"
        self.translation_service_dir = self.services_dir / "translation"
        self.assistance_service_dir = self.services_dir / "assistance"
    
    def create_directories(self):
        """Create all necessary directories"""
        directories = [
            self.models_dir,
            self.resources_dir,
            self.tts_models_dir,
            self.whisper_models_dir,
            self.piper_dir,
            self.sounds_dir,
            self.output_dir,
            self.logs_dir,
            self.services_dir,
            self.translation_service_dir,
            self.assistance_service_dir
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                print(f"✓ Directory ready: {directory}")
            except Exception as e:
                print(f"✗ Failed to create directory {directory}: {e}")
    
    def validate_essential_paths(self):
        """Validate that essential directories exist"""
        essential_dirs = [
            (self.shared_dir, "Shared modules directory"),
            (self.models_dir, "Models directory"),
            (self.resources_dir, "Resources directory")
        ]
        
        missing_paths = []
        for path, description in essential_dirs:
            if not path.exists():
                missing_paths.append((path, description))
        
        if missing_paths:
            print("Missing essential directories:")
            for path, desc in missing_paths:
                print(f"  - {desc}: {path}")
            return False
        
        return True
    
    def get_temp_dir(self, service_name=None):
        """Get temporary directory path for a service"""
        import tempfile
        
        if service_name:
            prefix = f'voice_assistant_{service_name}_'
        else:
            prefix = 'voice_assistant_'
        
        temp_path = Path(tempfile.mkdtemp(prefix=prefix))
        return temp_path
    
    def get_all_paths(self):
        """Get dictionary of all configured paths"""
        return {
            'root_dir': self.root_dir,
            'shared_dir': self.shared_dir,
            'models_dir': self.models_dir,
            'resources_dir': self.resources_dir,
            'tts_models_dir': self.tts_models_dir,
            'whisper_models_dir': self.whisper_models_dir,
            'piper_dir': self.piper_dir,
            'sounds_dir': self.sounds_dir,
            'output_dir': self.output_dir,
            'logs_dir': self.logs_dir,
            'services_dir': self.services_dir,
            'translation_service_dir': self.translation_service_dir,
            'assistance_service_dir': self.assistance_service_dir
        }