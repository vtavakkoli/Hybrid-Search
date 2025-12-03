import os
import shutil
import tempfile
import time
from fastapi import UploadFile
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import models

from .database import client as q_client
from .elastic_db import es_client
from .config import settings
from .ml_engine import ml_manager

def process_and_ingest_files(files: list[UploadFile]):
    total_chunks = 0
    qdrant_time = 0.0
    elastic_time = 0.0
    
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name

        try:
            # 1. Parsing
            loader = UnstructuredLoader(tmp_path)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = text_splitter.split_documents(docs)
            if not chunks: continue

            texts = [doc.page_content for doc in chunks]
            metadatas = [{"source": file.filename, "text": doc.page_content} for doc in chunks]

            # 2. Embedding
            dense_vecs = ml_manager.embed_dense(texts)
            sparse_vecs = ml_manager.embed_sparse(texts)

            # --- QDRANT BENCHMARK ---
            start_q = time.perf_counter()
            points = []
            base_id = q_client.count(settings.COLLECTION_NAME).count
            for i in range(len(texts)):
                q_sparse = models.SparseVector(
                    indices=sparse_vecs[i].indices.tolist(),
                    values=sparse_vecs[i].values.tolist()
                )
                points.append(models.PointStruct(
                    id=base_id + i,
                    vector={"dense-vector": dense_vecs[i].tolist(), "sparse-vector": q_sparse},
                    payload=metadatas[i]
                ))
            q_client.upsert(collection_name=settings.COLLECTION_NAME, points=points)
            qdrant_time += (time.perf_counter() - start_q) * 1000

            # --- ELASTIC BENCHMARK ---
            start_e = time.perf_counter()
            for i in range(len(texts)):
                doc = {
                    "text": texts[i],
                    "source": file.filename,
                    "vector": dense_vecs[i].tolist()
                }
                es_client.index(index=settings.ES_INDEX_NAME, document=doc)
            es_client.indices.refresh(index=settings.ES_INDEX_NAME)
            elastic_time += (time.perf_counter() - start_e) * 1000

            total_chunks += len(points)
        except Exception as e:
            print(f"Error: {e}")
            continue
        finally:
            if os.path.exists(tmp_path): os.remove(tmp_path)
                
    return total_chunks, qdrant_time, elastic_time

def search_qdrant(query: str, limit: int):
    q_dense = ml_manager.embed_dense([query])[0]
    q_sparse = ml_manager.embed_sparse([query])[0]
    q_sparse_fmt = models.SparseVector(indices=q_sparse.indices.tolist(), values=q_sparse.values.tolist())

    start = time.perf_counter()
    results = q_client.query_points(
        collection_name=settings.COLLECTION_NAME,
        prefetch=[
            models.Prefetch(query=q_dense.tolist(), using="dense-vector", limit=limit),
            models.Prefetch(query=q_sparse_fmt, using="sparse-vector", limit=limit),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=limit,
    )
    return results.points, (time.perf_counter() - start) * 1000

def search_elastic(query: str, limit: int):
    q_dense = ml_manager.embed_dense([query])[0]
    start = time.perf_counter()
    resp = es_client.search(
        index=settings.ES_INDEX_NAME,
        size=limit,
        knn={
            "field": "vector",
            "query_vector": q_dense.tolist(),
            "k": limit,
            "num_candidates": 100
        },
        query={"match": {"text": query}}
    )
    
    hits = []
    for hit in resp['hits']['hits']:
        hits.append({
            "score": hit['_score'] if hit['_score'] else 0.0,
            "text": hit['_source']['text'],
            "source": hit['_source']['source']
        })
    return hits, (time.perf_counter() - start) * 1000
