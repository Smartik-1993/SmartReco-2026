import chromadb
from chromadb.config import Settings

# Persistent ChromaDB client stored locally in project root
chroma_client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(allow_reset=True)
)

# Get or create collection for product semantic search
product_collection = chroma_client.get_or_create_collection(
    name="products",
    metadata={"hnsw:space": "cosine"}
)

def get_product_collection():
    return product_collection