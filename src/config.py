"""
Configuration and environment setup for Starbucks Recommendation System
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# OpenAI Configuration
OPENAI_MODEL = "gpt-4o-mini"  # For constraint extraction
EMBEDDING_MODEL = "text-embedding-3-small"  # For product embeddings
EMBEDDING_DIMENSIONS = 1536  # Dimensions for text-embedding-3-small

# Pinecone Configuration
PINECONE_INDEX_NAME = "starbucks-products"
PINECONE_METRIC = "cosine"  # Similarity metric

# File Paths
import os

# Try to get project root intelligently
if __name__ == "__main__":
    # Running config.py directly
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
else:
    # Imported as module
    try:
        # Get parent directory (project root) from src directory
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        # Fallback if __file__ is not defined (e.g., interactive mode)
        PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), '..'))

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
TRAIN_QUERIES_FILE = os.path.join(DATA_DIR, "queries_train.csv")
TEST_QUERIES_FILE = os.path.join(DATA_DIR, "queries_test.csv")
SUBMISSION_FILE = os.path.join(PROJECT_ROOT, "submission.csv")

# Validation
def validate_config():
    """Validate that all required configuration is present"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY not found in environment variables")
    print("✓ Configuration validated successfully")

if __name__ == "__main__":
    validate_config()
    print(f"OpenAI Model: {OPENAI_MODEL}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Pinecone Index: {PINECONE_INDEX_NAME}")