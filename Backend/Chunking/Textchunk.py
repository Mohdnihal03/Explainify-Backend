# Import NLTK for natural language processing
# NLTK provides the TextTiling algorithm for topic segmentation
import nltk
from nltk.tokenize import TextTilingTokenizer

# Import typing utilities for type hints
from typing import List, Dict

# Import json for saving chunk metadata
import json


class SemanticChunker:
    """
    A class to perform semantic chunking on text using the TextTiling algorithm.
    
    WHY TEXTTILING?
    ---------------
    1. NO LLM REQUIRED: Pure algorithmic approach, no API costs
    2. TOPIC-AWARE: Detects natural topic boundaries in text
    3. PROVEN ALGORITHM: Published research (Hearst, 1997), widely used
    4. FAST: Processes long transcripts in seconds
    5. TRANSCRIPT-OPTIMIZED: Works well with spoken content
    
    HOW TEXTTILING WORKS:
    ---------------------
    1. Divides text into sentence blocks
    2. Calculates word similarity between adjacent blocks
    3. Finds points where similarity drops (topic shift)
    4. Creates chunk boundaries at these points
    
    RESULT: Chunks that represent coherent topics/segments
    """
    
    def __init__(self, w=20, k=10):
        """
        Initialize the SemanticChunker with TextTiling parameters.
        
        Args:
            w (int): Window size - number of sentences to compare (default: 20)
                     - Larger w = fewer, larger chunks
                     - Smaller w = more, smaller chunks
            k (int): Smoothing parameter (default: 10)
                     - Controls sensitivity to topic changes
                     - Higher k = smoother, fewer boundaries
        
        WHY THESE DEFAULTS?
        - w=20: Good balance for YouTube transcripts (2-3 minute segments)
        - k=10: Standard smoothing, avoids over-segmentation
        """
        # Create the TextTiling tokenizer with specified parameters
        self.tokenizer = TextTilingTokenizer(w=w, k=k)
        
        # Store parameters for reference
        self.window_size = w
        self.smoothing = k
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into semantic chunks using TextTiling algorithm.
        
        Args:
            text (str): The input text to chunk (cleaned transcript)
        
        Returns:
            List[str]: List of text chunks, each representing a coherent topic
        
        WHY THIS METHOD?
        - Preserves topic coherence
        - No arbitrary word limits
        - Natural boundaries based on content
        """
        # Check if input is empty
        if not text or len(text.strip()) == 0:
            return []
        
        try:
            # Preprocess text to ensure it has paragraph breaks for TextTiling
            # TextTiling requires \n\n to identify blocks
            structured_text = self._preprocess_for_texttiling(text)
            
            # Use TextTiling to tokenize (chunk) the text
            # This returns a list of text segments
            chunks = self.tokenizer.tokenize(structured_text)
            
            # Post-process chunks to remove the artificial newlines if desired
            # (Optional: depends on if we want to keep the structure)
            # For now, we'll keep them or replace with spaces to match original flow
            chunks = [chunk.replace('\n\n', ' ').strip() for chunk in chunks]
            
            # Return the list of chunks
            return chunks
            
        except Exception as e:
            # If TextTiling fails (e.g., text too short), fall back to simple chunking
            print(f"TextTiling failed: {str(e)}")
            print("Falling back to simple sentence-based chunking")
            
            # Fallback: Split by sentences and group into reasonable chunks
            return self._fallback_chunking(text)

    def _preprocess_for_texttiling(self, text: str, sentences_per_block: int = 5) -> str:
        """
        Preprocess text by inserting paragraph breaks every N sentences.
        TextTiling needs paragraph breaks to function on continuous text.
        
        Args:
            text (str): Continuous text
            sentences_per_block (int): Number of sentences per artificial paragraph
            
        Returns:
            str: Text with \n\n inserted
        """
        # Split into sentences
        sentences = nltk.sent_tokenize(text)
        
        # Group sentences into blocks
        blocks = []
        current_block = []
        
        for i, sentence in enumerate(sentences):
            current_block.append(sentence)
            
            # If block is full, join and add to blocks
            if (i + 1) % sentences_per_block == 0:
                blocks.append(' '.join(current_block))
                current_block = []
        
        # Add remaining sentences
        if current_block:
            blocks.append(' '.join(current_block))
            
        # Join blocks with double newline
        return '\n\n'.join(blocks)
    
    def _fallback_chunking(self, text: str, target_sentences: int = 15, 
                           min_words: int = 100, max_words: int = 300) -> List[str]:
        """
        Fallback chunking method if TextTiling fails.
        Groups sentences into chunks with size constraints for better RAG performance.
        
        Args:
            text (str): The input text
            target_sentences (int): Approximate number of sentences per chunk (default: 15)
            min_words (int): Minimum words per chunk (default: 100)
            max_words (int): Maximum words per chunk (default: 300)
        
        Returns:
            List[str]: List of text chunks with consistent sizing
        
        IMPROVEMENTS:
        - Ensures chunks meet minimum size requirement for context
        - Prevents chunks from becoming too large for retrieval
        - Better quality chunks for RAG systems
        """
        # Split text into sentences using basic punctuation
        sentences = nltk.sent_tokenize(text)
        
        # Group sentences into chunks with size constraints
        chunks = []
        current_chunk = []
        
        for i, sentence in enumerate(sentences):
            # Add sentence to current chunk
            current_chunk.append(sentence)
            chunk_text = ' '.join(current_chunk)
            word_count = len(chunk_text.split())
            
            # Save chunk if it meets size requirements or is the last batch
            if word_count >= min_words and (i == len(sentences) - 1 or word_count >= max_words):
                chunks.append(chunk_text)
                current_chunk = []
            elif (i + 1) % target_sentences == 0 and word_count >= min_words:
                # Also save if target sentences reached and minimum size met
                chunks.append(chunk_text)
                current_chunk = []
        
        # Add remaining sentences as final chunk if large enough
        if current_chunk:
            final_chunk = ' '.join(current_chunk)
            if len(final_chunk.split()) >= min_words or not chunks:
                chunks.append(final_chunk)
            elif chunks:
                # Otherwise merge with last chunk
                chunks[-1] += ' ' + final_chunk
        
        return chunks
    
    
    def chunk_with_overlap(self, text: str, overlap_words: int = 25) -> List[str]:
        """
        Create chunks with overlapping content (sliding window approach).
        This improves RAG performance by maintaining context across chunk boundaries.
        
        Args:
            text (str): The input text to chunk
            overlap_words (int): Number of words to overlap between chunks (default: 25)
        
        Returns:
            List[str]: List of overlapping text chunks
        
        WHY OVERLAP?
        -----------
        - Prevents context loss at chunk boundaries
        - Improves RAG retrieval quality
        - Ensures answers that span multiple chunks are captured
        - Better context for LLM generation
        
        EXAMPLE:
        Without overlap: "...makes predictions." | "ML powers..."
        With overlap:    "...makes predictions. ML powers..." (25 word overlap)
        """
        # First, get the base chunks from TextTiling
        base_chunks = self.chunk_text(text)
        
        if len(base_chunks) <= 1:
            return base_chunks
        
        # Create overlapped chunks using sliding window
        overlapped_chunks = []
        
        for i in range(len(base_chunks)):
            if i == 0:
                # First chunk stays as is
                overlapped_chunks.append(base_chunks[i])
            else:
                # For subsequent chunks, prepend the last N words from previous chunk
                prev_words = base_chunks[i - 1].split()
                current_words = base_chunks[i].split()
                
                # Get overlap from previous chunk (last N words)
                overlap_text = ' '.join(prev_words[-overlap_words:])
                
                # Combine: previous chunk end + current chunk
                combined = overlap_text + ' ' + base_chunks[i]
                overlapped_chunks.append(combined.strip())
        
        return overlapped_chunks
    
    def chunk_with_metadata(self, text: str, video_id: str = None, 
                           transcript_segments: List[Dict] = None,
                           video_title: str = "",
                           use_overlap: bool = True, 
                           overlap_words: int = 25) -> List[Dict]:
        """
        Chunk text and return chunks with metadata for verification and storage.
        
        Args:
            text (str): The input text to chunk
            video_id (str): Optional video ID for tracking
            transcript_segments (List[Dict]): Original transcript segments with timestamps
                Format: [{"text": "...", "start": 0.0, "duration": 2.5}, ...]
            video_title (str): Title of the video for citation display
            use_overlap (bool): Whether to use overlapping chunks (default: True for RAG)
            overlap_words (int): Number of words to overlap (default: 25)
        
        Returns:
            List[Dict]: List of chunk dictionaries with metadata
        
        METADATA INCLUDES:
        - chunk_id: Sequential ID
        - text: The chunk content
        - word_count: Number of words in chunk
        - char_count: Number of characters
        - video_id: Associated video ID
        - video_title: Video title for citations
        - start_time: Start timestamp in seconds (if segments provided)
        - end_time: End timestamp in seconds (if segments provided)
        - has_overlap: Whether this chunk includes overlap from previous
        """
        # Import timestamp mapper for mapping chunks to timestamps
        from timestamp_mapper import TimestampMapper
        
        # Get chunks with or without overlap
        if use_overlap:
            chunks = self.chunk_with_overlap(text, overlap_words=overlap_words)
        else:
            chunks = self.chunk_text(text)
        
        # Create metadata for each chunk
        chunks_with_metadata = []
        
        for i, chunk in enumerate(chunks):
            # Calculate statistics for this chunk
            word_count = len(chunk.split())
            char_count = len(chunk)
            
            # Create metadata dictionary
            chunk_data = {
                "chunk_id": i,
                "text": chunk,
                "word_count": word_count,
                "char_count": char_count,
                "video_id": video_id,
                "video_title": video_title,
                "has_overlap": (i > 0 and use_overlap)  # Track if chunk includes overlap
            }
            
            # Add timestamp data if transcript segments are provided
            if transcript_segments:
                start_time, end_time = TimestampMapper.map_chunk_to_timestamps(
                    chunk, transcript_segments
                )
                chunk_data["start_time"] = start_time
                chunk_data["end_time"] = end_time
            else:
                chunk_data["start_time"] = 0.0
                chunk_data["end_time"] = 0.0
            
            chunks_with_metadata.append(chunk_data)
        
        return chunks_with_metadata

    
    def get_chunking_stats(self, chunks: List[str]) -> Dict:
        """
        Calculate statistics about the chunking results for verification.
        
        Args:
            chunks (List[str]): List of text chunks
        
        Returns:
            Dict: Statistics about the chunks
        
        USE THIS TO VERIFY CHUNKING QUALITY:
        - Check if chunk sizes are reasonable
        - Ensure no chunks are too small or too large
        - Verify total word count matches original
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_words": 0,
                "avg_words_per_chunk": 0,
                "min_words": 0,
                "max_words": 0
            }
        
        # Calculate word counts for each chunk
        word_counts = [len(chunk.split()) for chunk in chunks]
        
        # Calculate statistics
        stats = {
            "total_chunks": len(chunks),
            "total_words": sum(word_counts),
            "avg_words_per_chunk": sum(word_counts) / len(word_counts),
            "min_words": min(word_counts),
            "max_words": max(word_counts),
            "word_counts_per_chunk": word_counts
        }
        
        return stats


