# YouTube Transcript AI - Project Overview

## 🚀 Project Value Proposition
**"Talk to your YouTube videos."**

YouTube Transcript AI is an intelligent backend system that transforms passive video consumption into an active, conversational learning experience. Instead of watching hours of footage to find one specific answer, users can simply ask questions and get instant, accurate responses based on the video's content.

### Why it's helpful:
- **Save Time**: Instantly extract key insights without watching the entire video.
- **Deep Understanding**: Ask follow-up questions to clarify complex topics.
- **Noise Filtering**: The AI automatically ignores "subscribe" pleas and intro fluff, focusing only on the educational content.
- **Contextual Memory**: Have a real conversation—the AI remembers what you just asked.

---

## 🛠️ Technical Architecture
- **Backend**: FastAPI (High-performance Python web framework)
- **AI/LLM**: Google Gemini Pro (Reasoning and answer generation)
- **Vector Database**: ChromaDB (Semantic search and context retrieval)
- **Processing**: Custom semantic chunking algorithm (TextTiling-based)

---

## 🔌 API Documentation for Frontend

### Base URL
`http://localhost:8000`

### 1. Process Video
**Endpoint**: `POST /transcript`
**Description**: Fetches, cleans, chunks, and stores a video transcript. Call this first!

**Request Body**:
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response**:
```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "transcript": "Full cleaned text..."
}
```

### 2. Chat with Video
**Endpoint**: `POST /ask`
**Description**: Ask a question about the processed video. Supports conversation history.

**Request Body**:
```json
{
  "question": "What is the roadmap mentioned?",
  "video_id": "VIDEO_ID",
  "n_results": 5,
  "chat_history": [
    {
      "role": "user",
      "content": "What is this video about?"
    },
    {
      "role": "model",
      "content": "It is about learning Python."
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "answer": "The roadmap starts with learning variables...",
  "context": [
    {
      "text": "Relevant chunk text...",
      "metadata": {"chunk_id": 3}
    }
  ]
}
```

### 3. Get Full Transcript
**Endpoint**: `GET /transcript/{video_id}`
**Description**: Retrieve the full cleaned text of a video.

**Response**:
```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "transcript": "Full text content..."
}
```

---

## 🎨 Frontend Implementation Tips
- **State Management**: Keep track of `video_id` after the initial `POST /transcript` call.
- **Chat UI**: Maintain a local array of messages (`chat_history`) to display to the user and send back to the API with each new request.
- **Loading States**: The `POST /transcript` endpoint might take a few seconds to process long videos—show a nice loading spinner!
