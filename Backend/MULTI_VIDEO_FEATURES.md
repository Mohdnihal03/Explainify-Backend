# Multi-Video Querying + Timestamp Attribution

## Overview

This document describes the enhanced features added to Explainify that enable **multi-video querying** and **timestamp attribution** for citations. These features significantly improve the credibility and usability of the Q&A system by providing precise source references with video timestamps.

## Key Features

### 1. Multi-Video Querying
Search across multiple videos simultaneously to find answers from your entire video knowledge base.

**Benefits:**
- Get comprehensive answers that synthesize information from multiple sources
- No need to specify which video contains the answer
- Automatic relevance ranking across all videos

### 2. Timestamp Attribution
Every answer includes precise timestamps linking back to the source video segments.

**Benefits:**
- Increases credibility with verifiable sources
- Enables "jump to video" functionality
- Users can verify answers by watching the exact moment
- Multiple timestamp references per answer

## Architecture

### Data Flow

```
YouTube URL → Transcript with Timestamps → Cleaned Text + Segments
                                                    ↓
                                    Semantic Chunking with Timestamp Mapping
                                                    ↓
                                    Vector Store (with timestamp metadata)
                                                    ↓
                            User Question → Multi-Video Search
                                                    ↓
                            Answer Generation + Citation Building
                                                    ↓
                            Response with Timestamps & Sources
```

## Components

### 1. Enhanced Transcript Fetching
**File:** `youtube_transcript.py`

**New Method:** `get_transcript_with_timestamps()`
- Preserves original timestamp data from YouTube
- Returns structured data: `{text, segments, video_id}`
- Each segment includes: `{text, start, duration}`

**Example:**
```python
fetcher = YouTubeTranscriptFetcher()
data = fetcher.get_transcript_with_timestamps(url)
# Returns: {
#   'text': 'Full transcript...',
#   'segments': [{'text': '...', 'start': 0.0, 'duration': 2.5}, ...],
#   'video_id': 'abc123'
# }
```

### 2. Timestamp Mapping
**File:** `timestamp_mapper.py`

**Purpose:** Maps text chunks back to original video timestamps

**Key Methods:**
- `map_chunk_to_timestamps()` - Finds start/end times for a chunk
- `format_timestamp()` - Converts seconds to MM:SS format
- `format_range()` - Creates formatted ranges (e.g., "02:14 – 03:05")

**Example:**
```python
from timestamp_mapper import TimestampMapper

start, end = TimestampMapper.map_chunk_to_timestamps(
    chunk_text="Python is a programming language",
    transcript_segments=segments
)
# Returns: (5.0, 8.5)

formatted = TimestampMapper.format_range(start, end)
# Returns: "00:05 – 00:08"
```

### 3. Enhanced Chunking
**File:** `Chunking/Textchunk.py`

**Updated Method:** `chunk_with_metadata()`

**New Parameters:**
- `transcript_segments` - Original segments with timestamps
- `video_title` - Video title for citation display

**Output:** Each chunk now includes:
```python
{
    'chunk_id': 0,
    'text': 'chunk content...',
    'video_id': 'abc123',
    'video_title': 'Python Tutorial',
    'start_time': 5.0,      # NEW
    'end_time': 8.5,        # NEW
    'word_count': 150,
    'has_overlap': False
}
```

### 4. Enhanced Vector Storage
**File:** `Embedding/vector_store.py`

**Updated Metadata Schema:**
```python
{
    'video_id': 'abc123',
    'chunk_id': 0,
    'word_count': 150,
    'start_time': 5.0,      # NEW
    'end_time': 8.5,        # NEW
    'video_title': 'Python Tutorial'  # NEW
}
```

**New Method:** `search_multi_video()`
- Searches across all videos or a specified list
- Returns results ranked by relevance
- Supports filtering by video IDs

**Example:**
```python
# Search across all videos
results = vector_store.search_multi_video(
    query="How to handle errors?",
    n_results=5
)

# Search specific videos
results = vector_store.search_multi_video(
    query="How to handle errors?",
    n_results=5,
    video_ids=['abc123', 'def456']
)
```

### 5. Enhanced Response Models
**File:** `main.py`

**New Pydantic Models:**

```python
class TimestampRange(BaseModel):
    start: float
    end: float
    formatted: str  # "02:14 – 03:05"

class Citation(BaseModel):
    video_id: str
    video_title: str
    text: str
    timestamp_range: TimestampRange
    relevance_score: float

class EnhancedAnswerResponse(BaseModel):
    success: bool
    answer: str
    citations: List[Citation]
    error: Optional[str]
```

### 6. Enhanced Ask Endpoint
**File:** `enhanced_ask.py`

**Endpoint:** `POST /ask/enhanced`

**Features:**
- Multi-video search when `video_id` is None
- Single video search when `video_id` is specified
- Automatic citation building with timestamps
- Relevance scoring for each citation

## API Usage

### 1. Upload Multiple Videos

```bash
# Upload first video
curl -X POST "http://localhost:8000/transcript" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_1"}'

# Upload second video
curl -X POST "http://localhost:8000/transcript" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_2"}'
```

### 2. Query Across All Videos

```bash
curl -X POST "http://localhost:8000/ask/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I handle errors in Python?",
    "n_results": 5
  }'
```

### 3. Query Specific Video

```bash
curl -X POST "http://localhost:8000/ask/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are decorators?",
    "video_id": "abc123",
    "n_results": 3
  }'
```

### 4. Example Response

