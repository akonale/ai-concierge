# backend/main.py

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware
from dotenv import load_dotenv # Import load_dotenv
import os # Import os to access environment variables
import uvicorn
from contextlib import asynccontextmanager # For lifespan events
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Environment Variable Loading ---
# Load variables from .env file into environment
# Place this *before* initializing services that might need the variables
load_dotenv()
# Example: Accessing the API key (do this inside services where needed)
# openai_api_key = os.getenv("OPENAI_API_KEY")
# if not openai_api_key:
#    print("Warning: OPENAI_API_KEY environment variable not set.")

from app.services.sync_service import get_sync_service # Import scheduler

# --- Scheduler Setup ---
scheduler = AsyncIOScheduler()

# --- Lifespan Management (for starting/stopping scheduler) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Application startup...")
    try:
        # Ensure services (especially sync) are ready before scheduling
        sync_service = get_sync_service() # This will raise HTTPException if init failed
        logger.info("Sync service initialized successfully.")

        # Add the sync job to the scheduler
        # Example: Run every hour (adjust interval as needed)
        scheduler.add_job(
            sync_service.run_full_airtable_chroma_sync, # The function to run
            'interval',                                # Trigger type
            hours=1,                                   # Interval
            id='airtable_sync_job',                    # Unique ID for the job
            replace_existing=True                      # Replace job if it already exists on restart
        )
        # Start the scheduler
        scheduler.start()
        logger.info(f"Scheduler started with job '{scheduler.get_job('airtable_sync_job').id}' running every 1 hour(s).")
    except Exception as e:
         # Log critical failure if scheduler or service init fails
         logger.critical(f"Failed to initialize services or start scheduler: {e}", exc_info=True)
         # Depending on requirements, you might want the app to stop here
         # For now, it will continue but scheduling won't work if setup failed
    yield
    # Shutdown logic
    logger.info("Application shutdown...")
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down.")
    else:
        logger.info("Scheduler was not running.")


# --- Import API Routers ---
# Make sure the path is correct based on your structure
# Assuming your chat router is in backend/app/api/chat.py
from app.api import chat as chat_api # Import the chat router
# Assuming your admin router is in backend/app/api/admin.py
from app.api import admin as admin_api # Import the admin router

# Create the FastAPI application instance
app = FastAPI(
    title="AI Concierge Backend",
    description="API endpoints for the AI Concierge application.",
    version="0.1.0",
)

# --- CORS Middleware Configuration ---
# Define the list of origins allowed to make requests to this backend.
# For development, this includes your frontend's address.
# Use environment variables for production origins.
origins = [
    "http://localhost:3000", # Default Next.js port (if used)
    "http://localhost:3001", # The origin reported in your error message
    # Add other origins as needed (e.g., your deployed frontend URL)
    "https://ai-concierge-frontend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of allowed origins
    allow_credentials=True, # Allow cookies to be included in requests
    allow_methods=["*"], # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allow all headers
)
# --- End CORS Middleware Configuration ---

# --- Include API Routers ---
# Include the chat router with a prefix
# All routes defined in chat_api.router will now be accessible under /api/v1
app.include_router(chat_api.router, prefix="/api/v1", tags=["Chat"])
# Include the admin router
app.include_router(admin_api.router, prefix="/api/v1/admin", tags=["Admin"])
# Add other routers here later (e.g., for data management)


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
