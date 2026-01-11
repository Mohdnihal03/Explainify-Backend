"""
Timestamp Mapper Module

Maps text chunks back to original video timestamps for citation attribution.
Provides utilities for timestamp formatting and range calculation.
"""

from typing import List, Dict, Tuple, Optional


class TimestampMapper:
    """
    Maps text chunks back to original video timestamps.
    Handles overlapping chunks and provides formatted timestamp ranges.
    """
    
    @staticmethod
    def map_chunk_to_timestamps(
        chunk_text: str,
        transcript_segments: List[Dict],
        tolerance: int = 50
    ) -> Tuple[float, float]:
        """
        Find the start and end timestamps for a chunk by matching it to transcript segments.
        
        Args:
            chunk_text (str): The chunk text to locate
            transcript_segments (List[Dict]): Original transcript with timestamps
                Format: [{"text": "...", "start": 0.0, "duration": 2.5}, ...]
            tolerance (int): Number of characters to use for fuzzy matching
            
        Returns:
            Tuple[float, float]: (start_time, end_time) in seconds
        """
        if not transcript_segments or not chunk_text:
            return (0.0, 0.0)
        
        # Clean the chunk text for comparison
        chunk_clean = chunk_text.strip().lower()
        
        # Try to find where this chunk starts in the transcript
        start_time = None
        end_time = None
        
        # Build a continuous text from segments to find the chunk position
        full_text = " ".join([seg['text'] for seg in transcript_segments]).lower()
        
        # Find the chunk in the full text
        chunk_start_pos = full_text.find(chunk_clean[:tolerance])
        
        if chunk_start_pos == -1:
            # If exact match not found, use first and last segments as fallback
            start_time = transcript_segments[0]['start']
            last_seg = transcript_segments[-1]
            end_time = last_seg['start'] + last_seg['duration']
            return (start_time, end_time)
        
        # Calculate character positions for each segment
        current_pos = 0
        for i, segment in enumerate(transcript_segments):
            segment_text = segment['text'].lower()
            segment_start_pos = current_pos
            segment_end_pos = current_pos + len(segment_text) + 1  # +1 for space
            
            # Check if chunk starts in this segment
            if start_time is None and segment_start_pos <= chunk_start_pos < segment_end_pos:
                start_time = segment['start']
            
            # Check if chunk ends in this segment
            chunk_end_pos = chunk_start_pos + len(chunk_clean)
            if start_time is not None and segment_start_pos <= chunk_end_pos <= segment_end_pos:
                end_time = segment['start'] + segment['duration']
                break
            
            current_pos = segment_end_pos
        
        # If we found start but not end, use the last segment
        if start_time is not None and end_time is None:
            last_seg = transcript_segments[-1]
            end_time = last_seg['start'] + last_seg['duration']
        
        # Fallback if nothing found
        if start_time is None:
            start_time = transcript_segments[0]['start']
            last_seg = transcript_segments[-1]
            end_time = last_seg['start'] + last_seg['duration']
        
        return (start_time, end_time)
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """
        Convert seconds to MM:SS format.
        
        Args:
            seconds (float): Time in seconds
            
        Returns:
            str: Formatted timestamp (e.g., "02:14")
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def format_range(start: float, end: float) -> str:
        """
        Format timestamp range for display.
        
        Args:
            start (float): Start time in seconds
            end (float): End time in seconds
            
        Returns:
            str: Formatted range (e.g., "02:14 – 03:05")
        """
        return f"{TimestampMapper.format_timestamp(start)} – {TimestampMapper.format_timestamp(end)}"
    
    @staticmethod
    def get_chunk_timestamps(
        chunk_data: Dict,
        all_segments: Dict[str, List[Dict]]
    ) -> Optional[Tuple[float, float]]:
        """
        Get timestamps for a chunk using stored metadata or by mapping.
        
        Args:
            chunk_data (Dict): Chunk with metadata (may include start_time, end_time)
            all_segments (Dict[str, List[Dict]]): Mapping of video_id to transcript segments
            
        Returns:
            Optional[Tuple[float, float]]: (start_time, end_time) or None
        """
        # Check if timestamps are already in metadata
        if 'start_time' in chunk_data and 'end_time' in chunk_data:
            return (chunk_data['start_time'], chunk_data['end_time'])
        
        # Otherwise, try to map from text
        video_id = chunk_data.get('video_id')
        if video_id and video_id in all_segments:
            chunk_text = chunk_data.get('text', '')
            return TimestampMapper.map_chunk_to_timestamps(
                chunk_text,
                all_segments[video_id]
            )
        
        return None


# Example usage
if __name__ == "__main__":
    # Sample transcript segments
    segments = [
        {"text": "Hello everyone", "start": 0.0, "duration": 2.0},
        {"text": "Today we'll learn about Python", "start": 2.0, "duration": 3.0},
        {"text": "Python is a programming language", "start": 5.0, "duration": 3.5},
    ]
    
    # Sample chunk
    chunk = "Today we'll learn about Python Python is a programming language"
    
    # Map to timestamps
    start, end = TimestampMapper.map_chunk_to_timestamps(chunk, segments)
    print(f"Chunk timestamp: {TimestampMapper.format_range(start, end)}")
    print(f"Start: {start}s, End: {end}s")
