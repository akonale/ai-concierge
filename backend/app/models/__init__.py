# backend/app/models.py

from pydantic import BaseModel, Field
from typing import Optional # Optional might be needed later

# Pydantic model for the request body of the chat endpoint
class ChatRequest(BaseModel):
    """
    Defines the expected structure for incoming chat requests.
    """
    message: str = Field(..., description="The message content from the user.")
    session_id: str = Field(..., description="A unique identifier for the ongoing chat session.")
    # Add other fields later if needed, e.g., user preferences

    # Example for Pydantic V2 configuration if needed
    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "message": "Tell me about relaxing activities.",
    #                 "session_id": "user123_session_abc"
    #             }
    #         ]
    #     }
    # }


# Pydantic model for the response body of the chat endpoint
class ChatResponse(BaseModel):
    """
    Defines the structure for the response sent back by the chat endpoint.
    """
    reply: str = Field(..., description="The AI-generated reply to the user's message.")
    session_id: str = Field(..., description="The session identifier, returned for confirmation.")
    transcribed_text: str = Field(..., description="Transcribed text for audio input")
    # Add other fields later if needed, e.g., suggested actions, debug info

    # Example for Pydantic V2 configuration if needed
    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "reply": "Certainly! We have Rooftop Yoga sessions that many guests find relaxing.",
    #                 "session_id": "user123_session_abc"
    #             }
    #         ]
    #     }
    # }