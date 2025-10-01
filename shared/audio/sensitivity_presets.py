"""
Voice detection sensitivity presets for different environments and voice levels
"""

# Predefined sensitivity configurations
SENSITIVITY_PRESETS = {
    'ultra_sensitive': {
        'threshold': 0.0005,
        'duration': 1.0,
        'min_recording': 0.2,
        'description': 'Ultra-sensitive for very quiet speech without shouting'
    },
    'very_high': {
        'threshold': 0.002,
        'duration': 1.5,
        'min_recording': 0.3,
        'description': 'For whispers and very quiet speech'
    },
    'high': {
        'threshold': 0.005,
        'duration': 2.0,
        'min_recording': 0.5,
        'description': 'For quiet/normal speech (recommended)'
    },
    'medium': {
        'threshold': 0.01,
        'duration': 2.0,
        'min_recording': 0.5,
        'description': 'For normal to loud speech'
    },
    'low': {
        'threshold': 0.02,
        'duration': 2.5,
        'min_recording': 0.7,
        'description': 'For loud speech in noisy environments'
    },
    'very_low': {
        'threshold': 0.05,
        'duration': 3.0,
        'min_recording': 1.0,
        'description': 'For very loud speech or very noisy environments'
    }
}

# Environment-specific presets
ENVIRONMENT_PRESETS = {
    'quiet_room': 'very_high',
    'normal_room': 'high', 
    'office': 'medium',
    'cafe_restaurant': 'low',
    'street_outdoor': 'very_low'
}

def get_sensitivity_config(preset_name):
    """
    Get sensitivity configuration by preset name
    
    Args:
        preset_name: Name of the preset or environment
    
    Returns:
        Dictionary with threshold, duration, and min_recording values
    """
    # Check if it's an environment preset first
    if preset_name in ENVIRONMENT_PRESETS:
        preset_name = ENVIRONMENT_PRESETS[preset_name]
    
    if preset_name in SENSITIVITY_PRESETS:
        return SENSITIVITY_PRESETS[preset_name].copy()
    else:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(SENSITIVITY_PRESETS.keys())}")

def list_presets():
    """List all available sensitivity presets with descriptions"""
    print("Available Sensitivity Presets:")
    print("=" * 50)
    for name, config in SENSITIVITY_PRESETS.items():
        print(f"{name:12} - {config['description']}")
        print(f"             (threshold={config['threshold']}, duration={config['duration']}s)")
    
    print("\nEnvironment Presets:")
    print("=" * 30)
    for env, preset in ENVIRONMENT_PRESETS.items():
        preset_desc = SENSITIVITY_PRESETS[preset]['description']
        print(f"{env:15} -> {preset} ({preset_desc})")

def auto_configure_sensitivity(recorder, preset_name):
    """
    Auto-configure a recorder with a sensitivity preset
    
    Args:
        recorder: RealTimeRecorder instance
        preset_name: Preset name to apply
    """
    config = get_sensitivity_config(preset_name)
    
    recorder.silence_threshold = config['threshold']
    recorder.silence_duration = config['duration'] 
    recorder.min_recording_time = config['min_recording']
    
    print(f"Applied '{preset_name}' sensitivity preset:")
    print(f"  - Threshold: {config['threshold']}")
    print(f"  - Duration: {config['duration']}s") 
    print(f"  - Min recording: {config['min_recording']}s")
    print(f"  - Description: {config['description']}")
    
    return config