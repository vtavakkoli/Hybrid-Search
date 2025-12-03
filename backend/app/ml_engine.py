from fastembed import TextEmbedding, SparseTextEmbedding
from .config import settings

class ModelManager:
    """Singleton to load models once and persist them."""
    def __init__(self):
        print(f"Loading Models from {settings.MODEL_CACHE_DIR}...")
        
        self.dense_model = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5", 
            cache_dir=settings.MODEL_CACHE_DIR
        )
        
        self.sparse_model = SparseTextEmbedding(
            model_name="prithivida/Splade_PP_en_v1", 
            cache_dir=settings.MODEL_CACHE_DIR
        )
        print("Models Loaded.")

    def embed_dense(self, texts: list[str]):
        return list(self.dense_model.embed(texts))

    def embed_sparse(self, texts: list[str]):
        return list(self.sparse_model.embed(texts))

ml_manager = ModelManager()
