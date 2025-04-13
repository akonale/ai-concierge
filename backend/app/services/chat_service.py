# backend/app/services/chat_service.py

import os
from typing import Dict, List, Any
import logging

import openai # For logging information

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Placeholder for Session/History Management (In-Memory for POC) ---
# Warning: This is NOT suitable for production. Use Redis or DB for persistence.
conversation_history_store: Dict[str, List[Dict[str, str]]] = {}

class ChatService:
    """
    Handles the core logic for processing chat messages,
    including RAG retrieval and interaction with the OpenAI API.
    """

    def __init__(self):
        # Initialize necessary components here later
        # e.g., self.vector_store = initialize_vector_store()
        # e.g., self.data_store = load_data()
        self.openai_client = self.initialize_openai_client()
        logger.info("OpenAI client initialized successfully.")

        logger.info("ChatService initialized.")
        # Placeholder: Load data (replace with actual loading)
        self.experiences_data = self._load_poc_data()
        # Placeholder: Initialize simple history store
        self.history = conversation_history_store


    def initialize_openai_client(self) -> openai.OpenAI:
        # --- Initialize OpenAI Client ---
        try:
            # Load API key from environment variable
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY environment variable not set.")
                # Depending on requirements, either raise an error or disable OpenAI features
                raise ValueError("OPENAI_API_KEY is not configured.")
            
            return openai.OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
            # Handle initialization failure appropriately
            return None

        
    def _load_poc_data(self) -> List[Dict[str, Any]]:
        # In a real scenario, load from CSV/Airtable/DB
        # For POC placeholder:
        logger.info("Loading placeholder POC data...")
        return [
            {"id": "EXP001", "name": "Canal Cruise", "description": "A relaxing boat tour through the canals.", "tags": ["scenic", "water"]},
            {"id": "ACT001", "name": "Rooftop Yoga", "description": "Morning yoga session with city views.", "tags": ["wellness", "relaxing", "morning"]},
            {"id": "ACT002", "name": "Cooking Class", "description": "Learn to cook local dishes.", "tags": ["food", "hands-on", "interactive"]},
        ]

    def _get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieves conversation history for a given session."""
        return self.history.get(session_id, []).copy() # Return a copy

    def _update_conversation_history(self, session_id: str, user_message: str, ai_reply: str):
        """Updates conversation history for a given session."""
        if session_id not in self.history:
            self.history[session_id] = []
        
        # Append user message
        self.history[session_id].append({"role": "user", "content": user_message})
        # Append assistant message
        self.history[session_id].append({"role": "assistant", "content": ai_reply})

        # --- TODO: Implement history truncation logic for token limits ---
        # e.g., keep only the last N turns


    def _retrieve_rag_context(self, message: str) -> str:
        """
        Placeholder for RAG retrieval.
        Queries vector store and fetches relevant data.
        """
        logger.info(f"Performing RAG retrieval for message: '{message}'")
        # --- TODO: Implement actual RAG logic ---
        # 1. Embed the user message.
        # 2. Query the vector store for relevant IDs.
        # 3. Fetch full data for those IDs from self.experiences_data or primary store.
        # 4. Format the retrieved data into a string context.

        # Placeholder context based on simple keyword matching (very basic)
        context_parts = []
        if "relaxing" in message.lower() or "yoga" in message.lower():
             context_parts.append(str(self.experiences_data[1])) # Yoga
        if "canal" in message.lower() or "boat" in message.lower():
             context_parts.append(str(self.experiences_data[0])) # Canal Cruise
        if "cook" in message.lower() or "food" in message.lower():
             context_parts.append(str(self.experiences_data[2])) # Cooking Class
        
        if not context_parts:
            return "No specific context found."
        
        return "Context: \n" + "\n".join(context_parts)


    def _call_openai_api(self, message: str, history: List[Dict[str, str]], context: str) -> str:
        """
        Calls the OpenAI Chat Completions API with context and history.
        """
        if not self.openai_client:
             logger.error("OpenAI client not initialized. Cannot call API.")
             return "Error: AI service connection failed." # Return error message

        # Define the system message - tailor this to your concierge's persona and rules
        system_message = {
            "role": "system",
            "content": (
                "You are a helpful and friendly AI Concierge for a luxury hotel. "
                "Your goal is to assist guests in planning their stay by recommending relevant hotel activities and local experiences. "
                "Use only the information provided in the 'Context' section below to answer questions about activities and experiences. "
                "Do not make up activities, prices, durations, or other details not present in the context. "
                "If the context doesn't contain relevant information to answer the user's query about activities/experiences, politely state that you don't have that specific information available. "
                "Keep your responses concise and helpful."
            )
        }
        
        # Prepare the messages list for the API call
        messages = [system_message]
        
        # Add relevant conversation history (ensure roles alternate user/assistant)
        messages.extend(history) 
        
        # Add the RAG context and the latest user message
        # Prepending context to the user message is one common way
        context_enhanced_message = f"Context:\n{context}\n\nUser Question: {message}"
        messages.append({"role": "user", "content": context_enhanced_message})

        logger.info(f"Sending request to OpenAI with {len(messages)} messages.")
        # Log the message structure for debugging if needed (can be verbose)
        # logger.debug(f"OpenAI Request Messages: {messages}")

        try:
            # Make the API call to OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Or use "gpt-4" or other suitable models
                messages=messages,
                temperature=0.7,  # Adjust creativity (0.0 = deterministic, 1.0 = more creative)
                max_tokens=150,  # Limit response length
            )
            
            # Extract the response content
            ai_reply = response.choices[0].message.content.strip()
            logger.info("Received response from OpenAI.")
            # logger.debug(f"OpenAI Raw Response Choice: {response.choices[0]}") # For detailed debugging
            return ai_reply if ai_reply else "I received an empty response, could you please rephrase?"

        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API request failed to connect: {e}")
            return "Error: Could not connect to the AI service."
        except openai.RateLimitError as e:
            logger.error(f"OpenAI API request exceeded rate limit: {e}")
            return "Error: The AI service is currently busy. Please try again later."
        except openai.AuthenticationError as e:
             logger.error(f"OpenAI API authentication failed: {e}. Check your API key.")
             return "Error: AI service authentication failed."
        except openai.APIStatusError as e:
            logger.error(f"OpenAI API returned an API Error: {e.status_code} - {e.response}")
            return f"Error: The AI service returned an error (Status: {e.status_code})."
        except Exception as e:
            # Catch any other unexpected errors during the API call
            logger.error(f"An unexpected error occurred during OpenAI API call: {e}", exc_info=True)
            return "Error: An unexpected error occurred while contacting the AI service."


    async def process_chat_message(self, session_id: str, user_message: str) -> str:
        """
        Main method to process an incoming chat message.
        Orchestrates history management, RAG, and OpenAI call.
        """
        logger.info(f"Processing message for session {session_id}: '{user_message}'")

        # 1. Retrieve conversation history
        history = self._get_conversation_history(session_id)

        # 2. Perform RAG retrieval
        context = self._retrieve_rag_context(user_message)

        # 3. Call OpenAI API (or placeholder)
        ai_reply = self._call_openai_api(user_message, history, context)

        # 4. Update conversation history
        self._update_conversation_history(session_id, user_message, ai_reply)

        logger.info(f"Generated reply for session {session_id}: '{ai_reply}'")
        return ai_reply

# --- Optional: Singleton pattern or dependency injection setup ---
# For simplicity in POC, we can create a single instance here
# In a larger app, use FastAPI's dependency injection
chat_service_instance = ChatService()

def get_chat_service() -> ChatService:
    """Dependency injector for the ChatService."""
    return chat_service_instance