# backend/app/services/sync_service.py

import logging
from typing import Set
from .airtable_service import AirtableService, get_airtable_service # Import Airtable service
# Need access to ChromaDB collection and embedding model
# Option 1: Inject ChatService (simpler for POC if ChatService holds them)
# from .chat_service import ChatService
# Option 2: Initialize Chroma/Embedding model here directly (better separation)
import chromadb
from sentence_transformers import SentenceTransformer
import os
from fastapi import HTTPException
from starlette import status


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration --- (Duplicated from chat_service for clarity, could centralize)
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = os.getenv("CHROMA_PORT", "8000")
COLLECTION_NAME = "experiences"
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

class SyncService:
    """
    Handles synchronization tasks between Airtable and ChromaDB.
    """
    def __init__(self, airtable_service: AirtableService):
        """
        Initializes the SyncService.
        Requires AirtableService. Initializes its own Chroma/Embedding clients.
        """
        self.airtable_service = airtable_service
        self.embedding_model = None
        self.chroma_collection = None

        # --- Initialize Embedding Model ---
        try:
            logger.info(f"(SyncService) Loading sentence transformer model: {EMBEDDING_MODEL_NAME}...")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info("(SyncService) Sentence transformer model loaded.")
        except Exception as e:
            logger.error(f"(SyncService) Failed to load embedding model: {e}", exc_info=True)
            raise RuntimeError("SyncService could not load embedding model") from e

        # --- Initialize ChromaDB Client & Collection ---
        try:
            logger.info(f"(SyncService) Initializing ChromaDB HTTP client for host: {CHROMA_HOST}, port: {CHROMA_PORT}")
            chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
            chroma_client.heartbeat() # Check connection
            logger.info("(SyncService) ChromaDB server connection successful.")
            self.chroma_collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME) # Use get_or_create
            logger.info(f"(SyncService) ChromaDB collection '{COLLECTION_NAME}' ready.")
        except Exception as e:
            logger.error(f"(SyncService) Failed to initialize ChromaDB client or get collection: {e}", exc_info=True)
            raise RuntimeError("SyncService could not connect to or load ChromaDB collection") from e

    def _prepare_chroma_metadata(self, airtable_fields: dict) -> dict:
        """
        Extracts and formats metadata from Airtable fields for ChromaDB.
        Ensures values are compatible types (str, int, float, bool).
        """
        metadata = {}
        # Map Airtable fields to ChromaDB metadata keys
        # Adjust field names based on your actual Airtable base
        metadata['experience_name'] = str(airtable_fields.get("Experience Name", "")) # Use field names from Step 1
        metadata['description'] = str(airtable_fields.get("Description", ""))
        metadata['duration'] = str(airtable_fields.get("Duration", ""))
        metadata['price'] = str(airtable_fields.get("Price", ""))
        metadata['type'] = str(airtable_fields.get("Type", ""))
        metadata['url'] = str(airtable_fields.get("URL", ""))
        metadata['vendor'] = str(airtable_fields.get("Vendor", ""))
        # Add any other fields you want searchable/filterable in Chroma
        # Example: Convert tags if they are a list
        # tags = airtable_fields.get("Tags") # Assuming 'Tags' is the field name
        # if isinstance(tags, list):
        #     metadata['tags'] = ",".join(tags) # Store as comma-separated string if needed
        # elif isinstance(tags, str):
        #      metadata['tags'] = tags

        # Ensure all values are basic types
        for key, value in metadata.items():
            if not isinstance(value, (str, int, float, bool)):
                 logger.warning(f"Metadata field '{key}' has incompatible type {type(value)}, converting to string.")
                 metadata[key] = str(value)

        return metadata

    async def run_full_airtable_chroma_sync(self):
        """
        Performs a full synchronization between Airtable and ChromaDB.
        Fetches all records, identifies changes, and updates ChromaDB.
        """
        logger.info("--- Starting Full Airtable -> ChromaDB Sync ---")
        if not self.embedding_model or not self.chroma_collection or not self.airtable_service:
            logger.error("SyncService components not initialized. Aborting sync.")
            return

        try:
            # 1. Get all current Record IDs from Airtable (consider filtering for 'Active' status)
            # Example filter: filter_formula="{Status}='Active'" (adjust field name)
            airtable_ids: Set[str] = set(self.airtable_service.get_all_record_ids())
            logger.info(f"Found {len(airtable_ids)} records in Airtable.")
            if not airtable_ids:
                logger.warning("No records found in Airtable table. Check configuration or table content.")
                # Decide if you want to wipe ChromaDB or just log
                # self.chroma_collection.delete(where={}) # Example: Delete all if Airtable is empty
                # return

            # 2. Get all current IDs from ChromaDB
            chroma_results = self.chroma_collection.get(include=[]) # Only need IDs
            chroma_ids: Set[str] = set(chroma_results.get('ids', []))
            logger.info(f"Found {len(chroma_ids)} records in ChromaDB collection '{COLLECTION_NAME}'.")

            # 3. Identify Deletions (in ChromaDB but not in Airtable)
            ids_to_delete = list(chroma_ids - airtable_ids)
            if ids_to_delete:
                logger.info(f"Identified {len(ids_to_delete)} records to delete from ChromaDB.")
                try:
                    self.chroma_collection.delete(ids=ids_to_delete)
                    logger.info(f"Successfully deleted {len(ids_to_delete)} records from ChromaDB.")
                except Exception as e:
                    logger.error(f"Failed to delete records from ChromaDB: {e}", exc_info=True)
            else:
                logger.info("No records identified for deletion from ChromaDB.")

            # 4. Identify Additions/Updates (all records currently in Airtable)
            # We will fetch all and upsert, letting ChromaDB handle add vs update.
            # Fetch full records from Airtable (consider filtering for active again)
            # Fetching all can be slow for large tables - consider fetching only needed fields
            # airtable_records = self.airtable_service.get_all_records() # Fetch all fields for now
            # logger.info(f"Processing {len(airtable_records)} records from Airtable for upsert...")

            upsert_ids = []
            upsert_embeddings = []
            upsert_metadatas = []
            upsert_documents = []

            # --- SIMPLER (but less efficient) approach for now: Iterate IDs and fetch ---
            # A more efficient approach would modify get_all_records to return IDs + fields
            logger.info(f"Processing records for upsert (fetching one by one)...")
            processed_count = 0
            for record_id in airtable_ids:
                 record_fields = self.airtable_service.get_record(record_id)
                 if not record_fields:
                     logger.warning(f"Could not fetch details for Airtable ID {record_id} during upsert loop. Skipping.")
                     continue

                 # Prepare text, embedding, metadata
                 # Adjust field names based on your actual Airtable base
                 text_to_embed = f"{record_fields.get('Experience Name', '')} - {record_fields.get('Description', '')}"
                 if not text_to_embed or text_to_embed == " - ":
                     logger.warning(f"Record '{record_id}' has empty name/description. Skipping embedding.")
                     continue

                 try:
                     embedding = self.embedding_model.encode(text_to_embed).tolist()
                     metadata = self._prepare_chroma_metadata(record_fields) # Use helper method

                     upsert_ids.append(record_id)
                     upsert_embeddings.append(embedding)
                     upsert_metadatas.append(metadata)
                     upsert_documents.append(text_to_embed) # Store text used for embedding
                     processed_count += 1

                 except Exception as e:
                     logger.error(f"Failed to process record '{record_id}' for upsert: {e}", exc_info=True)

            # 5. Perform Batch Upsert
            if upsert_ids:
                logger.info(f"Upserting {len(upsert_ids)} records into ChromaDB...")
                try:
                    self.chroma_collection.upsert(
                        ids=upsert_ids,
                        embeddings=upsert_embeddings,
                        metadatas=upsert_metadatas,
                        documents=upsert_documents
                    )
                    logger.info("Successfully upserted records into ChromaDB.")
                except Exception as e:
                    logger.error(f"Failed to upsert batch into ChromaDB: {e}", exc_info=True)
            else:
                logger.info("No valid records to upsert into ChromaDB.")

        except Exception as e:
            logger.error(f"An error occurred during the full sync process: {e}", exc_info=True)

        logger.info("--- Full Airtable -> ChromaDB Sync Finished ---")

    async def sync_record_to_chroma(self, record_id: str):
        """
        Fetches a record from Airtable and upserts it into ChromaDB.
        """
        logger.info(f"Syncing Airtable record '{record_id}' to ChromaDB...")
        if not self.embedding_model or not self.chroma_collection:
            logger.error("SyncService RAG components not initialized.")
            # Maybe raise an exception to signal failure back to webhook caller
            raise RuntimeError("SyncService components not ready.")

        # 1. Fetch record from Airtable
        airtable_fields = self.airtable_service.get_record(record_id)

        if not airtable_fields:
            # Record might have been deleted between webhook trigger and processing
            logger.warning(f"Record '{record_id}' not found in Airtable. Skipping sync (might be deleted).")
            # Consider deleting from ChromaDB here if desired, though periodic cleanup is safer
            # try:
            #     self.chroma_collection.delete(ids=[record_id])
            #     logger.info(f"Deleted potentially orphaned record '{record_id}' from ChromaDB.")
            # except Exception as e:
            #     logger.error(f"Failed to delete record '{record_id}' from ChromaDB: {e}")
            return # Stop processing this record

        # 2. Prepare text for embedding (e.g., combine name and description)
        # Adjust field names based on your Airtable base
        text_to_embed = f"{airtable_fields.get('Experience Name', '')} - {airtable_fields.get('Description', '')}"
        if not text_to_embed or text_to_embed == " - ":
            logger.warning(f"Record '{record_id}' has empty name/description. Skipping embedding.")
            # Decide if you still want to store it without embedding or skip entirely
            return

        # 3. Generate Embedding
        try:
            embedding = self.embedding_model.encode(text_to_embed).tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding for record '{record_id}': {e}", exc_info=True)
            return # Don't proceed without embedding

        # 4. Prepare Metadata
        metadata = self._prepare_chroma_metadata(airtable_fields)

        # 5. Upsert to ChromaDB (uses Airtable Record ID as the Chroma ID)
        try:
            self.chroma_collection.upsert(
                ids=[record_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[text_to_embed] # Store the text used for embedding as the document
            )
            logger.info(f"Successfully upserted record '{record_id}' into ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to upsert record '{record_id}' into ChromaDB: {e}", exc_info=True)
            # Re-raise or handle as needed

# --- Singleton or Dependency Injection ---
# Requires AirtableService instance
sync_service_instance = None
if get_airtable_service(): # Check if AirtableService initialized correctly
    try:
        sync_service_instance = SyncService(get_airtable_service())
    except RuntimeError as e:
        logger.critical(f"Failed to initialize SyncService: {e}")
        sync_service_instance = None
else:
     logger.critical("Cannot initialize SyncService because AirtableService failed to initialize.")


def get_sync_service() -> SyncService:
    """Dependency injector for the SyncService."""
    if sync_service_instance is None:
        raise HTTPException(
             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
             detail="Sync service is not available due to initialization errors."
         )
    return sync_service_instance
