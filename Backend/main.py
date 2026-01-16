# Import FastAPI - the main framework for building the API
from fastapi import FastAPI

# Import CORS middleware to allow cross-origin requests from frontend
from fastapi.middleware.cors import CORSMiddleware

# Import Pydantic BaseModel for request/response validation
from pydantic import BaseModel

# Import typing utilities for type hints
from typing import Optional, Dict, List

# Import our custom YouTube transcript fetcher module
from youtube_transcript import YouTubeTranscriptFetcher

# Import the text cleaner module
from textcleaning.Textoptimization import TranscriptCleaner

# Import the semantic chunker module
from Chunking.Textchunk import SemanticChunker

# Import the vector store module
from Embedding.vector_store import VectorStore

# Import the Gemini Agent
from LLM.gemini_agent import GeminiAgent

# Import os and pathlib for file operations
import os
from pathlib import Path

# Import json for storing chunk metadata
import json

# Import dotenv to load environment variables
from dotenv import load_dotenv

# Load environment variables (specifically GOOGLE_API_KEY)
# We explicitly specify the path to ensure it's found
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


# Create a FastAPI application instance
app = FastAPI()

# Startup event to check for API key
@app.on_event("startup")
async def startup_event():
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"✅ API Key loaded successfully from {env_path}")
    else:
        print(f"❌ WARNING: GOOGLE_API_KEY not found in {env_path}")
        print("Please create a .env file with GOOGLE_API_KEY=your_key_here")


# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the frontend (running on a different port/domain) to make requests to this API

# Get allowed origins from environment variable
# For development: "http://localhost:3000,http://localhost:5173"
# For production: "https://yourdomain.com,https://www.yourdomain.com"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    # allow_origins: List of origins that are allowed to make requests
    allow_origins=ALLOWED_ORIGINS,  # Only allow specified origins
    # allow_credentials: Whether to allow cookies and authentication headers
    allow_credentials=True,
    # allow_methods: HTTP methods that are allowed (GET, POST, etc.)
    allow_methods=["*"],  # Allow all methods
    # allow_headers: HTTP headers that are allowed in requests
    allow_headers=["*"],  # Allow all headers
)

# ... imports ...
from database import models, database, schemas 
import auth
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# Create tables
models.Base.metadata.create_all(bind=database.engine)

# ... app definition ...
app = FastAPI()

