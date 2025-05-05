# backend/app/utils/mapping.py

import logging
from typing import Dict, Any, Optional
# Import the Pydantic model defining the card structure
from ..models.models import ExperienceCardData

# Configure logging
logger = logging.getLogger(__name__)

def map_airtable_to_card_data(airtable_record: Dict[str, Any]) -> Optional[ExperienceCardData]:
    """
    Maps fields from a retrieved Airtable record (including its ID)
    to the ExperienceCardData Pydantic model.
    Handles potential missing fields and type conversions.

    Args:
        airtable_record: A dictionary containing the 'id' (Airtable Record ID)
                         and the 'fields' dictionary fetched from Airtable.
                         Example: {'id': 'recXXX', 'Experience Name': 'Yoga', ...}

    Returns:
        An ExperienceCardData object if mapping is successful, otherwise None.
    """
    if not airtable_record or 'id' not in airtable_record:
        logger.warning("Attempted to map invalid airtable_record structure.")
        return None

    try:
        # Extract image URL (example assumes 'Attachments' field containing a list of objects)
        # Adjust 'Attachments' based on your actual Airtable field name for images

        # Create the card data object using field names from your Airtable base
        # Use .get() with defaults to handle potentially missing fields gracefully
        card_data = ExperienceCardData(
            id=airtable_record.get('id'), # Use the ID passed in the dictionary key
            name=airtable_record.get('Experience Name', 'N/A'), # Adjust field name as per your Airtable
            description=airtable_record.get('Description'), # Optional field
            image_url=airtable_record.get('Image URL'), # Use the extracted URL
            price=str(airtable_record.get('Price', '')), # Ensure string, adjust field name
            duration=str(airtable_record.get('Duration', '')), # Ensure string, adjust field name
            type=airtable_record.get('Type', [])[0], # Adjust field name
            url=airtable_record.get('URL') # Adjust field name for details/booking link
            # Map other fields from your ExperienceCardData model here
        )
        return card_data
    except Exception as e:
        # Log error if mapping fails for a specific record
        logger.error(f"Error mapping Airtable record {airtable_record.get('id')} to Card Data: {e}", exc_info=True)
        return None # Return None if mapping fails
