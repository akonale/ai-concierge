# backend/app/services/chat_service.py

import os
from typing import Dict, List, Any, Optional
import logging
import io # Add io

import chromadb
import openai # For logging information
from sentence_transformers import SentenceTransformer # Import sentence transformer

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration for ChromaDB and Embeddings ---
# Load ChromaDB connection details from environment variables
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost") # Default to localhost
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))    # Default to 8000
# Name for the ChromaDB collection used in the loading script
COLLECTION_NAME = "experiences"
# Pre-trained model used for generating embeddings in the loading script
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
# Number of relevant documents to retrieve from ChromaDB
NUM_RAG_RESULTS = 3

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
        self.chroma_client, self.chroma_collection = self.initialize_chroma_client()
        self.embedding_model = self.initialize_embedding_model()
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
        Performs RAG retrieval using ChromaDB (via HTTP client).
        Embeds the query message and queries the ChromaDB collection.
        Formats the results into a context string for the LLM.
        """
        if not self.embedding_model or not self.chroma_collection:
            logger.error("RAG components (embedding model or Chroma collection) not initialized.")
            return "Error: Could not perform context retrieval."

        logger.info(f"Performing RAG retrieval for message: '{message}'")
        try:
            # 1. Embed the user query
            query_embedding = self.embedding_model.encode(message).tolist()

            # 2. Query ChromaDB
            results = self.chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=NUM_RAG_RESULTS,
                include=['metadatas', 'documents', 'distances']  # Include desired data
            )

            # 3. Process and Format Results
            retrieved_metadatas = results.get('metadatas', [[]])[0]  # Get list of metadata dicts
            # retrieved_documents = results.get('documents', [[]])[0] # Get list of document texts
            # retrieved_distances = results.get('distances', [[]])[0] # Get list of distances (lower is better)

            if not retrieved_metadatas:
                logger.info("No relevant documents found in ChromaDB for the query.")
                return "No specific context found in the knowledge base."

            # Format the context string
            context_parts = []
            logger.info(f"Retrieved {len(retrieved_metadatas)} results from ChromaDB.")
            for i, meta in enumerate(retrieved_metadatas):
                # Customize this formatting based on what's most useful from your metadata
                context_line = (
                    f"[Result {i + 1}: "
                    f"Name: {meta.get('experience_name', 'N/A')}, "
                    f"Description: {meta.get('description', 'N/A')}, "
                    # Add other relevant metadata fields loaded previously
                    f"Price: {meta.get('price', 'N/A')}, "
                    f"Type: {meta.get('type', 'N/A')}"
                    # f"Distance: {retrieved_distances[i]:.4f}" # Optionally include distance
                    f"]"
                )
                context_parts.append(context_line)

            formatted_context = "Context from knowledge base:\n" + "\n".join(context_parts)
            logger.info(f"Formatted RAG context:\n{formatted_context}")
            return formatted_context

        except Exception as e:
            logger.error(f"Error during RAG retrieval: {e}", exc_info=True)
            return "Error: Failed to retrieve context information."

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


    async def transcribe_audio(self, audio_bytes: bytes, filename: str = "audio.webm") -> str:
        """
        Transcribes audio bytes using the OpenAI Whisper API.
        Requires audio_bytes and a filename hint for the API.
        """
        if not self.openai_client:
            logger.error("OpenAI client not initialized. Cannot transcribe audio.")
            return "Error: AI service connection failed."

        logger.info(f"Transcribing audio file '{filename}' ({len(audio_bytes)} bytes)...")
        try:
            # Wrap bytes in a file-like object for the API
            audio_file = io.BytesIO(audio_bytes)
            # Provide a filename, which Whisper uses to infer format/type
            # The tuple format is (filename, file-like object)
            audio_file.name = filename
            transcription = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            logger.info(f"Transcription successful: '{transcription}'")
            return transcription
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API request failed to connect during transcription: {e}")
            return "Error: Could not connect to the AI service for transcription."
        except openai.RateLimitError as e:
            logger.error(f"OpenAI API request exceeded rate limit during transcription: {e}")
            return "Error: The AI service is currently busy. Please try again later."
        except openai.AuthenticationError as e:
             logger.error(f"OpenAI API authentication failed during transcription: {e}. Check your API key.")
             return "Error: AI service authentication failed."
        except openai.APIStatusError as e:
            logger.error(f"OpenAI API returned an API Error during transcription: {e.status_code} - {e.message}")
            return f"Error: The AI service returned an error during transcription (Status: {e.status_code})."
        except Exception as e:
            logger.error(f"An unexpected error occurred during OpenAI transcription: {e}", exc_info=True)
            return "Error: An unexpected error occurred during audio transcription."


    async def process_audio_message(self, session_id: str, audio_bytes: bytes, filename: str) -> tuple[str, str]:
        """
        Processes an incoming audio message.
        Transcribes audio, uses the text for RAG and chat completion.
        Returns a tuple: (transcribed_text, ai_reply).
        If transcription fails, transcribed_text will be an empty string "" and ai_reply will contain the error.
        """
        logger.info(f"Processing audio message for session {session_id} (filename: {filename})")
        transcribed_text: str = "" # Initialize as empty string
        ai_reply: str

        # 1. Transcribe Audio
        try:
            transcribed_text = await self.transcribe_audio(audio_bytes, filename)
            # Check for transcription errors returned as strings
            # Check for transcription errors returned as strings
            if transcribed_text.startswith("Error:"):
                logger.error(f"Transcription failed for session {session_id}: {transcribed_text}")
                ai_reply = f"Audio Processing Error: {transcribed_text}"
                transcribed_text = "" # Ensure transcription is empty string on error
                return transcribed_text, ai_reply # Return error early
            # If transcription returns an empty string legitimately, keep it as ""
            logger.info(f"Transcribed text for session {session_id}: '{transcribed_text}'")
        except Exception as e:
             logger.error(f"Unexpected error during transcription call for session {session_id}: {e}", exc_info=True)
             ai_reply = "Error: An unexpected issue occurred during audio transcription."
             return "", ai_reply # Return empty string and error early

        # --- Now use the transcribed text like a regular message ---
        # No need to check for None anymore, proceed with the (potentially empty) string

        # 2. Retrieve conversation history
        history = self._get_conversation_history(session_id)

        # 3. Perform RAG retrieval using the transcribed text
        context = self._retrieve_rag_context(transcribed_text)

        # 4. Call OpenAI API with transcribed text, history, and context
        ai_reply = self._call_openai_api(transcribed_text, history, context)

        # 5. Update conversation history (using transcribed text as user message)
        # Only update history if both transcription and reply were successful
        if not ai_reply.startswith("Error:"):
             self._update_conversation_history(session_id, transcribed_text, ai_reply)

        logger.info(f"Generated reply for session {session_id} from audio: '{ai_reply}' for question: '{transcribed_text}'")
        return transcribed_text, ai_reply

    def initialize_embedding_model(self):
        # --- Initialize Embedding Model ---
        try:
            logger.info(f"Loading sentence transformer model: {EMBEDDING_MODEL_NAME}...")
            # You can specify cache_folder='./embedding_models' to control download location
            embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info("Sentence transformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer model: {e}", exc_info=True)
            # Decide how to handle failure - maybe service can't start?
            raise RuntimeError(f"Could not load embedding model {EMBEDDING_MODEL_NAME}") from e
        return embedding_model

    def initialize_chroma_client(self):
        # --- Initialize ChromaDB HTTP Client & Collection ---
        try:
            logger.info(f"Initializing ChromaDB HTTP client for host: {CHROMA_HOST}, port: {CHROMA_PORT}")
            # Use HttpClient instead of PersistentClient
            chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            # Optional: Ping the server to check connection early
            chroma_client.heartbeat() # Throws exception if connection fails
            logger.info("ChromaDB server connection successful.")

            logger.info(f"Getting ChromaDB collection: {COLLECTION_NAME}")
            # Check if collection exists before getting (optional but good practice)
            # Note: get_collection throws exception if it doesn't exist.
            # get_or_create_collection is safer if unsure if loading script ran.
            chroma_collection = chroma_client.get_collection(name=COLLECTION_NAME)
            logger.info(f"ChromaDB collection '{COLLECTION_NAME}' loaded successfully.")
            # Verify collection has items (optional)
            count = chroma_collection.count()
            logger.info(f"Collection contains {count} items.")
            if count == 0:
                 logger.warning(f"ChromaDB collection '{COLLECTION_NAME}' is empty. Did the loading script run successfully against the Docker instance?")
            return chroma_client, chroma_collection

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB HTTP client or get collection: {e}", exc_info=True)
            # Decide how to handle failure
            raise RuntimeError(f"Could not connect to or load ChromaDB collection at {CHROMA_HOST}:{CHROMA_PORT}") from e



# --- Optional: Singleton pattern or dependency injection setup ---
# For simplicity in POC, we can create a single instance here
# In a larger app, use FastAPI's dependency injection
chat_service_instance = ChatService()

def get_chat_service() -> ChatService:
    """Dependency injector for the ChatService."""
    return chat_service_instance