# Auth Routes
@app.post("/auth/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, full_name=user.full_name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# Include enhanced ask router (after app and middleware setup)
from enhanced_ask import router as enhanced_router
app.include_router(enhanced_router)


# Dictionary to store transcripts with timestamp data in memory
# Format: {video_id: {"text": "...", "segments": [...], "title": "..."}}
# In production, you would use a database instead
transcript_storage: Dict[str, Dict] = {}


# Define a Pydantic model for the POST request
# This validates incoming JSON data
class VideoRequest(BaseModel):
    """
    Data model for the video URL request body.
    """
    url: str

class QuestionRequest(BaseModel):
    """
    Data model for the question request body.
    """
    question: str
    video_id: Optional[str] = None
    n_results: Optional[int] = 3
    chat_history: Optional[List[Dict]] = []  # Accept any dict structure for flexibility



# Define a Pydantic model for the response
class TranscriptResponse(BaseModel):
    """
    Data model for the API response.
    """
    success: bool
    video_id: Optional[str] = None
    transcript: Optional[str] = None
    error: Optional[str] = None

class AnswerResponse(BaseModel):
    """
    Data model for the Q&A response.
    """
    success: bool
    answer: Optional[str] = None
    context: Optional[List[Dict]] = None
    error: Optional[str] = None

class TimestampRange(BaseModel):
    """
    Data model for timestamp ranges in citations.
    """
    start: float
    end: float
    formatted: str  # e.g., "02:14 – 03:05"

class Citation(BaseModel):
    """
    Data model for a single citation with timestamp.
    """
    video_id: str
    video_title: Optional[str] = None
    text: str
    timestamp_range: TimestampRange
    relevance_score: float

class EnhancedAnswerResponse(BaseModel):
    """
    Enhanced Q&A response with citations and timestamps.
    """
    success: bool
    answer: Optional[str] = None
    citations: Optional[List[Citation]] = []
    error: Optional[str] = None


# POST endpoint - Fetch and store a transcript from YouTube URL
@app.post("/transcript")
async def post_transcript(request: VideoRequest):
    """
    Fetch a transcript from a YouTube URL, clean it, chunk it, and store everything.
    
    Args:
        request: VideoRequest containing the YouTube URL
    
    Returns:
        TranscriptResponse with the fetched and cleaned transcript
    """
    try:
        # Create an instance of the YouTubeTranscriptFetcher
        fetcher = YouTubeTranscriptFetcher()
        
        # Extract the video ID from the URL
        video_id = fetcher.extract_video_id(request.url)
        
        # Check if video ID extraction was successful
        if not video_id:
            # Return an error response if URL is invalid
            return TranscriptResponse(
                success=False,
                error="Invalid YouTube URL"
            )
        
        # Fetch the transcript WITH timestamps using the new method
        transcript_data = fetcher.get_transcript_with_timestamps(request.url)
        
        # Check if transcript was successfully fetched
        if not transcript_data:
            # Return an error response if transcript is unavailable
            return TranscriptResponse(
                success=False,
                video_id=video_id,
                error="Could not fetch transcript"
            )
        
        # Extract components from transcript data
        raw_transcript = transcript_data['text']
        transcript_segments = transcript_data['segments']  # Preserve timestamps
        
        # Clean the transcript using the TranscriptCleaner
        # This removes filler words, extra spaces, repeated words, etc.
        cleaner = TranscriptCleaner()
        cleaned_transcript = cleaner.clean_transcript(raw_transcript)
        
        # Create the transcripts directory if it doesn't exist
        # This is where we'll store the full cleaned transcripts
        transcripts_dir = Path("transcripts")
        transcripts_dir.mkdir(exist_ok=True)
        
        # Define the file path using the video ID as the filename
        # Example: transcripts/dQw4w9WgXcQ.txt
        file_path = transcripts_dir / f"{video_id}.txt"
        
        # Write the cleaned transcript to the file
        # 'w' mode creates a new file or overwrites existing one
        # encoding='utf-8' ensures proper character encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_transcript)
        
        # ===== CHUNKING SECTION =====
        # Calculate word count to optimize chunking parameters
        word_count = len(cleaned_transcript.split())
        
        # Determine optimal TextTiling parameters based on length
        # Short: < 1000 words (~7 mins) -> w=15
        # Medium: 1000-4000 words -> w=20 (Default)
        # Long: > 4000 words (~30 mins) -> w=30
        if word_count < 1000:
            w, k = 15, 10
            print(f"🔹 Short video detected ({word_count} words). Using w=15 for finer granularity.")
        elif word_count > 4000:
            w, k = 30, 15
            print(f"🔹 Long video detected ({word_count} words). Using w=30 for broader topics.")
        else:
            w, k = 20, 10
            print(f"🔹 Medium video detected ({word_count} words). Using default w=20.")

        # Create semantic chunks with optimized parameters
        chunker = SemanticChunker(w=w, k=k)
        
        # Get chunks with metadata, timestamps, and overlapping for better RAG performance
        # use_overlap=True enables sliding window (25 word overlap between chunks)
        # This improves context retrieval for Q&A systems
        chunks_with_metadata = chunker.chunk_with_metadata(
            cleaned_transcript, 
            video_id=video_id,
            transcript_segments=transcript_segments,  # NEW: Pass timestamp data
            video_title=f"Video {video_id}",  # TODO: Extract actual title from YouTube API
            use_overlap=True,  # Enable overlapping chunks for RAG
            overlap_words=25   # 25 word overlap between consecutive chunks
        )

        
        # Create a directory for this video's chunks
        # Example: chunks/dQw4w9WgXcQ/
        chunks_dir = Path("chunks") / video_id
        chunks_dir.mkdir(parents=True, exist_ok=True)
        
        # Store each chunk as a separate file
        for chunk_data in chunks_with_metadata:
            chunk_id = chunk_data['chunk_id']
            
            # Save the chunk text
            # Example: chunks/dQw4w9WgXcQ/chunk_0.txt
            chunk_file = chunks_dir / f"chunk_{chunk_id}.txt"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk_data['text'])
        
        # Save chunk metadata as JSON
        # This includes chunk_id, word_count, char_count for each chunk
        # Example: chunks/dQw4w9WgXcQ/metadata.json
        metadata_file = chunks_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_with_metadata, f, indent=2, ensure_ascii=False)
            
        # ===== VECTOR STORAGE SECTION =====
        # Initialize the vector store
        vector_store = VectorStore()
        
        # Delete any existing chunks for this video to avoid duplicates
        vector_store.delete_video_chunks(video_id)
        
        # Add the new chunks to the vector database
        # This automatically converts text to embeddings and stores them
        vector_store.add_chunks(chunks_with_metadata)
        
        # Store the transcript data with timestamps in memory (for quick access)
        transcript_storage[video_id] = {
            "text": cleaned_transcript,
            "segments": transcript_segments,
            "title": f"Video {video_id}"  # TODO: Extract actual title
        }

        
        # Return a successful response with the cleaned transcript
        return TranscriptResponse(
            success=True,
            video_id=video_id,
            transcript=cleaned_transcript
        )
    
    except Exception as e:
        # Catch any unexpected errors and return error response
        return TranscriptResponse(
            success=False,
            error=f"An error occurred: {str(e)}"
        )


