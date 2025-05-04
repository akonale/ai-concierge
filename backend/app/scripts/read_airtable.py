import sys
from dotenv import load_dotenv
import os

# Add project root to sys.path to allow absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)
load_dotenv()

# Now use absolute import from the project root
from backend.app.services.airtable_service import get_airtable_service

print(get_airtable_service().get_all_records())
