# Enhanced Ask Endpoint with Citations and Timestamps
# This file contains the enhanced /ask endpoint that provides timestamp attribution

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
from Embedding.vector_store import VectorStore
from LLM.gemini_agent import GeminiAgent
from timestamp_mapper import TimestampMapper

router = APIRouter()

# Define models locally to avoid circular import
class QuestionRequest(BaseModel):
    """Data model for the question request body."""
    question: str
    video_id: Optional[str] = None
    n_results: Optional[int] = 3  # Default to 3 citations for cleaner UI
    chat_history: Optional[List[Dict]] = []  # Accept any dict structure for flexibility


class TimestampRange(BaseModel):
    """Data model for timestamp ranges in citations."""
    start: float
    end: float
    formatted: str  # e.g., "02:14 – 03:05"

class Citation(BaseModel):
    """Data model for a single citation with timestamp."""
    video_id: str
    video_title: Optional[str] = None
    text: str
    timestamp_range: TimestampRange
    relevance_score: float

class EnhancedAnswerResponse(BaseModel):
    """Enhanced Q&A response with citations and timestamps."""
    success: bool
    answer: Optional[str] = None
    citations: Optional[List[Citation]] = []
    error: Optional[str] = None



@router.post("/ask/enhanced", response_model=EnhancedAnswerResponse)
async def ask_with_citations(request: QuestionRequest):
    """
    Answer a user's question with full citations and timestamp attribution.
    Supports multi-video querying when video_id is None.
    
    Args:
        request: QuestionRequest containing the question and optional video_id
    
    Returns:
        EnhancedAnswerResponse with answer, citations, and timestamps
    """
    try:
        # 1. Initialize Vector Store
        vector_store = VectorStore()
        
        # 2. Search for relevant chunks (multi-video if video_id is None)
        if request.video_id:
            # Single video search
            relevant_chunks = vector_store.search(
                query=request.question,
                n_results=request.n_results,
                video_id=request.video_id
            )
        else:
            # Multi-video search across all videos
            relevant_chunks = vector_store.search_multi_video(
                query=request.question,
                n_results=request.n_results
            )
        
        if not relevant_chunks:
            return EnhancedAnswerResponse(
                success=False,
                error="No relevant information found in the transcripts."
            )
        
        # 3. Generate Answer using Gemini
        try:
            agent = GeminiAgent()
            answer = agent.generate_answer(
                request.question, 
                relevant_chunks, 
                request.chat_history
            )
            
            # 4. Build citations with timestamps
            citations = []
            for chunk in relevant_chunks:
                metadata = chunk.get('metadata', {})
                
                # Get timestamp data from metadata
                start_time = metadata.get('start_time', 0.0)
                end_time = metadata.get('end_time', 0.0)
                
                # Create timestamp range
                timestamp_range = TimestampRange(
                    start=start_time,
                    end=end_time,
                    formatted=TimestampMapper.format_range(start_time, end_time)
                )
                
                # Create citation
                citation = Citation(
                    video_id=metadata.get('video_id', 'unknown'),
                    video_title=metadata.get('video_title', 'Unknown Video'),
                    text=chunk.get('text', '')[:200] + "...",  # Truncate for display
                    timestamp_range=timestamp_range,
                    relevance_score=1.0 - chunk.get('distance', 0.0)  # Convert distance to relevance
                )
                citations.append(citation)
            
            return EnhancedAnswerResponse(
                success=True,
                answer=answer,
                citations=citations
            )
            
        except ValueError as ve:
            # Handle missing API key
            return EnhancedAnswerResponse(
                success=False,
                error=f"Configuration Error: {str(ve)}. Please check your .env file."
            )
            
    except Exception as e:
        return EnhancedAnswerResponse(
            success=False,
            error=f"An error occurred: {str(e)}"
        )
