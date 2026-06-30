from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import os

class VectorMemory:
    def __init__(self, host: str = "localhost", port: int = 6333):
        # Allow override from env variables, fallback to defaults
        self.host = os.environ.get("QDRANT_HOST", host)
        self.port = int(os.environ.get("QDRANT_PORT", port))
        
        try:
            self.client = QdrantClient(host=self.host, port=self.port)
        except Exception as e:
            print(f"Warning: Could not connect to Qdrant at {self.host}:{self.port}. Error: {e}")
            self.client = None

    def initialize_collection(self, collection_name: str, vector_size: int = 768):
        """Creates a collection if it doesn't exist."""
        if not self.client:
            return
            
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == collection_name for c in collections):
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                print(f"Collection {collection_name} created.")
        except Exception as e:
            print(f"Error initializing collection {collection_name}: {e}")

    def add_texts(self, collection_name: str, texts: list[str], vectors: list[list[float]], payloads: list[dict]):
        # Implementation for adding texts
        pass

    def search(self, collection_name: str, query_vector: list[float], limit: int = 5):
        # Implementation for vector search
        pass