```json
{
  "success": true,
  "answer": "Python offers several error handling mechanisms. Try-except blocks are the most common approach, allowing you to catch and handle specific exceptions. You can also use context managers with 'with' statements for automatic cleanup.",
  "citations": [
    {
      "video_id": "abc123",
      "video_title": "Python Error Handling Basics",
      "text": "Try-except blocks are the most common approach for handling errors in Python. You can catch specific exceptions...",
      "timestamp_range": {
        "start": 134.5,
        "end": 185.2,
        "formatted": "02:14 – 03:05"
      },
      "relevance_score": 0.92
    },
    {
      "video_id": "def456",
      "video_title": "Advanced Python Patterns",
      "text": "Context managers using 'with' statements provide automatic cleanup and exception handling...",
      "timestamp_range": {
        "start": 420.1,
        "end": 458.7,
        "formatted": "07:00 – 07:38"
      },
      "relevance_score": 0.87
    }
  ],
  "error": null
}
```

## Frontend Integration

### Display Citations

```javascript
// Example: Display answer with citations
response.citations.forEach(citation => {
  console.log(`Source: ${citation.video_title}`);
  console.log(`Timestamp: ${citation.timestamp_range.formatted}`);
  console.log(`Relevance: ${citation.relevance_score}`);
  
  // Create "Jump to Video" link
  const youtubeUrl = `https://youtube.com/watch?v=${citation.video_id}&t=${Math.floor(citation.timestamp_range.start)}s`;
  console.log(`Watch: ${youtubeUrl}`);
});
```

### Jump to Video Feature

```javascript
function jumpToVideo(citation) {
  const startSeconds = Math.floor(citation.timestamp_range.start);
  const url = `https://youtube.com/watch?v=${citation.video_id}&t=${startSeconds}s`;
  window.open(url, '_blank');
}
```

## Storage Structure

### Transcript Storage (In-Memory)

```python
transcript_storage = {
    'abc123': {
        'text': 'Full cleaned transcript...',
        'segments': [
            {'text': 'Hello everyone', 'start': 0.0, 'duration': 2.0},
            {'text': 'Today we learn Python', 'start': 2.0, 'duration': 3.0},
            # ...
        ],
        'title': 'Python Tutorial'
    },
    'def456': {
        # Another video...
    }
}
```

### Vector Database (ChromaDB)

Each chunk is stored with:
- **Document:** The chunk text
- **Metadata:** video_id, chunk_id, start_time, end_time, video_title, word_count
- **Embedding:** 384-dimensional vector (automatic)
- **ID:** Unique identifier (video_id_chunk_id)

## Performance Considerations

### Timestamp Mapping
- Uses fuzzy matching to locate chunks in original segments
- Tolerance parameter for matching flexibility
- Fallback to segment boundaries if exact match fails

### Multi-Video Search
- ChromaDB handles cross-video search efficiently
- Results ranked by semantic similarity
- Optional filtering by video IDs for targeted search

### Scalability
- In-memory storage suitable for development
- For production, migrate to:
  - PostgreSQL for transcript metadata
  - Redis for caching
  - Persistent ChromaDB for vectors

## Testing

### Manual Testing Steps

1. **Upload 2-3 related videos** (e.g., Python tutorials)
2. **Ask cross-video question:** "What are different ways to handle errors?"
3. **Verify response includes:**
   - Answer synthesizing multiple sources
   - Citations with video titles
   - Timestamp ranges in MM:SS format
   - Relevance scores
4. **Test timestamp accuracy:** Click through to videos and verify timestamps

### Example Test Cases

```python
# Test 1: Single video query
response = await ask_with_citations({
    "question": "What is a decorator?",
    "video_id": "abc123",
    "n_results": 3
})
assert len(response.citations) <= 3
assert all(c.video_id == "abc123" for c in response.citations)

# Test 2: Multi-video query
response = await ask_with_citations({
    "question": "How to optimize Python code?",
    "n_results": 5
})
# Should return results from multiple videos
video_ids = {c.video_id for c in response.citations}
assert len(video_ids) > 1

# Test 3: Timestamp format
citation = response.citations[0]
assert citation.timestamp_range.formatted.match(r'\d{2}:\d{2} – \d{2}:\d{2}')
```

## Future Enhancements

### Planned Features
- **Video metadata extraction:** Get actual titles from YouTube API
- **Confidence scores:** Add confidence metrics to citations
- **Citation clustering:** Group related citations together
- **Visual timeline:** Generate timeline visualization for frontend
- **Cross-language support:** Link videos in different languages

### Optimization Opportunities
- **Caching:** Cache frequently asked questions
- **Batch processing:** Process multiple videos in parallel
- **Smart chunking:** Adjust chunk sizes based on video type
- **Relevance tuning:** Fine-tune distance thresholds

## Troubleshooting

### Timestamps Not Appearing
- Verify `transcript_segments` is passed to `chunk_with_metadata()`
- Check that `get_transcript_with_timestamps()` is used instead of `get_transcript_from_url()`
- Ensure vector store metadata includes `start_time` and `end_time`

### Multi-Video Search Not Working
- Confirm multiple videos are uploaded
- Check that `video_id` is None or omitted in request
- Verify ChromaDB collection contains chunks from multiple videos

### Inaccurate Timestamps
- Increase tolerance parameter in `map_chunk_to_timestamps()`
- Check that transcript cleaning doesn't remove too much text
- Verify original segments have correct timestamps

## Summary

The multi-video querying and timestamp attribution features transform Explainify into a powerful video knowledge base system. Users can now:

✅ Query across their entire video library  
✅ Get precise timestamp references for every answer  
✅ Verify information by jumping directly to source moments  
✅ Build trust through transparent source attribution  

This creates a "jump to video" UX that significantly enhances the user experience and credibility of the system.
