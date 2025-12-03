from elasticsearch import Elasticsearch
from .config import settings

es_client = Elasticsearch(f"http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}")

def init_es_index():
    if not es_client.indices.exists(index=settings.ES_INDEX_NAME):
        print(f"Creating Elastic Index: {settings.ES_INDEX_NAME}")
        mapping = {
            "mappings": {
                "properties": {
                    "text": {"type": "text"}, 
                    "source": {"type": "keyword"},
                    "vector": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
        es_client.indices.create(index=settings.ES_INDEX_NAME, body=mapping)