# ============================================================================
# VERIFICATION METHODS
# ============================================================================

def verify_chunking(original_text: str, chunks: List[str]) -> Dict:
    """
    Verify that chunking was successful and makes sense.
    
    Args:
        original_text (str): The original text before chunking
        chunks (List[str]): The resulting chunks
    
    Returns:
        Dict: Verification results
    
    VERIFICATION CHECKS:
    1. No data loss: Total words in chunks = words in original
    2. Reasonable chunk sizes: Not too small or too large
    3. No empty chunks
    4. Chunks are coherent (basic check)
    """
    # Count words in original text
    original_word_count = len(original_text.split())
    
    # Count words in all chunks combined
    chunks_word_count = sum(len(chunk.split()) for chunk in chunks)
    
    # Check for empty chunks
    empty_chunks = sum(1 for chunk in chunks if len(chunk.strip()) == 0)
    
    # Calculate chunk size distribution
    word_counts = [len(chunk.split()) for chunk in chunks]
    
    # Verification results
    verification = {
        "passed": True,
        "checks": {
            "no_data_loss": abs(original_word_count - chunks_word_count) < 10,  # Allow small variance
            "no_empty_chunks": empty_chunks == 0,
            "reasonable_sizes": min(word_counts) > 20 and max(word_counts) < 2000,  # Reasonable range
            "total_chunks": len(chunks)
        },
        "stats": {
            "original_words": original_word_count,
            "chunks_words": chunks_word_count,
            "empty_chunks": empty_chunks,
            "min_chunk_size": min(word_counts) if word_counts else 0,
            "max_chunk_size": max(word_counts) if word_counts else 0,
            "avg_chunk_size": sum(word_counts) / len(word_counts) if word_counts else 0
        }
    }
    
    # Overall pass/fail
    verification["passed"] = all(verification["checks"].values())
    
    return verification


