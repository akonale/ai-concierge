# backend/app/api/chat.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from ..models import ChatRequest, ChatResponse # Use relative import from models.py
from ..services.chat_service import ChatService, get_chat_service # Import service and dependency getter
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an API router
# All routes defined here will be prefixed with /api/v1 (defined in main.py)
router = APIRouter()

@router.post(
    "/chat",
    response_model=ChatResponse, # Specify the response model
    summary="Process a user chat message",
    description="Receives a message from the user, processes it using RAG and OpenAI, and returns the AI's reply.",
    tags=["Chat"] # Tag for grouping in API docs
)
async def handle_chat_message(
    request: ChatRequest, # Use the Pydantic model for request body validation
    chat_service: ChatService = Depends(get_chat_service) # Inject ChatService dependency
) -> ChatResponse:
    """
    Handles incoming chat requests.

    - Validates the request body using the `ChatRequest` model.
    - Uses the injected `ChatService` to process the message.
    - Returns the AI's reply structured according to the `ChatResponse` model.
    """
    logger.info(f"Received chat request for session: {request.session_id}")
    try:
        # Process the message using the chat service
        # ChatService.process_chat_message now returns a tuple:
        # (ai_text_reply, list_of_experience_card_data | None)
        ai_reply_text, suggestions = await chat_service.process_chat_message(
            session_id=request.session_id,
            user_message=request.message
        )

        # Return the successful response using the updated ChatResponse model
        return ChatResponse(
            reply=ai_reply_text,
            session_id=request.session_id,
            transcribed_text=request.message,
            suggested_experiences=suggestions # Pass the list (or None) received from the service
        )

    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error processing chat message for session {request.session_id}: {e}", exc_info=True)
        # Raise an HTTPException for FastAPI to handle
        # Return a generic error message to the client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your message."
        )

@router.post(
    "/audio",
    response_model=ChatResponse,
    response_model_exclude_none=False, # Ensure 'transcribed_text: null' is included if transcription fails
    summary="Process a user audio message",
    description="Receives an audio file and session ID, transcribes the audio using OpenAI Whisper, processes the transcribed text using RAG and OpenAI Chat Completion, and returns the AI's reply.",
    tags=["Chat"]
)
async def handle_audio_message(
    session_id: str = Form(...), # Get session_id from form data
    audio_file: UploadFile = File(...), # Get audio file from form data
    chat_service: ChatService = Depends(get_chat_service) # Inject ChatService
) -> ChatResponse:
    """
    Handles incoming audio chat requests.

    - Receives audio file and session ID as form data.
    - Reads the audio file content.
    - Uses the injected `ChatService` to transcribe and process the audio message.
    - Returns the AI's reply structured according to the `ChatResponse` model.
    """
    logger.info(f"Received audio chat request for session: {session_id}, filename: {audio_file.filename}")

    # Validate file type if necessary (e.g., check audio_file.content_type)
    # Example:
    # if not audio_file.content_type.startswith("audio/"):
    #     logger.warning(f"Invalid file type received for session {session_id}: {audio_file.content_type}")
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Invalid file type. Please upload an audio file."
    #     )

    try:
        # Read the audio file content as bytes
        audio_bytes = await audio_file.read()
        if not audio_bytes:
             logger.warning(f"Received empty audio file for session {session_id}")
             raise HTTPException(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 detail="Received an empty audio file."
             )

        # Process the audio message using the chat service
        # Assume this now returns a tuple: (transcribed_text, ai_reply, suggestions)
        transcribed_text, ai_reply, suggestions = await chat_service.process_audio_message(
            session_id=session_id,
            audio_bytes=audio_bytes,
            filename=audio_file.filename # Pass filename
        )

        logger.info(f"Sending back {session_id} from audio: '{ai_reply}' for question: '{transcribed_text}' with suggestions: {suggestions is not None}")
        # Return the successful response, including the transcribed text and suggestions
        return ChatResponse(
            reply=ai_reply,
            session_id=session_id,
            transcribed_text=transcribed_text, # Include the transcription
            suggested_experiences=suggestions # Include the suggestions
        )

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions directly (e.g., from file validation or service layer)
        raise http_exc
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error processing audio message for session {session_id}: {e}", exc_info=True)
        # Raise an HTTPException for FastAPI to handle
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your audio message."
        )
