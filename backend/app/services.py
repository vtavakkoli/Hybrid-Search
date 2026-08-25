from __future__ import annotations

import os
import shutil
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_unstructured import UnstructuredLoader
from qdrant_client import models

from .config import settings
from .database import client as q_client
from .elastic_db import es_client
from .ml_engine import ml_manager
from .queryweave_client import queryweave_client


def _sparse_payload(vector) -> dict[str, list]:
    return {"indices": vector.indices.tolist(), "values": vector.values.tolist()}


def process_and_ingest_files(files: list[UploadFile]):
    total_chunks = 0
    embedding_time = 0.0
    qdrant_time = 0.0
    elastic_time = 0.0
    queryweave_time = 0.0

    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name

        try:
            docs = UnstructuredLoader(tmp_path).load()
            chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
            if not chunks:
                continue

            texts = [doc.page_content for doc in chunks]
            metadatas = [{"source": file.filename, "text": doc.page_content} for doc in chunks]

            embed_start = time.perf_counter()
            dense_vecs = ml_manager.embed_dense(texts)
            sparse_vecs = ml_manager.embed_sparse(texts)
            embedding_time += (time.perf_counter() - embed_start) * 1000

            base_id = q_client.count(settings.COLLECTION_NAME).count

            start_q = time.perf_counter()
            points = []
            for i, text in enumerate(texts):
                points.append(
                    models.PointStruct(
                        id=base_id + i,
                        vector={
                            "dense-vector": dense_vecs[i].tolist(),
                            "sparse-vector": models.SparseVector(**_sparse_payload(sparse_vecs[i])),
                        },
                        payload=metadatas[i],
                    )
                )
            q_client.upsert(collection_name=settings.COLLECTION_NAME, points=points)
            qdrant_time += (time.perf_counter() - start_q) * 1000

            start_e = time.perf_counter()
            for i, text in enumerate(texts):
                es_client.index(
                    index=settings.ES_INDEX_NAME,
                    document={"text": text, "source": file.filename, "vector": dense_vecs[i].tolist()},
                )
            es_client.indices.refresh(index=settings.ES_INDEX_NAME)
            elastic_time += (time.perf_counter() - start_e) * 1000

            queryweave_docs = [
                {
                    "id": f"{file.filename}:{base_id + i}",
                    "text": text,
                    "source": file.filename,
                    "metadata": {"source": file.filename, "chunk": str(base_id + i)},
                    "dense": dense_vecs[i].tolist(),
                    "sparse": _sparse_payload(sparse_vecs[i]),
                }
                for i, text in enumerate(texts)
            ]
            queryweave_time += queryweave_client.upsert(queryweave_docs)
            total_chunks += len(texts)
        except Exception as exc:
            print(f"Ingestion error for {file.filename}: {exc}")
            raise
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return total_chunks, embedding_time, qdrant_time, elastic_time, queryweave_time


def _search_qdrant(query_dense, query_sparse, limit: int):
    start = time.perf_counter()
    results = q_client.query_points(
        collection_name=settings.COLLECTION_NAME,
        prefetch=[
            models.Prefetch(query=query_dense, using="dense-vector", limit=max(limit * 4, limit)),
            models.Prefetch(
                query=models.SparseVector(**query_sparse),
                using="sparse-vector",
                limit=max(limit * 4, limit),
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=limit,
    )
    return results.points, (time.perf_counter() - start) * 1000


def _search_elastic(query: str, query_dense, limit: int):
    start = time.perf_counter()
    resp = es_client.search(
        index=settings.ES_INDEX_NAME,
        size=limit,
        knn={
            "field": "vector",
            "query_vector": query_dense,
            "k": limit,
            "num_candidates": max(100, limit * 10),
        },
        query={"match": {"text": query}},
    )
    hits = [
        {
            "score": hit.get("_score") or 0.0,
            "text": hit["_source"]["text"],
            "source": hit["_source"]["source"],
        }
        for hit in resp["hits"]["hits"]
    ]
    return hits, (time.perf_counter() - start) * 1000


def _search_queryweave(query: str, query_dense, query_sparse, limit: int, mode: str):
    return queryweave_client.search(query, query_dense, query_sparse, limit, mode=mode)


def search_all(query: str, limit: int, queryweave_mode: str = "auto"):
    embed_start = time.perf_counter()
    q_dense = ml_manager.embed_dense([query])[0].tolist()
    q_sparse = _sparse_payload(ml_manager.embed_sparse([query])[0])
    embedding_time = (time.perf_counter() - embed_start) * 1000

    with ThreadPoolExecutor(max_workers=3) as executor:
        q_future = executor.submit(_search_qdrant, q_dense, q_sparse, limit)
        e_future = executor.submit(_search_elastic, query, q_dense, limit)
        w_future = executor.submit(_search_queryweave, query, q_dense, q_sparse, limit, queryweave_mode)
        q_result, q_time = q_future.result()
        e_result, e_time = e_future.result()
        w_result, w_time, w_meta = w_future.result()

    return {
        "embedding_time_ms": embedding_time,
        "qdrant": (q_result, q_time),
        "elastic": (e_result, e_time),
        "queryweave": (w_result, w_time, w_meta),
    }
