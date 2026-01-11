# Updated User Flow with Chunking & Storage

## 🔄 Complete Flow (Updated)

```
┌─────────────────────────────────────────────────────────────────┐
│                    UPDATED USER FLOW                             │
└─────────────────────────────────────────────────────────────────┘

1️⃣ USER ACTION
   └─> POST YouTube URL to /transcript endpoint
       Example: {"url": "https://youtube.com/watch?v=abc123"}

2️⃣ FETCH TRANSCRIPT (youtube_transcript.py)
   └─> Extract video_id: "abc123"
   └─> Fetch raw transcript from YouTube
   └─> Return raw messy text

3️⃣ CLEAN TRANSCRIPT (textcleaning/Textoptimization.py)
   └─> Remove filler words, extra spaces, repeated words
   └─> Fix broken sentences
   └─> Return cleaned text

4️⃣ CHUNK TRANSCRIPT (Chunking/Textchunk.py) ✨ NEW
   └─> Use TextTiling semantic chunking
   └─> Detect topic boundaries
   └─> Create coherent chunks
   └─> Generate metadata for each chunk

5️⃣ STORE EVERYTHING (main.py) ✨ UPDATED
   ├─> Save full transcript: transcripts/abc123.txt
   ├─> Save chunks: chunks/abc123/chunk_0.txt, chunk_1.txt, ...
   └─> Save metadata: chunks/abc123/metadata.json

6️⃣ RETURN RESPONSE
   └─> Return cleaned transcript to user
   └─> Include video_id and success status
```

---

## 📂 File Structure After Processing

### Example: Video ID = "dQw4w9WgXcQ"

```
Backend/
├── transcripts/                      # Full cleaned transcripts
│   └── dQw4w9WgXcQ.txt              # Complete cleaned transcript
│
├── chunks/                           # Semantic chunks (NEW ✨)
│   └── dQw4w9WgXcQ/                 # Folder per video
│       ├── chunk_0.txt              # First topic chunk
│       ├── chunk_1.txt              # Second topic chunk
│       ├── chunk_2.txt              # Third topic chunk
│       ├── chunk_3.txt              # Fourth topic chunk
│       └── metadata.json            # Chunk metadata
│
├── main.py
├── youtube_transcript.py
├── textcleaning/
│   └── Textoptimization.py
└── Chunking/
    └── Textchunk.py
```

---

## 📄 File Contents Examples

### 1. Full Transcript
**File:** `transcripts/dQw4w9WgXcQ.txt`
```
Today we're going to talk about Python programming. Python is a high-level 
programming language that's great for beginners. It has simple syntax and 
is very readable. Many companies use Python for web development. Now let's 
discuss data types in Python...
```

### 2. Individual Chunks
**File:** `chunks/dQw4w9WgXcQ/chunk_0.txt`
```
Today we're going to talk about Python programming. Python is a high-level 
programming language that's great for beginners. It has simple syntax and 
is very readable. Many companies use Python for web development.
```

**File:** `chunks/dQw4w9WgXcQ/chunk_1.txt`
```
Now let's discuss data types in Python. Python has several built-in data 
types including integers, floats, strings, and booleans. Each data type 
has its own characteristics and use cases.
```

**File:** `chunks/dQw4w9WgXcQ/chunk_2.txt`
```
Moving on to functions. Functions are reusable blocks of code that perform 
specific tasks. You define a function using the def keyword. Functions can 
take parameters and return values.
```

### 3. Metadata File
**File:** `chunks/dQw4w9WgXcQ/metadata.json`
```json
[
  {
    "chunk_id": 0,
    "text": "Today we're going to talk about Python programming...",
    "word_count": 287,
    "char_count": 1543,
    "video_id": "dQw4w9WgXcQ"
  },
  {
    "chunk_id": 1,
    "text": "Now let's discuss data types in Python...",
    "word_count": 312,
    "char_count": 1687,
    "video_id": "dQw4w9WgXcQ"
  },
  {
    "chunk_id": 2,
    "text": "Moving on to functions. Functions are reusable...",
    "word_count": 245,
    "char_count": 1321,
    "video_id": "dQw4w9WgXcQ"
  }
]
```

---

## 🎯 What Gets Stored

| Item | Location | Format | Purpose |
|------|----------|--------|---------|
| **Full Transcript** | `transcripts/{video_id}.txt` | Plain text | Complete cleaned transcript |
| **Individual Chunks** | `chunks/{video_id}/chunk_X.txt` | Plain text | Topic-based segments |
| **Chunk Metadata** | `chunks/{video_id}/metadata.json` | JSON | Stats & info about each chunk |

---

## 🔍 Metadata Details

Each chunk's metadata includes:

```json
{
  "chunk_id": 0,           // Sequential ID (0, 1, 2, ...)
  "text": "...",           // The actual chunk text
  "word_count": 287,       // Number of words
  "char_count": 1543,      // Number of characters
  "video_id": "abc123"     // Associated video ID
}
```

**Why this is useful:**
- ✅ Know how many chunks were created
- ✅ See chunk sizes for verification
- ✅ Easy to load specific chunks later
- ✅ Track which chunks belong to which video

---

## 📊 Example API Response

```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "transcript": "Today we're going to talk about Python programming..."
}
```

**Behind the scenes:**
- ✅ Full transcript saved to `transcripts/dQw4w9WgXcQ.txt`
- ✅ 5 chunks saved to `chunks/dQw4w9WgXcQ/chunk_0.txt` through `chunk_4.txt`
- ✅ Metadata saved to `chunks/dQw4w9WgXcQ/metadata.json`

---

## 🚀 Benefits of This Structure

1. **Organized Storage**
   - Each video has its own folder
   - Easy to find and manage chunks

2. **Metadata Tracking**
   - Know exactly what was created
   - Verify chunking quality
   - Debug issues easily

3. **Ready for Next Steps**
   - Chunks ready for embedding
   - Metadata ready for vector database
   - Easy to implement search

4. **Scalable**
   - Can handle thousands of videos
   - Each video isolated in its own folder
   - No naming conflicts

---

## ✅ Summary

**What happens when you POST a URL:**

1. Fetch raw transcript from YouTube ✅
2. Clean the transcript ✅
3. Chunk semantically (TextTiling) ✅
4. Save full transcript to `transcripts/` ✅
5. Save chunks to `chunks/{video_id}/` ✅
6. Save metadata to `chunks/{video_id}/metadata.json` ✅
7. Return cleaned transcript to user ✅

**Everything is now stored and ready for the Q&A system!** 🎉
