# Import the YouTubeTranscriptApi class from the youtube_transcript_api library
# This library allows us to fetch transcripts/captions from YouTube videos
from youtube_transcript_api import YouTubeTranscriptApi

# Import the re module for regular expression operations
# We'll use this to extract video IDs from YouTube URLs
import re

# Import typing utilities for type hints
# This improves code readability and helps with IDE autocomplete
from typing import Optional, List, Dict


class YouTubeTranscriptFetcher:
    """
    A class to handle fetching and processing YouTube video transcripts.
    This class provides methods to extract video IDs from URLs and retrieve transcripts.
    """
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract the video ID from a YouTube URL.
        
        Args:
            url (str): The YouTube URL (supports various formats like youtube.com/watch?v=, youtu.be/, etc.)
        
        Returns:
            Optional[str]: The extracted video ID if found, None otherwise
        """
        # Define a regular expression pattern to match YouTube video IDs
        # This pattern handles multiple YouTube URL formats:
        # - youtube.com/watch?v=VIDEO_ID
        # - youtu.be/VIDEO_ID
        # - youtube.com/embed/VIDEO_ID
        # - youtube.com/v/VIDEO_ID
        pattern = r'(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        
        # Search for the pattern in the provided URL
        match = re.search(pattern, url)
        
        # If a match is found, return the first captured group (the video ID)
        # Otherwise, return None
        return match.group(1) if match else None
    
    @staticmethod
    def get_transcript(video_id: str, languages: List[str] = ['en']) -> Optional[List[Dict]]:
        """
        Fetch the transcript for a given YouTube video ID.
        
        Args:
            video_id (str): The YouTube video ID (11 characters)
            languages (List[str]): List of preferred language codes (default: ['en'] for English)
        
        Returns:
            Optional[List[Dict]]: A list of transcript segments, each containing 'text', 'start', and 'duration'
                                  Returns None if transcript cannot be fetched
        """
        try:
            # Create an instance of YouTubeTranscriptApi
            ytt_api = YouTubeTranscriptApi()
            
            # Use the fetch method to get the transcript
            # This returns a FetchedTranscript object
            fetched_transcript = ytt_api.fetch(video_id, languages=languages)
            
            # Convert the FetchedTranscript object to raw data (list of dictionaries)
            # Each dictionary contains 'text', 'start', and 'duration' keys
            transcript_data = fetched_transcript.to_raw_data()
            
            # Return the transcript data
            return transcript_data
            
        except Exception as e:
            # If any error occurs (video not found, no transcript available, etc.)
            # Print the error message for debugging purposes
            print(f"Error fetching transcript: {str(e)}")
            
            # Return None to indicate failure
            return None
    
    @staticmethod
    def format_transcript(transcript_data: List[Dict]) -> str:
        """
        Format the transcript data into a single readable text string.
        
        Args:
            transcript_data (List[Dict]): Raw transcript data from YouTube
        
        Returns:
            str: A formatted string containing all transcript text concatenated together
        """
        # Check if transcript_data is None or empty
        if not transcript_data:
            # Return an empty string if no data is available
            return ""
        
        # Extract the 'text' field from each transcript segment
        # Join all text segments with a space separator to create a continuous text
        formatted_text = " ".join([segment['text'] for segment in transcript_data])
        
        # Return the formatted transcript text
        return formatted_text
    
    @classmethod
    def get_transcript_from_url(cls, url: str, languages: List[str] = ['en']) -> Optional[str]:
        """
        Convenience method to get a formatted transcript directly from a YouTube URL.
        
        Args:
            url (str): The YouTube video URL
            languages (List[str]): List of preferred language codes (default: ['en'])
        
        Returns:
            Optional[str]: The formatted transcript text, or None if unable to fetch
        """
        # Step 1: Extract the video ID from the URL
        video_id = cls.extract_video_id(url)
        
        # If video ID extraction failed, return None
        if not video_id:
            print("Invalid YouTube URL: Could not extract video ID")
            return None
        
        # Step 2: Fetch the raw transcript data using the video ID
        transcript_data = cls.get_transcript(video_id, languages)
        
        # If transcript fetching failed, return None
        if not transcript_data:
            return None
        
        # Step 3: Format the transcript data into a readable string
        formatted_transcript = cls.format_transcript(transcript_data)
        
        # Return the formatted transcript
        return formatted_transcript


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create an instance of the YouTubeTranscriptFetcher class
    fetcher = YouTubeTranscriptFetcher()
    
    # Example YouTube URL (replace with an actual video URL for testing)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Fetch and print the transcript
    transcript = fetcher.get_transcript_from_url(test_url)
    
    # Check if transcript was successfully fetched
    if transcript:
        # Print the first 500 characters of the transcript
        print("Transcript Preview:")
        print(transcript[:500])
    else:
        # Print error message if transcript couldn't be fetched
        print("Failed to fetch transcript")
