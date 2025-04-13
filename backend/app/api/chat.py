# backend/app/api/chat.py

from fastapi import APIRouter, Depends, HTTPException, status
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
        ai_reply = await chat_service.process_chat_message(
            session_id=request.session_id,
            user_message=request.message
        )

        # Return the successful response
        return ChatResponse(reply=ai_reply, session_id=request.session_id)

    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error processing chat message for session {request.session_id}: {e}", exc_info=True)
        # Raise an HTTPException for FastAPI to handle
        # Return a generic error message to the client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your message."
        )

