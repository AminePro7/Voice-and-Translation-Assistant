"""
Text processing utilities for speech recognition output
"""

import re
from ..config.speech_config import TEXT_CLEANUP_PATTERNS

class TextProcessor:
    @staticmethod
    def clean_text(text):
        """
        Clean and normalize text output from speech recognition
        
        Args:
            text: Raw text from speech recognition
        
        Returns:
            Cleaned text string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Apply cleanup patterns
        cleaned_text = text
        
        # Remove excessive whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Remove non-printable characters (keep basic punctuation)
        cleaned_text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\'\"]', '', cleaned_text)
        
        # Remove leading/trailing whitespace
        cleaned_text = cleaned_text.strip()
        
        return cleaned_text
    
    @staticmethod
    def extract_keywords(text, min_length=3):
        """
        Extract keywords from text
        
        Args:
            text: Input text
            min_length: Minimum word length to consider
        
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        # Split into words and filter
        words = text.lower().split()
        keywords = []
        
        for word in words:
            # Remove punctuation and check length
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) >= min_length:
                keywords.append(clean_word)
        
        return keywords
    
    @staticmethod
    def is_empty_or_nonsense(text, min_length=2):
        """
        Check if text is empty or appears to be nonsense
        
        Args:
            text: Input text to check
            min_length: Minimum meaningful length
        
        Returns:
            True if text appears empty or nonsensical
        """
        if not text or not isinstance(text, str):
            return True
        
        cleaned = TextProcessor.clean_text(text)
        
        # Check if text is too short
        if len(cleaned) < min_length:
            return True
        
        # Check if text contains actual words
        words = cleaned.split()
        if len(words) == 0:
            return True
        
        # Check for common nonsense patterns
        nonsense_patterns = [
            r'^[a-z]\s*$',  # Single letter
            r'^[.,!?]+$',   # Only punctuation
            r'^\d+$',       # Only numbers
        ]
        
        for pattern in nonsense_patterns:
            if re.match(pattern, cleaned.lower()):
                return True
        
        return False
    
    @staticmethod
    def format_transcription(text, capitalize_first=True):
        """
        Format transcription text for display or further processing
        
        Args:
            text: Input text
            capitalize_first: Whether to capitalize first letter
        
        Returns:
            Formatted text
        """
        if not text:
            return ""
        
        cleaned = TextProcessor.clean_text(text)
        
        if capitalize_first and cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned
    
    @staticmethod
    def split_sentences(text):
        """
        Split text into sentences
        
        Args:
            text: Input text
        
        Returns:
            List of sentences
        """
        if not text:
            return []
        
        # Simple sentence splitting on common punctuation
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter empty sentences
        cleaned_sentences = []
        for sentence in sentences:
            cleaned = sentence.strip()
            if cleaned:
                cleaned_sentences.append(cleaned)
        
        return cleaned_sentences