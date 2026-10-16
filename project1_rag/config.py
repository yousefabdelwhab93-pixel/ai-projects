
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load environment variables from the root .env
load_dotenv(find_dotenv())

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chroma_db"

# Chroma settings
COLLECTION_NAME = "course_documents"

# Chunking settings
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Retrieval settings
TOP_K = 4

# Model settings
CHAT_MODEL = "mercury-2.5"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
