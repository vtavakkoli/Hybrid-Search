from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_collection
from .elastic_db import init_es_index
from .schemas import SearchRequest, ComparisonResponse, SingleResult, IngestResponse
from .services import process_and_ingest_files, search_qdrant, search_elastic

app = FastAPI(title="Hybrid Search Comparison")

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
    return {"status": "ok"}

@app.post("/ingest", response_model=IngestResponse)
async def ingest(files: List[UploadFile] = File(...)):
    count, t_q, t_e = process_and_ingest_files(files)
    return IngestResponse(
        message="Done", chunks=count, qdrant_time_ms=t_q, elastic_time_ms=t_e
    )

@app.post("/search", response_model=ComparisonResponse)
async def search(request: SearchRequest):
    q_res, q_time = search_qdrant(request.query, request.limit)
    e_res, e_time = search_elastic(request.query, request.limit)

    q_mapped = [SingleResult(score=p.score, text=p.payload.get("text",""), source=p.payload.get("source","")) for p in q_res]
    e_mapped = [SingleResult(score=h["score"], text=h["text"], source=h["source"]) for h in e_res]

    return ComparisonResponse(
        qdrant_time_ms=q_time, elastic_time_ms=e_time,
        qdrant_results=q_mapped, elastic_results=e_mapped
    )
