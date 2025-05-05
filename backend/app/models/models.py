# backend/app/models.py

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List # Import List

# --- New Model for Experience Card Data ---
class ExperienceCardData(BaseModel):
    """
    Defines the structured data for a single experience card
    to be displayed in the frontend sidebar.
    Field names should align with Airtable fields or prepared metadata.
    """
    id: str = Field(..., description="The unique identifier (Airtable Record ID).")
    name: str = Field(..., description="The name of the experience or activity.")
    description: Optional[str] = Field(None, description="A brief description.")
    # Assuming image URL comes from an 'Attachments' field or a specific URL field
    image_url: Optional[HttpUrl | str] = Field(None, description="URL of the primary image.") # Use HttpUrl for validation if possible
    price: Optional[str] = Field(None, description="Price information (as string).")
    duration: Optional[str] = Field(None, description="Duration information (as string).")
    type: Optional[str] = Field(None, description="Category or type of the experience.")
    url: Optional[HttpUrl | str] = Field(None, description="Link for booking or more details.")
    # Add other fields as needed based on brainstorming, e.g., location, vendor

    # Pydantic V2 config example
    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "id": "recXXXXXXXXXXXXXX",
    #                 "name": "Rooftop Yoga",
    #                 "description": "Morning yoga session with city views.",
    #                 "image_url": "https://example.com/yoga.jpg",
    #                 "price": "€25",
    #                 "duration": "60 min",
    #                 "type": "Wellness",
    #                 "url": "https://example.com/book-yoga"
    #             }
    #         ]
    #     }
    # }


# --- Updated Chat Request Model ---
class ChatRequest(BaseModel):
    """
    Defines the expected structure for incoming chat requests.
    """
    message: str = Field(..., description="The message content from the user.")
    session_id: str = Field(..., description="A unique identifier for the ongoing chat session.")


# --- Updated Chat Response Model ---
class ChatResponse(BaseModel):
    """
    Defines the structure for the response sent back by the chat endpoint.
    Includes the text reply and optionally structured data for suggested experiences.
    """
    reply: str = Field(..., description="The AI-generated text reply to the user's message.")
    session_id: str = Field(..., description="The session identifier, returned for confirmation.")
    # Add the list of suggested experiences
    suggested_experiences: Optional[List[ExperienceCardData]] = Field(None, description="List of structured data for experiences suggested in the reply.")

    # Pydantic V2 config example
    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "reply": "Certainly! We have Rooftop Yoga sessions (€25, 60 min) that many guests find relaxing.",
    #                 "session_id": "user123_session_abc",
    #                 "suggested_experiences": [
    #                     {
    #                         "id": "recXXXXXXXXXXXXXX",
    #                         "name": "Rooftop Yoga",
    #                         "description": "Morning yoga session with city views.",
    #                         "image_url": "https://example.com/yoga.jpg",
    #                         "price": "€25",
    #                         "duration": "60 min",
    #                         "type": "Wellness",
    #                         "url": "https://example.com/book-yoga"
    #                     }
    #                 ]
    #             }
    #         ]
    #     }
    # }