def print_chunking_report(chunks: List[str], verification: Dict = None):
    """
    Print a human-readable report of chunking results.
    
    Args:
        chunks (List[str]): The chunks to report on
        verification (Dict): Optional verification results
    
    USE THIS TO:
    - Visually inspect chunking quality
    - Debug issues
    - Show results to users
    """
    print("=" * 80)
    print("CHUNKING REPORT")
    print("=" * 80)
    
    print(f"\nTotal Chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        word_count = len(chunk.split())
        preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
        
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Words: {word_count}")
        print(f"Preview: {preview}")
    
    if verification:
        print("\n" + "=" * 80)
        print("VERIFICATION RESULTS")
        print("=" * 80)
        print(f"Overall: {'✅ PASSED' if verification['passed'] else '❌ FAILED'}")
        print(f"\nChecks:")
        for check, result in verification['checks'].items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {result}")
        print(f"\nStats:")
        for key, value in verification['stats'].items():
            print(f"  {key}: {value}")


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Download required NLTK data (run once)
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK punkt tokenizer...")
        nltk.download('punkt')
    
    # Example transcript
    sample_transcript = """
    Today we're going to talk about Python programming. Python is a high-level 
    programming language that's great for beginners. It has simple syntax and 
    is very readable. Many companies use Python for web development.
    
    Now let's discuss data types in Python. Python has several built-in data types
    including integers, floats, strings, and booleans. Each data type has its own
    characteristics and use cases. Understanding data types is crucial for writing
    effective Python code.
    
    Moving on to functions. Functions are reusable blocks of code that perform
    specific tasks. You define a function using the def keyword. Functions can
    take parameters and return values. They help make your code more organized
    and maintainable.
    """
    
    # Create chunker with optimized parameters for educational content
    chunker = SemanticChunker(w=15, k=8)  # More granular for education videos
    
    # Example 1: Basic chunking without overlap
    print("=" * 80)
    print("EXAMPLE 1: Basic Chunking (No Overlap)")
    print("=" * 80)
    chunks = chunker.chunk_text(sample_transcript)
    verification = verify_chunking(sample_transcript, chunks)
    print_chunking_report(chunks, verification)
    
    # Example 2: Chunking with overlap for RAG systems
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Chunking with Overlap (Recommended for RAG)")
    print("=" * 80)
    overlapped_chunks = chunker.chunk_with_overlap(sample_transcript, overlap_words=25)
    print(f"Total Overlapped Chunks: {len(overlapped_chunks)}\n")
    for i, chunk in enumerate(overlapped_chunks):
        word_count = len(chunk.split())
        preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
        overlap_marker = "🔄 [OVERLAP]" if i > 0 else "🆕 [FIRST]"
        print(f"--- Chunk {i + 1} {overlap_marker} ---")
        print(f"Words: {word_count}")
        print(f"Preview: {preview}\n")
    
    # Example 3: Chunks with metadata and overlap
    print("=" * 80)
    print("EXAMPLE 3: Chunks with Metadata (For Vector Storage)")
    print("=" * 80)
    chunks_with_meta = chunker.chunk_with_metadata(
        sample_transcript, 
        video_id="demo_video_123",
        use_overlap=True,
        overlap_words=25
    )
    for chunk_data in chunks_with_meta:
        print(f"Chunk {chunk_data['chunk_id']}: {chunk_data['word_count']} words " +
              f"(Overlap: {chunk_data['has_overlap']})")
        print(f"  Preview: {chunk_data['text'][:80]}...\n")
