from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_collection
from .elastic_db import init_es_index
from .queryweave_client import queryweave_client
from .schemas import ComparisonResponse, IngestResponse, SearchRequest, SingleResult
from .services import process_and_ingest_files, search_all

app = FastAPI(
    title="Hybrid Search Lab",
    description="Fair comparison of Qdrant, Elasticsearch and QueryWeave using identical vectors.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_collection()
    init_es_index()


@app.get("/health")
def health():
    engines = {"qdrant": "ok", "elasticsearch": "ok", "queryweave": "unknown"}
    try:
        queryweave_client.health()
        engines["queryweave"] = "ok"
    except Exception as exc:
        engines["queryweave"] = f"unavailable: {exc}"
    return {"status": "ok", "engines": engines}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(files: List[UploadFile] = File(...)):
    count, t_embed, t_q, t_e, t_w = process_and_ingest_files(files)
    return IngestResponse(
        message="Done",
        chunks=count,
        embedding_time_ms=t_embed,
        qdrant_time_ms=t_q,
        elastic_time_ms=t_e,
        queryweave_time_ms=t_w,
    )


@app.post("/search", response_model=ComparisonResponse)
async def search(request: SearchRequest):
    result = search_all(request.query, request.limit, request.queryweave_mode)
    q_res, q_time = result["qdrant"]
    e_res, e_time = result["elastic"]
    w_res, w_time, w_meta = result["queryweave"]

    q_mapped = [
        SingleResult(
            score=p.score,
            text=p.payload.get("text", ""),
            source=p.payload.get("source", ""),
        )
        for p in q_res
    ]
    e_mapped = [SingleResult(**hit) for hit in e_res]
    w_mapped = [
        SingleResult(
            score=hit["score"],
            text=hit["text"],
            source=hit.get("source", ""),
            details={
                "components": hit.get("components", {}),
                "explanation": hit.get("explanation"),
            },
        )
        for hit in w_res
    ]

    return ComparisonResponse(
        embedding_time_ms=result["embedding_time_ms"],
        qdrant_time_ms=q_time,
        elastic_time_ms=e_time,
        queryweave_time_ms=w_time,
        qdrant_results=q_mapped,
        elastic_results=e_mapped,
        queryweave_results=w_mapped,
        queryweave_meta=w_meta,
    )
