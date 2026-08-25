import os


class Config:
    MODEL_CACHE_DIR = "/app/models_cache"

    COLLECTION_NAME = "hybrid_docs"
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

    ES_INDEX_NAME = "hybrid_docs_es"
    ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
    ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

    QUERYWEAVE_URL = os.getenv("QUERYWEAVE_URL", "http://localhost:7777")

    CORS_ORIGINS = [
        "http://localhost:4300",
        "http://127.0.0.1:4300",
        "*",
    ]


settings = Config()
