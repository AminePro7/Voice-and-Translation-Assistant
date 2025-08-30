"""
System utilities and device detection
"""

import sys
import platform
import torch

class SystemUtils:
    @staticmethod
    def get_platform_info():
        """Get detailed platform information"""
        return {
            'system': platform.system(),
            'platform': platform.platform(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'python_executable': sys.executable
        }
    
    @staticmethod
    def is_windows():
        """Check if running on Windows"""
        return platform.system().lower() == 'windows'
    
    @staticmethod
    def is_linux():
        """Check if running on Linux"""
        return platform.system().lower() == 'linux'
    
    @staticmethod
    def is_macos():
        """Check if running on macOS"""
        return platform.system().lower() == 'darwin'
    
    @staticmethod
    def is_cuda_available():
        """Check if CUDA is available for GPU acceleration"""
        try:
            return torch.cuda.is_available()
        except:
            return False
    
    @staticmethod
    def get_cuda_info():
        """Get CUDA device information"""
        if not SystemUtils.is_cuda_available():
            return {"cuda_available": False}
        
        try:
            return {
                "cuda_available": True,
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "device_name": torch.cuda.get_device_name(),
                "memory_allocated": torch.cuda.memory_allocated(),
                "memory_cached": torch.cuda.memory_reserved()
            }
        except Exception as e:
            return {"cuda_available": True, "error": str(e)}
    
    @staticmethod
    def get_optimal_device():
        """Get the optimal computing device (cuda/cpu)"""
        return "cuda" if SystemUtils.is_cuda_available() else "cpu"
    
    @staticmethod
    def print_system_info():
        """Print comprehensive system information"""
        print("=== System Information ===")
        
        platform_info = SystemUtils.get_platform_info()
        for key, value in platform_info.items():
            print(f"{key}: {value}")
        
        print(f"\n=== Device Information ===")
        cuda_info = SystemUtils.get_cuda_info()
        for key, value in cuda_info.items():
            print(f"{key}: {value}")
        
        print(f"Optimal device: {SystemUtils.get_optimal_device()}")
        print("=" * 30)