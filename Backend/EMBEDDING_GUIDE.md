# Embeddings & Vector Storage Guide

## Overview

We have integrated **ChromaDB** to store and search transcript chunks. This enables semantic search, allowing users to find relevant parts of a video by meaning, not just keywords.

## 🛠️ Components

### 1. Vector Store (`Embedding/vector_store.py`)
- **Library**: `chromadb`
- **Embedding Model**: `all-MiniLM-L6-v2` (Default in ChromaDB)
  - Converts text to 384-dimensional vectors
  - Optimized for semantic similarity
  - Runs locally (no API costs)
- **Storage**: Persisted to `Backend/chroma_db/` folder

### 2. Integration (`main.py`)
- Automatically initializes vector store on startup
- When a transcript is processed:
  1. Chunks are generated
  2. Old chunks for the video are deleted (to prevent duplicates)
  3. New chunks are embedded and stored

## 🔄 Data Flow

```
Cleaned Text 
   ↓ 
Semantic Chunks 
   ↓ 
Embedding Model (all-MiniLM-L6-v2)
   ↓ 
Vector Embeddings ([0.1, -0.5, ...])
   ↓ 
ChromaDB (Persistent Storage)
```

## 🔍 How to Search (Code Example)

```python
from Embedding.vector_store import VectorStore

# Initialize
store = VectorStore()

# Search
results = store.search(
    query="How does backpropagation work?",
    n_results=3,
    video_id="dQw4w9WgXcQ"  # Optional filter
)

# Print results
for res in results:
    print(f"Match: {res['text']}")
    print(f"Score: {res['distance']}")
```

## 📂 File Structure

```
Backend/
├── chroma_db/                       # 💾 Vector Database (Auto-created)
├── Embedding/
│   └── vector_store.py              # 🧠 Vector Logic
├── requirements.txt                 # Added chromadb, sentence-transformers
└── main.py                          # Updated integration
```

## ✅ Verification

To verify it works:
1. Run `pip install -r requirements.txt`
2. Start server: `uvicorn main:app --reload`
3. POST a URL to `/transcript`
4. Check if `Backend/chroma_db` folder is created
