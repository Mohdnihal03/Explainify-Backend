# Import ChromaDB for vector storage
import chromadb
from chromadb.config import Settings

# Import typing utilities
from typing import List, Dict, Optional

# Import uuid for generating unique IDs
import uuid

class VectorStore:
    """
    A class to handle vector database operations using ChromaDB.
    This manages storing text chunks as embeddings and retrieving them via semantic search.
    """
    
    def __init__(self, collection_name: str = "youtube_transcripts"):
        """
        Initialize the VectorStore with a ChromaDB client.
        
        Args:
            collection_name (str): Name of the collection to store embeddings in
        """
        # Initialize ChromaDB client
        # PersistentClient saves data to disk so it persists between restarts
        self.client = chromadb.PersistentClient(path="chroma_db")
        
        # Get or create the collection
        # ChromaDB uses the default embedding function (all-MiniLM-L6-v2) if none is provided
        # This model converts text to 384-dimensional vectors
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
    def add_chunks(self, chunks_with_metadata: List[Dict]):
        """
        Add text chunks to the vector database.
        
        Args:
            chunks_with_metadata (List[Dict]): List of chunk dictionaries containing 'text' and metadata
        """
        if not chunks_with_metadata:
            return
            
        # Prepare data for ChromaDB
        documents = []  # The actual text content
        metadatas = []  # Metadata (video_id, chunk_id, etc.)
        ids = []        # Unique IDs for each chunk
        
        for chunk in chunks_with_metadata:
            # Add text
            documents.append(chunk['text'])
            
            # Add metadata (filter out 'text' to avoid duplication)
            # We convert non-string/int/float values to strings if necessary
            meta = {
                "video_id": chunk.get('video_id', 'unknown'),
                "chunk_id": chunk.get('chunk_id', 0),
                "word_count": chunk.get('word_count', 0)
            }
            metadatas.append(meta)
            
            # Generate a unique ID for the chunk
            # Format: video_id_chunk_id
            unique_id = f"{chunk.get('video_id', 'unknown')}_{chunk.get('chunk_id', 0)}"
            ids.append(unique_id)
            
        # Add to collection
        # ChromaDB automatically handles tokenization and embedding generation
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(documents)} chunks to vector store.")
        
    def search(self, query: str, n_results: int = 3, video_id: Optional[str] = None) -> List[Dict]:
        """
        Search for relevant chunks based on a query.
        
        Args:
            query (str): The search query (question)
            n_results (int): Number of results to return
            video_id (str): Optional filter to search only within a specific video
            
        Returns:
            List[Dict]: List of relevant chunks with their metadata and distance scores
        """
        # Prepare filter if video_id is provided
        where_filter = {"video_id": video_id} if video_id else None
        
        # Perform search
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )
        
        # Format results
        # ChromaDB returns lists of lists (one list per query)
        formatted_results = []
        
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
                
        return formatted_results
    
    def delete_video_chunks(self, video_id: str):
        """
        Delete all chunks associated with a specific video ID.
        Useful for updating or removing videos.
        
        Args:
            video_id (str): The video ID to remove
        """
        self.collection.delete(
            where={"video_id": video_id}
        )

# Example usage
if __name__ == "__main__":
    # Initialize vector store
    store = VectorStore()
    
    # Example data
    sample_chunks = [
        {
            "text": "Python is a high-level programming language.",
            "video_id": "test_vid",
            "chunk_id": 0,
            "word_count": 6
        },
        {
            "text": "Machine learning uses statistical algorithms.",
            "video_id": "test_vid",
            "chunk_id": 1,
            "word_count": 5
        }
    ]
    
    # Add chunks
    store.add_chunks(sample_chunks)
    
    # Search
    results = store.search("What is Python?")
    
    print("Search Results:")
    for res in results:
        print(f"- {res['text']} (Score: {res['distance']})")
