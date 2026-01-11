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
# Get chunks with metadata (WITHOUT overlap)
chunks_with_metadata = chunker.chunk_with_metadata(
    text, 
    video_id="abc123",
    use_overlap=False
)

# Inspect each chunk
for chunk_data in chunks_with_metadata:
    print(f"Chunk {chunk_data['chunk_id']}")
    print(f"Words: {chunk_data['word_count']}")
    print(f"Preview: {chunk_data['text'][:100]}...")
    print()
```

### Method 4: Use Overlapping Chunks (Recommended for RAG) 🔄

```python
# Get chunks WITH overlapping content (sliding window approach)
# This is RECOMMENDED for RAG systems as it improves retrieval quality
chunks_with_overlap = chunker.chunk_with_overlap(
    text,
    overlap_words=25  # 25 word overlap between consecutive chunks
)

# Or use chunk_with_metadata with overlap enabled (RECOMMENDED)
chunks_with_metadata = chunker.chunk_with_metadata(
    text,
    video_id="abc123",
    use_overlap=True,      # Enable overlapping
    overlap_words=25       # Words to overlap
)

# Verify chunks with overlap
for chunk_data in chunks_with_metadata:
    print(f"Chunk {chunk_data['chunk_id']}: {chunk_data['word_count']} words")
    print(f"Has Overlap: {chunk_data['has_overlap']}")
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

## 🔄 Overlapping Chunks (Sliding Window) - NEW! ✨

### What is Overlap?

**Overlapping chunks** use a **sliding window approach** where consecutive chunks share common content. This dramatically improves RAG performance.

### Visual Example:

```
WITHOUT OVERLAP (Problem):
Chunk 1: "Machine learning processes patterns and makes predictions. [ENDS]"
Chunk 2: "[STARTS] These predictions drive business decisions. ML powers..."
                     ↑ CONTEXT LOST AT BOUNDARY

WITH OVERLAP (Solution):
Chunk 1: "Machine learning processes patterns and makes predictions."
Chunk 2: "...patterns and makes predictions. These predictions drive 
          business decisions. ML powers recommendation systems..."
         ← 25 word overlap maintains context
```

### Why You Need Overlap for RAG:

1. **Prevents Context Loss**
   - Information flows naturally across chunks
   - No abrupt boundaries that confuse the LLM

2. **Better Answer Retrieval**
   - Captures answers that span multiple chunk boundaries
   - Improves semantic search relevance

3. **Improved LLM Generation**
   - Gemini has complete context when generating answers
   - Reduces hallucinations from incomplete information

4. **Edge Case Protection**
   - Questions about transition topics are fully addressed
   - No information loss at chunk boundaries

### How to Use:

```python
from Chunking.Textchunk import SemanticChunker

chunker = SemanticChunker(w=20, k=10)

# Enable overlapping chunks (RECOMMENDED)
chunks = chunker.chunk_with_overlap(
    your_transcript,
    overlap_words=25  # Standard: 20-30 words
)

# Or with metadata (for vector storage):
chunks_with_meta = chunker.chunk_with_metadata(
    your_transcript,
    video_id="video_123",
    use_overlap=True,
    overlap_words=25
)
```

### Overlap Parameters:

| Parameter | Recommended | Range | Effect |
|-----------|------------|-------|--------|
| `overlap_words` | 25 | 15-40 | Number of words to repeat from previous chunk |

- **15 words**: Minimal overlap, smaller chunks
- **25 words**: Balanced (DEFAULT) ✅
- **40 words**: Heavy overlap, more context but larger storage

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

The chunker is integrated into `main.py` to:

1. **Fetch transcript** → YouTube API
2. **Clean transcript** → TextCleaner
3. **Chunk transcript** → SemanticChunker with optimal parameters
4. **Enable overlapping** → 25-word sliding window for RAG ✨
5. **Store chunks** → ChromaDB with embeddings

### Current Implementation in main.py:

```python
# Determine optimal parameters based on video length
if word_count < 1000:
    w, k = 15, 10  # Short videos: finer granularity
elif word_count > 4000:
    w, k = 30, 15  # Long videos: broader topics
else:
    w, k = 20, 10  # Medium videos: balanced (default)

# Create chunker with optimized parameters
chunker = SemanticChunker(w=w, k=k)

# Get chunks with overlap enabled (recommended for RAG)
chunks_with_metadata = chunker.chunk_with_metadata(
    cleaned_transcript,
    video_id=video_id,
    use_overlap=True,      # Enable sliding window
    overlap_words=25       # 25 word overlap
)
```

---

## Size Constraint Improvements

The **fallback chunking** method now enforces size constraints for consistent chunk quality:

### Parameters:

```python
def _fallback_chunking(
    self,
    text: str,
    target_sentences: int = 15,
    min_words: int = 100,      # Minimum chunk size
    max_words: int = 300       # Maximum chunk size
) -> List[str]:
    pass
```

### Why These Defaults?

| Parameter | Value | Reason |
|-----------|-------|--------|
| `min_words` | 100 | Ensures sufficient context for embeddings |
| `max_words` | 300 | Prevents chunks too large for retrieval |
| `target_sentences` | 15 | Balances granularity for educational content |

**Result:** More consistent, higher-quality chunks for RAG systems! 🚀

---

## Quick Start Guide

### For Educational Videos (Python, Data Science, etc.):

```python
from Chunking.Textchunk import SemanticChunker

# Create chunker optimized for educational content
chunker = SemanticChunker(w=15, k=8)

# Process with overlapping chunks
chunks = chunker.chunk_with_metadata(
    transcript,
    video_id="GRNI9T9R8gQ",
    use_overlap=True,
    overlap_words=25
)

print(f"✅ Created {len(chunks)} overlapping chunks")
for chunk in chunks:
    print(f"  - Chunk {chunk['chunk_id']}: {chunk['word_count']} words")
```

### Testing:

```bash
cd Backend
python Chunking/Textchunk.py
```

This runs 3 examples:
1. **Basic chunking** (no overlap)
2. **Overlapping chunks** (sliding window)
3. **Chunks with metadata** (for vector storage)

---
