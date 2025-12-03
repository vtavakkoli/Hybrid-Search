from qdrant_client import QdrantClient, models
from .config import settings

client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)

def init_collection():
    if not client.collection_exists(settings.COLLECTION_NAME):
        print(f"Creating Qdrant Collection: {settings.COLLECTION_NAME}")
        client.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config={
                "dense-vector": models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse-vector": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            }
        )
