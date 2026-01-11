# YouTube Transcript AI - Backend

This is the FastAPI backend for the YouTube Video Q&A system. It allows users to ask questions about YouTube videos and receive AI-powered answers based on the video's transcript.

## Features

- 📝 Fetch transcripts from YouTube videos
- 🤖 AI-powered question answering using Google Gemini
- 🌐 RESTful API with FastAPI
- 📚 Automatic API documentation (Swagger UI)
- 🔒 Environment-based configuration

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Get your Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. Edit `.env` and add your API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### 3. Run the Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Get Transcript
**POST** `/transcript`

Fetch the transcript for a YouTube video.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "languages": ["en"]
}
```

**Response:**
```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "transcript": "Full transcript text...",
  "error": null
}
```

### 2. Ask Question
**POST** `/ask`

Ask a question about a YouTube video and get an AI-powered answer.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "question": "What is the main topic of this video?",
  "languages": ["en"]
}
```

**Response:**
```json
{
  "success": true,
  "question": "What is the main topic of this video?",
  "answer": "Based on the transcript, the main topic is...",
  "error": null
}
```

### 3. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "YouTube Q&A API"
}
```

## File Structure

```
Backend/
├── main.py                 # FastAPI application and endpoints
├── youtube_transcript.py   # YouTube transcript fetching logic
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .env                   # Your actual environment variables (not in git)
└── README.md              # This file
```

## How It Works

1. **Transcript Fetching**: The `youtube_transcript.py` module uses the `youtube-transcript-api` library to fetch video transcripts from YouTube.

2. **AI Processing**: The `main.py` file uses Google's Gemini AI model to answer questions based on the transcript content.

3. **API Layer**: FastAPI provides a clean REST API interface with automatic validation and documentation.

## Example Usage

### Using cURL

```bash
# Get transcript
curl -X POST "http://localhost:8000/transcript" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "question": "What is this video about?"
  }'
```

### Using Python

```python
import requests

# Ask a question
response = requests.post(
    "http://localhost:8000/ask",
    json={
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "question": "What is the main message of this video?"
    }
)

print(response.json())
```

## Troubleshooting

### No transcript available
- Not all YouTube videos have transcripts/captions
- Try videos with auto-generated or manual captions
- Check if the video is publicly accessible

### API Key errors
- Ensure your `GOOGLE_API_KEY` is correctly set in `.env`
- Verify the API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)

### CORS errors
- The API is configured to allow all origins in development
- For production, update the `allow_origins` in `main.py`

## Next Steps

- Add caching for frequently accessed transcripts
- Implement rate limiting
- Add user authentication
- Support for multiple languages
- Store conversation history
- Add vector database for semantic search

## License

MIT