# POST endpoint - Ask a question about a video
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Answer a user's question about a video using RAG (Retrieval Augmented Generation).
    
    Args:
        request: QuestionRequest containing the question and optional video_id
    
    Returns:
        AnswerResponse with the generated answer and context used
    """
    try:
        # 1. Initialize Vector Store
        vector_store = VectorStore()
        
        # 2. Search for relevant chunks
        # This converts the question to an embedding and finds similar chunks
        relevant_chunks = vector_store.search(
            query=request.question,
            n_results=request.n_results,
            video_id=request.video_id
        )
        
        if not relevant_chunks:
            return AnswerResponse(
                success=False,
                error="No relevant information found in the transcripts."
            )
            
        # 3. Generate Answer using Gemini
        try:
            agent = GeminiAgent()
            answer = agent.generate_answer(request.question, relevant_chunks, request.chat_history)
            
            return AnswerResponse(
                success=True,
                answer=answer,
                context=relevant_chunks
            )
            
        except ValueError as ve:
            # Handle missing API key
            return AnswerResponse(
                success=False,
                error=f"Configuration Error: {str(ve)}. Please check your .env file."
            )
            
    except Exception as e:
        return AnswerResponse(
            success=False,
            error=f"An error occurred: {str(e)}"
        )


# GET endpoint - List all processed videos
@app.get("/videos")
async def list_videos():
    """
    Get a list of all processed videos.
    
    Returns:
        List of video metadata for all processed videos
    """
    videos = []
    for video_id, data in transcript_storage.items():
        videos.append({
            "video_id": video_id,
            "title": data.get("title", f"Video {video_id}"),
            "word_count": len(data.get("text", "").split()),
            "has_segments": len(data.get("segments", [])) > 0
        })
    
    return {
        "success": True,
        "count": len(videos),
        "videos": videos
    }


# GET endpoint - Retrieve a stored transcript by video ID
@app.get("/transcript/{video_id}")
async def get_transcript(video_id: str):
    """
    Retrieve a previously fetched transcript by video ID.
    
    Args:
        video_id: The YouTube video ID
    
    Returns:
        TranscriptResponse with the stored transcript
    """
    # Check if the video_id exists in our storage
    if video_id in transcript_storage:
        # Return the stored transcript text
        return TranscriptResponse(
            success=True,
            video_id=video_id,
            transcript=transcript_storage[video_id]["text"]  # Extract text from structured storage
        )
    else:
        # Return error if transcript not found
        return TranscriptResponse(
            success=False,
            video_id=video_id,
            error="Transcript not found. Please POST the URL first."
        )



# Entry point for running the application
if __name__ == "__main__":
    # Import uvicorn - the ASGI server for running FastAPI
    import uvicorn
    
    # Run the FastAPI application
    # host: 0.0.0.0 means accessible from any network interface
    # port: The port number to listen on (8000)
    # reload: Enable auto-reload during development
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
