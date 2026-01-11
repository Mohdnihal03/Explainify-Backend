# Question Answering (RAG) Guide

## Overview

We have implemented a **Retrieval Augmented Generation (RAG)** system. This allows users to ask questions about a video, and the system answers using the video's transcript as context.

## 🧠 How It Works

1. **User asks a question** ("What is backpropagation?")
2. **Search**: System converts question to vector and finds top 3 relevant transcript chunks from ChromaDB.
3. **Prompting**: System constructs a prompt containing:
   - The user's question
   - The relevant transcript chunks
   - Instructions to answer *only* based on the context
4. **Generation**: Prompt is sent to **Google Gemini Pro**.
5. **Response**: Gemini generates the answer.

## 🚀 How to Use

### 1. Setup API Key
Ensure your `.env` file has your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

### 2. Ask a Question (API Endpoint)

**Endpoint:** `POST /ask`

**Request Body:**
```json
{
  "question": "What does the speaker say about Python data types?",
  "video_id": "dQw4w9WgXcQ"  // Optional: Filter by video
}
```

**Response:**
```json
{
  "success": true,
  "answer": "The speaker mentions that Python has several built-in data types including integers, floats, strings, and booleans.",
  "context": [
    {
      "text": "Now let's discuss data types in Python...",
      "metadata": {"video_id": "dQw4w9WgXcQ", ...}
    },
    ...
  ]
}
```

## 📂 Code Structure

- **`LLM/gemini_agent.py`**: Handles communication with Google Gemini API.
- **`main.py`**:
  - `/ask` endpoint orchestrates the flow (Search → Generate).
  - Loads environment variables.

## 🛠️ Troubleshooting

- **"Configuration Error"**: Check if `GOOGLE_API_KEY` is set in `.env`.
- **"No relevant information found"**: The question might be unrelated to the video content.
- **"Error generating answer"**: Check internet connection or API quota.
