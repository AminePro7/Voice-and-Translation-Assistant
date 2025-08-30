"""
Setup script for Voice and Translation Assistant modular package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else "Voice and Translation Assistant - Modular Architecture"

# Read requirements
def read_requirements(filename):
    """Read requirements from file"""
    requirements_path = this_directory / filename
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="voice-translation-assistant",
    version="1.0.0",
    author="Voice Assistant Team",
    description="Modular voice assistant with translation and AI assistance capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "translation": read_requirements("services/translation/requirements.txt"),
        "assistance": read_requirements("services/assistance/requirements.txt"),
        "all": (
            read_requirements("services/translation/requirements.txt") +
            read_requirements("services/assistance/requirements.txt")
        ),
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "voice-translator=services.translation.translation_service:main",
            "voice-assistant=services.assistance.rag_assistant:main",
        ]
    },
    package_data={
        "shared": ["models/**/*", "resources/**/*"],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="voice assistant translation speech recognition text-to-speech AI",
    project_urls={
        "Documentation": "https://github.com/yourusername/voice-translation-assistant/wiki",
        "Source": "https://github.com/yourusername/voice-translation-assistant",
        "Tracker": "https://github.com/yourusername/voice-translation-assistant/issues",
    },
)