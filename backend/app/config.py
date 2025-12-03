import os

class Config:
    # Storage Paths
    MODEL_CACHE_DIR = "/app/models_cache"
    
    # Qdrant Settings (Internal Docker DNS)
    COLLECTION_NAME = "hybrid_docs"
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

    # Elasticsearch Settings (Internal Docker DNS)
    ES_INDEX_NAME = "hybrid_docs_es"
    ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
    ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

    # CORS - Allow Frontend on Port 4300
    CORS_ORIGINS = [
        "http://localhost:4300",
        "http://127.0.0.1:4300",
        "*"
    ]

settings = Config()
