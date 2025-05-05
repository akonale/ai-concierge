# backend/app/services/chat_service.py

import os
from typing import Dict, List, Any, Optional, Tuple
import logging
import io # Add io

import chromadb
from fastapi import HTTPException
import openai

from ..utils.mapping import map_airtable_to_card_data

from ..models.models import ExperienceCardData # For logging information
from .airtable_service import AirtableService,airtable_service_instance
from sentence_transformers import SentenceTransformer # Import sentence transformer
from starlette import status

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

    def __init__(self, airtable_service: AirtableService):
        # Initialize necessary components here later
        # e.g., self.vector_store = initialize_vector_store()
        # e.g., self.data_store = load_data()
        self.airtable_service = airtable_service
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

    # --- Updated RAG Context Retrieval ---
    # Now returns a tuple: (context_string, list_of_retrieved_airtable_records)
    def _retrieve_rag_context(self, message: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Performs RAG retrieval. Embeds query, queries ChromaDB for IDs,
        fetches full details from Airtable, formats text context,
        and returns both the text context and the raw Airtable records (with IDs).
        """
        default_error_return = ("Error: Could not perform context retrieval.", [])
        if not self.embedding_model or not self.chroma_collection or not self.airtable_service:
             logger.error("RAG components not fully initialized in ChatService.")
             return default_error_return

        logger.info(f"Performing RAG retrieval for message: '{message}'")
        retrieved_airtable_records: List[Dict[str, Any]] = [] # Store full records here {id: ..., **fields}
        context_parts = []
        try:
            # 1. Embed the user query
            query_embedding = self.embedding_model.encode(message).tolist()

            # 2. Query ChromaDB for relevant IDs
            results = self.chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=NUM_RAG_RESULTS,
                include=[] # Only need IDs (which are Airtable Record IDs)
            )
            retrieved_ids = results.get('ids', [[]])[0]

            if not retrieved_ids:
                logger.info("No relevant document IDs found in ChromaDB.")
                return ("No specific context found in the knowledge base.", []) # Return empty list

            logger.info(f"Retrieved {len(retrieved_ids)} IDs from ChromaDB: {retrieved_ids}")

            # 3. Fetch full details from Airtable using the retrieved IDs
            for i, record_id in enumerate(retrieved_ids):
                airtable_fields = self.airtable_service.get_record(record_id)
                if airtable_fields:
                    # Store the full record fields along with its ID for later processing
                    record_with_id = {"id": record_id, **airtable_fields}
                    retrieved_airtable_records.append(record_with_id)

                    # Format context string for LLM using fresh Airtable data
                    # Adjust field names based on your actual Airtable base structure
                    context_line = (
                        f"[Result {i+1} (ID: {record_id}): "
                        f"Name: {airtable_fields.get('Experience Name', 'N/A')}, " # Example field name
                        f"Description: {airtable_fields.get('Description', 'N/A')}, "
                        f"Price: {airtable_fields.get('Price', 'N/A')}, "
                        f"Type: {airtable_fields.get('Type', 'N/A')}"
                        # Add other key fields useful for LLM context
                        f"]"
                    )
                    context_parts.append(context_line)
                else:
                    # Log if an ID retrieved from Chroma doesn't exist in Airtable (might happen if sync is delayed)
                    logger.warning(f"Could not fetch Airtable details for retrieved ID: {record_id}. It might have been deleted.")

            if not context_parts:
                logger.info("No details found in Airtable for the retrieved IDs.")
                return ("Context details could not be retrieved.", []) # Return empty list

            formatted_context = "Context from knowledge base:\n" + "\n".join(context_parts)
            logger.info(f"Formatted RAG context using Airtable data:\n{formatted_context}")
            # Return both the context string and the list of full records
            return formatted_context, retrieved_airtable_records

        except Exception as e:
            logger.error(f"Error during RAG retrieval: {e}", exc_info=True)
            # Return error string and empty list
            return ("Error: Failed to retrieve context information.", [])

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
        suggested_experiences_data = []
        try: 
            # 1. Retrieve conversation history
            history = self._get_conversation_history(session_id)

            # 2. Perform RAG retrieval - Returns (context_str, airtable_records)
            context_str, airtable_records = self._retrieve_rag_context(user_message)

            # Handle potential errors from RAG retrieval itself
            if context_str.startswith("Error:"):
                    ai_text_reply = context_str # Pass the RAG error message back
                    # Don't proceed to OpenAI call if context retrieval failed
            else:
                # 3. Call OpenAI API with the text context
                ai_text_reply = self._call_openai_api(user_message, history, context_str)

                # 4. Prepare structured data if RAG returned records and OpenAI call didn't error
                if airtable_records and not ai_text_reply.startswith("Error:"):
                    suggestions = []
                    for record in airtable_records:
                        card_data = map_airtable_to_card_data(record)
                        if card_data: # Only add if mapping was successful
                            suggestions.append(card_data)

                    if suggestions: # Only assign if we successfully created some cards
                            suggested_experiences_data = suggestions
                            logger.info(f"Prepared {len(suggested_experiences_data)} structured suggestions.")
                    else:
                            logger.warning("RAG retrieved records, but failed to map any to card data.")
            # 5. Update conversation history (only if AI reply wasn't an error)
            if not ai_text_reply.startswith("Error:"):
                    self._update_conversation_history(session_id, user_message, ai_text_reply)
            else:
                logger.warning(f"Did not save error reply to history for session {session_id}")
        except Exception as e:
            logger.error(f"Unexpected error in process_chat_message for session {session_id}: {e}", exc_info=True)
            ai_text_reply = "An unexpected error occurred while processing your message."
            suggested_experiences_data = None # Ensure suggestions are None on error

        logger.info(f"Generated reply for session {session_id}: '{ai_text_reply}'")
        # Return both the text reply and the structured data
        return ai_text_reply, suggested_experiences_data



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
            chroma_collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
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
chat_service_instance = None
if airtable_service_instance: # Check if AirtableService initialized correctly
    try:
        # Pass the airtable_service_instance to the constructor
        chat_service_instance = ChatService(airtable_service_instance)
    except RuntimeError as e:
        logger.critical(f"Failed to initialize ChatService: {e}")
        chat_service_instance = None
else:
     logger.critical("Cannot initialize ChatService because AirtableService failed to initialize.")


def get_chat_service() -> ChatService:
    """Dependency injector for the ChatService."""
    if chat_service_instance is None:
         # Raise appropriate HTTP exception if service failed to initialize
         raise HTTPException(
             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
             detail="Chat service is not available due to initialization errors."
         )
    return chat_service_instance