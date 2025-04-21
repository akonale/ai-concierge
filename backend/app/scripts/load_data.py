# backend/scripts/load_chroma.py

import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import uuid
import logging
import os

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
# Assumes your CSV is in backend/data/poc/experiences_simple.csv relative to this script's location
# Adjust the path if your structure or filename is different.
# Using the fields you provided: "Experience Name", "Description", "Duration", "Price", "Type", "URL", "Vendor"
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '..','..','..', 'data', 'poc', 'amsterdam_experiences_full.csv')
# Directory where ChromaDB will store its persistent data
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000
# Name for the ChromaDB collection
COLLECTION_NAME = "experiences"
# Pre-trained model for generating embeddings
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'  # A popular choice, downloads automatically


# --- Helper Functions ---

def get_embedding_model(model_name: str):
    """Loads or downloads the sentence transformer model."""
    try:
        logging.info(f"Loading sentence transformer model: {model_name}...")
        # You can specify cache_folder='./embedding_models' to control download location
        model = SentenceTransformer(model_name)
        logging.info("Sentence transformer model loaded successfully.")
        return model
    except Exception as e:
        logging.error(f"Error loading sentence transformer model: {e}", exc_info=True)
        raise


def initialize_chroma_client(host: str, port: int):
    """Initializes a persistent ChromaDB client."""
    try:
        logging.info(f"Initializing ChromaDB http client running on port {port}...")
        client = chromadb.HttpClient(host=host, port=port)
        logging.info("ChromaDB client initialized successfully.")
        return client
    except Exception as e:
        logging.error(f"Error initializing ChromaDB client: {e}", exc_info=True)
        raise


def load_data_from_csv(file_path: str) -> pd.DataFrame:
    """Loads data from the specified CSV file."""
    try:
        logging.info(f"Loading data from CSV: {file_path}")
        df = pd.read_csv(file_path)
        # Basic validation: Check if required columns exist
        required_columns = ["Experience Name", "Description"]  # Minimum needed for embedding
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV file must contain at least columns: {required_columns}")
        # Fill NaN values in metadata columns with empty strings or appropriate defaults
        df.fillna({
            "Duration": "",
            "Price": "",
            "Type": "",
            "URL": "",
            "Vendor": ""
        }, inplace=True)
        logging.info(f"Successfully loaded {len(df)} records from CSV.")
        return df
    except FileNotFoundError:
        logging.error(f"CSV file not found at path: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}", exc_info=True)
        raise


def prepare_chroma_data(df: pd.DataFrame, model: SentenceTransformer):
    """Prepares data lists (ids, documents, metadata, embeddings) for ChromaDB."""
    ids = []
    documents = []
    metadatas = []
    embeddings = []

    logging.info("Preparing data and generating embeddings...")
    # Combine relevant text fields for embedding generation
    # Using Name and Description seems reasonable for semantic search
    texts_to_embed = (df["Experience Name"] + " - " + df["Description"]).tolist()

    # Generate embeddings in batches (SentenceTransformer handles this efficiently)
    generated_embeddings = model.encode(texts_to_embed, show_progress_bar=True)

    for index, row in df.iterrows():
        # Create a unique ID for each experience
        doc_id = f"exp_{uuid.uuid4()}"  # Or use a unique ID column if available in CSV
        ids.append(doc_id)

        # Document content (used for embedding)
        doc_content = f"{row['Experience Name']} - {row['Description']}"
        documents.append(doc_content)  # ChromaDB also stores the document text

        # Metadata: Store all other relevant fields
        # Ensure metadata values are ChromaDB compatible (str, int, float, bool)
        metadata = {
            "experience_name": str(row.get("Experience Name", "")),
            "description": str(row.get("Description", "")),
            "duration": str(row.get("Duration", "")),  # Store as string
            "price": str(row.get("Price", "")),  # Store as string, handle potential non-numeric values
            "type": str(row.get("Type", "")),
            "url": str(row.get("URL", "")),
            "vendor": str(row.get("Vendor", "")),
            # Add other relevant fields from your CSV if needed
        }
        metadatas.append(metadata)

        # Add the pre-generated embedding for this row
        embeddings.append(generated_embeddings[index].tolist())  # Convert numpy array to list

    logging.info(f"Prepared {len(ids)} items for ChromaDB.")
    return ids, documents, metadatas, embeddings


# --- Main Execution ---
if __name__ == "__main__":
    logging.info("--- Starting ChromaDB Data Loading Script ---")

    try:
        # 1. Load data from CSV
        dataframe = load_data_from_csv(CSV_FILE_PATH)

        # 2. Initialize Embedding Model
        embedding_model = get_embedding_model(EMBEDDING_MODEL_NAME)

        # 3. Initialize ChromaDB Client
        chroma_client = initialize_chroma_client(CHROMA_HOST, CHROMA_PORT)

        # 4. Get or Create ChromaDB Collection
        logging.info(f"Getting or creating ChromaDB collection: {COLLECTION_NAME}")
        # Note: If using a model other than default, specify embedding function metadata
        # For sentence-transformers, ChromaDB can often infer it, but explicitly:
        # from chromadb.utils import embedding_functions
        # sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
        # collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=sentence_transformer_ef)

        # Simpler approach if default embedding function mapping works:
        collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
        logging.info(f"Collection '{COLLECTION_NAME}' ready.")

        # 5. Prepare data for ChromaDB
        ids, documents, metadatas, embeddings = prepare_chroma_data(dataframe, embedding_model)

        # 6. Add data to ChromaDB collection
        # Adding in batches might be more efficient for very large datasets,
        # but ChromaDB's add handles lists directly.
        logging.info(f"Adding {len(ids)} items to the collection...")
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logging.info("Successfully added data to ChromaDB collection.")

        # Optional: Verify count
        count = collection.count()
        logging.info(f"Collection '{COLLECTION_NAME}' now contains {count} items.")

    except Exception as e:
        logging.error(f"An error occurred during the data loading process: {e}", exc_info=True)

    logging.info("--- ChromaDB Data Loading Script Finished ---")
