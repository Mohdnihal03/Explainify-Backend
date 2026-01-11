# Import the re module for regular expression operations
# Used for pattern matching and text replacement
import re

# Import typing utilities for type hints
from typing import List, Set


class TranscriptCleaner:
    """
    A class to clean and optimize YouTube transcripts.
    Removes filler words, extra spaces, repeated words, and fixes broken sentences.
    """
    
    # Define a set of common filler words and sounds to remove
    # These are words that don't add meaning to the transcript
    FILLER_WORDS: Set[str] = {
        'uh', 'um', 'uhm', 'hmm', 'hm', 'ah', 'eh', 'er', 'like',
        'you know', 'i mean', 'sort of', 'kind of', 'basically',
        'actually', 'literally', 'right', 'okay', 'ok', 'yeah', 'yep',
        'nah', 'mhm', 'uh-huh', 'mm-hmm'
    }
    
    @staticmethod
    def remove_extra_spaces(text: str) -> str:
        """
        Remove extra spaces from the text.
        
        Args:
            text (str): The input text with potential extra spaces
        
        Returns:
            str: Text with normalized spacing
        """
        # Replace multiple spaces with a single space
        # \s+ matches one or more whitespace characters
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading and trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def remove_filler_words(text: str) -> str:
        """
        Remove common filler words and sounds from the text.
        
        Args:
            text (str): The input text containing filler words
        
        Returns:
            str: Text with filler words removed
        """
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Split the text into words
        words = text_lower.split()
        
        # Filter out filler words
        # Keep only words that are not in the FILLER_WORDS set
        cleaned_words = [
            word for word in words 
            if word.strip('.,!?;:') not in TranscriptCleaner.FILLER_WORDS
        ]
        
        # Join the cleaned words back into a string
        cleaned_text = ' '.join(cleaned_words)
        
        return cleaned_text
    
    @staticmethod
    def remove_repeated_words(text: str) -> str:
        """
        Remove consecutive repeated words from the text.
        Example: "the the cat" -> "the cat"
        
        Args:
            text (str): The input text with potential repeated words
        
        Returns:
            str: Text with consecutive repeated words removed
        """
        # Regular expression pattern to match repeated words
        # \b(\w+)\s+\1\b matches a word followed by the same word
        # \b = word boundary
        # (\w+) = capture group for one or more word characters
        # \s+ = one or more whitespace characters
        # \1 = backreference to the first capture group (the repeated word)
        pattern = r'\b(\w+)\s+\1\b'
        
        # Keep replacing repeated words until no more are found
        # This handles cases like "the the the cat" -> "the cat"
        while re.search(pattern, text, re.IGNORECASE):
            # Replace the repeated word with a single occurrence
            text = re.sub(pattern, r'\1', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def fix_broken_sentences(text: str) -> str:
        """
        Fix broken sentence lines and improve sentence structure.
        
        Args:
            text (str): The input text with broken sentences
        
        Returns:
            str: Text with improved sentence structure
        """
        # Remove line breaks and replace with spaces
        # YouTube transcripts often have unnecessary line breaks
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Fix spacing around punctuation
        # Remove space before punctuation marks
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Add space after punctuation if missing
        # (?<=[.,!?;:]) = positive lookback for punctuation
        # (?=[^\s]) = positive lookahead for non-whitespace
        text = re.sub(r'(?<=[.,!?;:])(?=[^\s])', ' ', text)
        
        # Capitalize first letter after sentence-ending punctuation
        # This makes the text more readable
        def capitalize_after_period(match):
            # Get the matched text
            matched = match.group(0)
            # Return punctuation + space + capitalized letter
            return matched[:-1] + matched[-1].upper()
        
        # Pattern: period/question mark/exclamation + space + lowercase letter
        text = re.sub(r'[.!?]\s+[a-z]', capitalize_after_period, text)
        
        # Capitalize the first letter of the entire text
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    @staticmethod
    def remove_special_characters(text: str) -> str:
        """
        Remove or replace special characters that don't add value.
        
        Args:
            text (str): The input text with special characters
        
        Returns:
            str: Text with special characters cleaned
        """
        # Remove brackets and their contents (often metadata)
        # Example: "[Music]" or "[Applause]"
        text = re.sub(r'\[.*?\]', '', text)
        
        # Remove parentheses and their contents if they contain non-word characters
        # Example: "(background noise)"
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Remove multiple punctuation marks
        # Example: "!!!" -> "!"
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        
        return text
    
    @classmethod
    def clean_transcript(cls, text: str) -> str:
        """
        Main method to clean a transcript using all cleaning steps.
        This applies all cleaning operations in the correct order.
        
        Args:
            text (str): The raw transcript text
        
        Returns:
            str: The cleaned and optimized transcript
        """
        # Check if input is empty
        if not text:
            return ""
        
        # Step 1: Remove special characters and metadata
        text = cls.remove_special_characters(text)
        
        # Step 2: Remove filler words
        text = cls.remove_filler_words(text)
        
        # Step 3: Remove repeated words
        text = cls.remove_repeated_words(text)
        
        # Step 4: Fix broken sentences
        text = cls.fix_broken_sentences(text)
        
        # Step 5: Remove extra spaces (final cleanup)
        text = cls.remove_extra_spaces(text)
        
        return text


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Example raw transcript with common issues
    raw_transcript = """
    [Music] Um, so, uh, today we're we're gonna talk about, you know, 
    Python programming. Like, it's it's really really important to 
    understand the the basics.Okay?Yeah.
    """
    
    # Create a cleaner instance
    cleaner = TranscriptCleaner()
    
    # Clean the transcript
    cleaned = cleaner.clean_transcript(raw_transcript)
    
    # Print results
    print("Raw Transcript:")
    print(raw_transcript)
    print("\nCleaned Transcript:")
    print(cleaned)
