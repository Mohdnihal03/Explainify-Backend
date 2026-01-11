import google.generativeai as genai
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiAgent:
    """
    A class to interact with Google's Gemini Pro model for Question Answering.
    """
    
    def __init__(self):
        """
        Initialize the Gemini Agent.
        Fetches API key from environment variables.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
    def generate_answer(self, question: str, context_chunks: List[Dict], chat_history: List[Dict] = []) -> str:
        """
        Generate an answer to the question based on the provided context chunks and chat history.
        
        Args:
            question (str): The user's question
            context_chunks (List[Dict]): List of relevant transcript chunks from VectorStore
            chat_history (List[Dict]): List of previous messages [{"role": "user", "content": "..."}, ...]
            
        Returns:
            str: The generated answer
        """
        # 1. Prepare the context text
        context_text = "\n\n".join([
            f"Chunk {i+1}: {chunk['text']}" 
            for i, chunk in enumerate(context_chunks)
        ])
        
        # 2. Format chat history
        history_text = ""
        if chat_history:
            history_text = "PREVIOUS CONVERSATION:\n" + "\n".join([
                f"{msg.get('role', 'unknown').upper()}: {msg.get('content', '')}" 
                for msg in chat_history
            ]) + "\n\n"
        
        # 3. Construct the prompt
        prompt = f"""
        You are an AI assistant that answers questions about YouTube videos based on their transcripts.
        
        {history_text}
        CONTEXT FROM VIDEO TRANSCRIPT:
        {context_text}
        
        USER QUESTION:
        {question}
        
        INSTRUCTIONS:
- Prioritize the video transcript when answering the question.
- If the transcript directly contains the answer, base your response on it.
- If the transcript is incomplete, unclear, or assumes prior knowledge, you MAY use your general knowledge to:
  • Explain concepts
  • Provide definitions
  • Clarify terminology
  • Add brief contextual understanding
- Do NOT contradict the transcript.
- Do NOT invent facts that are unrelated to the video topic.
- If neither the transcript nor your general knowledge reasonably supports an answer, respond with:
  "I couldn't find a reliable answer based on the video transcript."

STYLE GUIDELINES:
- Be concise, clear, and direct.
- Do NOT mention transcript chunks, timestamps, or internal references.
- Ignore non-informational content such as:
  • Greetings and introductions
  • Outros, sign-offs, and calls to action
  • Casual or irrelevant chatter
- Focus on the educational and informational content.
- Maintain continuity using the previous conversation if the question refers back to it.
        ANSWER:
        """
        
        try:
            # 3. Generate response
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating answer: {str(e)}"

# Example usage
if __name__ == "__main__":
    try:
        agent = GeminiAgent()
        # Mock context
        context = [{"text": "Python is a programming language."}]
        print(agent.generate_answer("What is Python?", context))
    except Exception as e:
        print(f"Setup failed: {e}")
