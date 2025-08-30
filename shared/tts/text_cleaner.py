"""
Text cleaning utilities for TTS to remove markdown and formatting
"""

import re

class TTSTextCleaner:
    """Clean text for better TTS pronunciation"""
    
    @staticmethod
    def clean_for_tts(text):
        """
        Clean text to make it suitable for TTS by removing markdown formatting
        
        Args:
            text: Raw text with potential markdown formatting
            
        Returns:
            Clean text suitable for speech synthesis
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove "Human: Question:" prefix if present
        text = re.sub(r'^Human:\s*Question:\s*', '', text, flags=re.IGNORECASE)
        
        # Remove markdown headers (### ** etc.)
        text = re.sub(r'#{1,6}\s*', '', text)  # Remove ### headers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *italic* -> italic
        
        # Remove list formatting
        text = re.sub(r'^\s*\d+\.\s*\*\*([^*]+)\*\*\s*:\s*', r'\1: ', text, flags=re.MULTILINE)  # 3. **Result:** -> Result:
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)  # Remove numbered lists
        text = re.sub(r'^\s*[-*+]\s*', '', text, flags=re.MULTILINE)  # Remove bullet points
        
        # Clean up bullet points and asterisks
        text = re.sub(r'^\s*\*\s*', '', text, flags=re.MULTILINE)  # Remove * at line start
        text = re.sub(r'\*', '', text)  # Remove remaining asterisks
        
        # Remove excessive whitespace and newlines
        text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines with space
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        
        # Remove parenthetical notes that are too technical for speech
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Clean up common formatting artifacts
        text = re.sub(r':\s*$', '.', text)  # Replace trailing colons with periods
        text = re.sub(r'\.+', '.', text)  # Replace multiple periods with single period
        
        # Ensure sentences end properly
        text = text.strip()
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text.strip()
    
    @staticmethod
    def extract_main_content(text):
        """
        Extract the main response content, removing metadata and formatting
        
        Args:
            text: Response text that may contain question echoes and formatting
            
        Returns:
            Main content suitable for TTS
        """
        if not text:
            return ""
        
        # Split by common separators and take the substantial part
        lines = text.split('\n')
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that are just question echoes
            if line.startswith('Human:') or line.startswith('Question:'):
                continue
                
            # Skip lines that are just numbers or formatting
            if re.match(r'^\d+\.\s*$', line):
                continue
                
            content_lines.append(line)
        
        # Join the content and clean it
        main_content = ' '.join(content_lines)
        return TTSTextCleaner.clean_for_tts(main_content)
    
    @staticmethod
    def format_for_speech(text, max_length=200):
        """
        Format text for natural speech, breaking long responses into chunks
        
        Args:
            text: Text to format
            max_length: Maximum length for comfortable speech
            
        Returns:
            List of text chunks suitable for TTS
        """
        cleaned_text = TTSTextCleaner.extract_main_content(text)
        
        if len(cleaned_text) <= max_length:
            return [cleaned_text] if cleaned_text else []
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', cleaned_text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed max_length, start new chunk
            if current_chunk and len(current_chunk + " " + sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip() + ".")
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip() + ".")
        
        return chunks