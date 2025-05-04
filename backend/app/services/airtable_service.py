# backend/app/services/airtable_service.py

import os
import logging
from dotenv import load_dotenv
from pyairtable import Api, Table
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AirtableService:
    """
    Service class to interact with the Airtable API.
    """
    def __init__(self):
        """
        Initializes the Airtable client using environment variables.
        """
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self.experiences_table_id = os.getenv("AIRTABLE_EXPERIENCES_TABLE_ID")
        if not all([self.api_key, self.base_id, self.experiences_table_id]):
            logger.error("Airtable environment variables not fully configured (API Key/PAT, Base ID, Table ID).")
            raise ValueError("Airtable configuration missing in environment variables.")

        try:
            self.experiences_table = Table(self.api_key, self.base_id, self.experiences_table_id)
            logger.info("Airtable client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Airtable client: {e}", exc_info=True)
            raise RuntimeError("Could not initialize Airtable client") from e

    def get_record(self, record_id: str) -> dict | None:
        """
        Fetches a single record from the Experiences table by its Airtable Record ID.
        """
        try:
            # logger.debug(f"Fetching record '{record_id}' from Airtable.") # Use debug level
            record = self.experiences_table.get(record_id)
            return record.get('fields') if record else None
        except Exception as e:
            logger.error(f"Error fetching record '{record_id}' from Airtable: {e}", exc_info=True)
            return None

    def get_all_records(self, fields: List[str] = None, filter_formula: str = None) -> List[dict]:
        """
        Fetches all records from the Experiences table, optionally filtering
        and selecting specific fields.

        Args:
            fields: A list of field names to retrieve. If None, retrieves all fields.
            filter_formula: An Airtable formula string to filter records (e.g., "{Status}='Active'").

        Returns:
            A list of dictionaries, where each dictionary represents the 'fields' of a record.
        """
        all_records_data = []
        try:
            logger.info(f"Fetching all records from Airtable table '{self.experiences_table_id}'...")
            # Use all() which handles pagination automatically
            all_records_raw = self.experiences_table.all(fields=fields, formula=filter_formula)
            # Extract just the 'fields' dictionary from each raw record
            all_records_data = [record.get('fields', {}) for record in all_records_raw]
            logger.info(f"Successfully fetched {len(all_records_data)} records.")
        except Exception as e:
            logger.error(f"Error fetching all records from Airtable: {e}", exc_info=True)
            # Depending on need, could return empty list or re-raise
        return all_records_data

    def get_all_record_ids(self, filter_formula: str = None) -> List[str]:
        """
        Fetches only the Record IDs for all records in the table, optionally filtering.
        More efficient than fetching all fields if only IDs are needed.

        Args:
            filter_formula: An Airtable formula string to filter records.

        Returns:
            A list of Airtable Record IDs.
        """
        all_ids = []
        try:
            logger.info(f"Fetching all record IDs from Airtable table '{self.experiences_table_id}'...")
            # Fetch only the 'id' field implicitly by specifying fields=[] (or check pyairtable docs)
            # Alternatively, fetch a minimal field known to exist to get IDs
            # Let's fetch the primary field name if known, or just rely on .all() returning IDs
            all_records_raw = self.experiences_table.all(formula=filter_formula, fields=[]) # fields=[] might not work as expected
            
            # Iterate and extract IDs - .all() returns full records even with fields=[] in some versions
            all_ids = [record['id'] for record in all_records_raw if 'id' in record]
            
            # Fallback if above doesn't work: Fetch a minimal field
            # if not all_ids:
            #    logger.warning("Fetching minimal field to get IDs as fields=[] didn't yield IDs directly.")
            #    # Replace 'Experience Name' with your actual primary field if different
            #    all_records_raw = self.experiences_table.all(formula=filter_formula, fields=['Experience Name']) 
            #    all_ids = [record['id'] for record in all_records_raw if 'id' in record]

            logger.info(f"Successfully fetched {len(all_ids)} record IDs.")
        except Exception as e:
            logger.error(f"Error fetching all record IDs from Airtable: {e}", exc_info=True)
        return all_ids


# --- Singleton or Dependency Injection ---
try:
    airtable_service_instance = AirtableService()
except (ValueError, RuntimeError) as e:
    logger.critical(f"Failed to initialize AirtableService: {e}")
    airtable_service_instance = None

def get_airtable_service() -> AirtableService:
    """Dependency injector for the AirtableService."""
    if airtable_service_instance is None:
        raise HTTPException(
             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
             detail="Airtable service is not available due to initialization errors."
         )
    return airtable_service_instance

# --- Add necessary imports ---
from fastapi import HTTPException
from starlette import status