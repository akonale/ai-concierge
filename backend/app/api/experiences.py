# backend/app/api/experiences.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from pydantic import BaseModel
# Import the response model and the mapping utility
from ..models.models import ExperienceCardData
from ..utils.mapping import map_airtable_to_card_data
# Import the Airtable service and its dependency getter
from ..services.airtable_service import AirtableService, get_airtable_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an API router for experience-related endpoints
router = APIRouter()

# Define a response model for the list of default experiences
class DefaultExperiencesResponse(BaseModel):
    default_experiences: List[ExperienceCardData]


@router.get(
    "/default",
    response_model=DefaultExperiencesResponse, # Use the new response model
    summary="Get Default/Featured Experiences",
    description="Retrieves a list of default or featured experiences to display on initial page load.",
    tags=["Experiences"] # Tag for grouping in API docs
)
async def get_default_experiences(
    airtable_service: AirtableService = Depends(get_airtable_service) # Inject Airtable service
):
    """
    Fetches default experiences (e.g., marked as 'Featured' in Airtable).
    """
    logger.info("Request received for default experiences.")
    default_experiences_data = []
    try:
        # Define the filter to get featured items (adjust field name and value as needed)
        # Assumes a checkbox field named "Featured" which is TRUE() when checked
        filter_formula = "{Featured}=TRUE()" # Example filter
        # Fetch records marked as featured from Airtable
        # Modify get_all_records if it doesn't return IDs along with fields
        # Assuming get_all_records returns list of {'id': '...', 'fields': {...}}
        # For now, let's fetch all fields and assume ID is included somehow or fetch separately
        
        # Fetch all records matching the filter
        # Limit the number of results if desired using max_records parameter
        featured_records_fields = airtable_service.get_all_records(
            #filter_formula=filter_formula,
            max_records=3 # Optional: limit the number of defaults
        )

        if not featured_records_fields:
            logger.warning(f"No records found in Airtable matching filter: {filter_formula}")
            # Return empty list if none are featured
            return DefaultExperiencesResponse(default_experiences=[])

        # --- Need IDs associated with fields ---
        # This highlights the need for get_all_records to return IDs.
        # Workaround: Fetch IDs separately and then fetch records one-by-one (inefficient)
        # OR assume the structure includes ID. Let's proceed assuming ID is available.
        # If get_all_records only returns fields, this needs adjustment.

        logger.info(f"Found {len(featured_records_fields)} featured records in Airtable.")

        for i, record_fields in enumerate(featured_records_fields):
            record_fields['id'] = str(i + 1)
        
        # Map the Airtable data to the response model structure
        for record_fields in featured_records_fields:
             # --- ASSUMPTION: record_fields dictionary contains the 'id' key ---
             # If not, the mapping function needs the ID passed separately,
             # requiring a different fetch strategy (e.g., get IDs then get records by ID)
             if 'id' not in record_fields: # Add a check/warning
                 logger.warning(f"Airtable record missing 'id' key, cannot map: {record_fields.get('Experience Name', 'Unknown Name')}")
                 continue # Skip this record

             card_data = map_airtable_to_card_data(record_fields) # Pass the dict including 'id'
             if card_data:
                 default_experiences_data.append(card_data)

        logger.info(f"Successfully mapped {len(default_experiences_data)} records to card data.")
        return DefaultExperiencesResponse(default_experiences=default_experiences_data)

    except Exception as e:
        logger.error(f"Error fetching default experiences: {e}", exc_info=True)
        # Raise internal server error if fetching fails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve default experiences."
        )

