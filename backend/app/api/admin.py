# backend/app/api/admin.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
# Import the sync service and its dependency getter
from ..services.sync_service import SyncService, get_sync_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an API router for admin endpoints
router = APIRouter()

# --- Optional: Add basic security dependency ---
# from fastapi import Header, Security
# ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "default_insecure_key") # Load from env
# async def verify_admin_key(x_admin_key: str = Header(None)):
#     if not x_admin_key or x_admin_key != ADMIN_API_KEY:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Admin API Key")
# ---

@router.post(
    "/trigger-sync",
    summary="Manually Trigger Airtable-ChromaDB Sync",
    description="Triggers the full synchronization process between Airtable and ChromaDB in the background.",
    status_code=status.HTTP_202_ACCEPTED, # Return 202 Accepted as task runs in background
    # dependencies=[Security(verify_admin_key)], # Uncomment to enable API Key security
    tags=["Admin"] # Tag for grouping in API docs
)
async def trigger_sync(
    background_tasks: BackgroundTasks, # Inject background tasks handler
    sync_service: SyncService = Depends(get_sync_service) # Inject sync service
):
    """
    Manually triggers the full sync from Airtable to ChromaDB.
    The sync process runs in the background.
    """
    logger.info("Received request to manually trigger Airtable-ChromaDB sync.")

    # Add the potentially long-running sync task to the background
    background_tasks.add_task(sync_service.run_full_airtable_chroma_sync)

    logger.info("Full sync task added to background.")
    return {"message": "Airtable to ChromaDB synchronization triggered successfully in the background."}