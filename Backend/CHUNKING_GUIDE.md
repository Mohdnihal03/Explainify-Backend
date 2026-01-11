# Semantic Chunking Guide

## Why TextTiling Algorithm?

### ✅ Reasons for Choosing TextTiling:

1. **No LLM Required**
   - Pure algorithmic approach
   - No API costs or rate limits
   - Runs completely offline

2. **Topic-Aware Segmentation**
   - Detects natural topic boundaries
   - Creates semantically coherent chunks
   - Preserves context within each chunk

3. **Proven & Reliable**
   - Published research (Hearst, 1997)
   - Widely used in academia and industry
   - Battle-tested algorithm

4. **Fast Performance**
   - Processes long transcripts in seconds
   - No network latency
   - Scales well

5. **Optimized for Transcripts**
   - Works well with spoken content
   - Handles informal language
   - Adapts to varying content structure

### How TextTiling Works:

```
1. Split text into sentence blocks
2. Calculate word similarity between adjacent blocks
3. Find points where similarity drops (topic shift)
4. Create chunk boundaries at these points
```

**Result:** Chunks that represent coherent topics/segments

---

## How to Verify Chunking Results

### Method 1: Run the Test Script

```bash
cd Backend
python Chunking/Textchunk.py
```

This will:
- Chunk a sample transcript
- Show each chunk with word count
- Display verification results
- Print pass/fail status

### Method 2: Use Verification Functions

```python
from Chunking.Textchunk import SemanticChunker, verify_chunking, print_chunking_report

# Create chunker
chunker = SemanticChunker(w=20, k=10)

# Chunk your text
chunks = chunker.chunk_text(your_transcript)

# Verify results
verification = verify_chunking(your_transcript, chunks)

# Print detailed report
print_chunking_report(chunks, verification)
```

### Method 3: Check Metadata

```python
# Get chunks with metadata
chunks_with_metadata = chunker.chunk_with_metadata(text, video_id="abc123")

# Inspect each chunk
for chunk_data in chunks_with_metadata:
    print(f"Chunk {chunk_data['chunk_id']}")
    print(f"Words: {chunk_data['word_count']}")
    print(f"Preview: {chunk_data['text'][:100]}...")
    print()
```

---

## Verification Checklist

### ✅ What to Check:

1. **No Data Loss**
   - Total words in chunks ≈ words in original text
   - Acceptable variance: ±10 words

2. **No Empty Chunks**
   - Every chunk should have content
   - Minimum: 20 words per chunk

3. **Reasonable Sizes**
   - Chunks should be 50-2000 words
   - Average: 200-500 words

4. **Coherent Topics**
   - Each chunk should discuss one main topic
   - Read first/last sentences to verify flow

5. **Total Chunk Count**
   - For 10-minute video: ~3-8 chunks
   - For 30-minute video: ~10-20 chunks
   - For 60-minute video: ~20-40 chunks

---

## Expected Output Format

### Verification Report Example:

```
================================================================================
CHUNKING REPORT
================================================================================

Total Chunks: 5

--- Chunk 1 ---
Words: 287
Preview: Today we're going to talk about Python programming. Python is a high-level...

--- Chunk 2 ---
Words: 312
Preview: Now let's discuss data types in Python. Python has several built-in...

--- Chunk 3 ---
Words: 245
Preview: Moving on to functions. Functions are reusable blocks of code...

================================================================================
VERIFICATION RESULTS
================================================================================
Overall: ✅ PASSED

Checks:
  ✅ no_data_loss: True
  ✅ no_empty_chunks: True
  ✅ reasonable_sizes: True
  ✅ total_chunks: 5

Stats:
  original_words: 844
  chunks_words: 844
  empty_chunks: 0
  min_chunk_size: 245
  max_chunk_size: 312
  avg_chunk_size: 280.8
```

---

## Tuning Parameters

### Adjust `w` (Window Size):

```python
# More chunks (smaller segments)
chunker = SemanticChunker(w=10, k=10)

# Fewer chunks (larger segments)
chunker = SemanticChunker(w=30, k=10)

# Default (balanced)
chunker = SemanticChunker(w=20, k=10)
```

### Adjust `k` (Smoothing):

```python
# More sensitive (more boundaries)
chunker = SemanticChunker(w=20, k=5)

# Less sensitive (fewer boundaries)
chunker = SemanticChunker(w=20, k=15)
```

---

## Short vs Long-form Optimization 🚀

The system automatically adjusts chunking granularity based on the transcript length (word count) to ensure the best RAG performance:

| Video Type | Word Count | Window Size (`w`) | Smoothing (`k`) | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Short** | < 1,000 | 15 | 10 | Finer granularity for dense content. |
| **Medium** | 1,000 - 4,000 | 20 | 10 | Balanced default for most videos. |
| **Long** | > 4,000 | 30 | 15 | Broader topic detection for long-form. |

### Why this matters:
- **Short Videos**: Prevents creating too few chunks (which would lead to poor retrieval).
- **Long Videos**: Prevents over-segmenting into hundreds of tiny chunks, preserving broader context.

---

## Integration with Main API

The chunker will be integrated into `main.py` to:

1. **Fetch transcript** → YouTube API
2. **Clean transcript** → TextCleaner
3. **Chunk transcript** → SemanticChunker ✨
4. **Store chunks** → Save to files/database

Next step: Update `main.py` to use the chunker!
