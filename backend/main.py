# backend/main.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv # Import load_dotenv
import os # Import os to access environment variables
import uvicorn

# --- Environment Variable Loading ---
# Load variables from .env file into environment
# Place this *before* initializing services that might need the variables
load_dotenv()
# Example: Accessing the API key (do this inside services where needed)
# openai_api_key = os.getenv("OPENAI_API_KEY")
# if not openai_api_key:
#    print("Warning: OPENAI_API_KEY environment variable not set.")


# --- Import API Routers ---
# Make sure the path is correct based on your structure
# Assuming your chat router is in backend/app/api/chat.py
from app.api import chat as chat_api # Import the chat router

# Create the FastAPI application instance
app = FastAPI(
    title="AI Concierge Backend",
    description="API endpoints for the AI Concierge application.",
    version="0.1.0",
)

# --- Include API Routers ---
# Include the chat router with a prefix
# All routes defined in chat_api.router will now be accessible under /api/v1
app.include_router(chat_api.router, prefix="/api/v1", tags=["Chat"])
# Add other routers here later (e.g., for admin, data management)


# Define a simple root endpoint for health checks or basic info
@app.get("/")
async def read_root():
    """
    Root endpoint providing a welcome message.
    Can be used for basic health checks.
    """
    return JSONResponse(content={"message": "Welcome to the AI Concierge Backend!"})

# Define another simple endpoint (example)
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    return JSONResponse(content={"status": "ok"})

# --- Optional: Add main execution block for direct running ---
# This allows running `python main.py` but `uvicorn main:app --reload` is preferred for development
# if __name__ == "__main__":
#     # Use string format "main:app" for uvicorn reload to work correctly
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)