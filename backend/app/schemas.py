from typing import Any, List

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=10, ge=1, le=100)
    queryweave_mode: str = "auto"


class SingleResult(BaseModel):
    score: float
    text: str
    source: str
    details: dict[str, Any] | None = None


class ComparisonResponse(BaseModel):
    embedding_time_ms: float
    qdrant_time_ms: float
    elastic_time_ms: float
    queryweave_time_ms: float
    qdrant_results: List[SingleResult]
    elastic_results: List[SingleResult]
    queryweave_results: List[SingleResult]
    queryweave_meta: dict[str, Any]


class IngestResponse(BaseModel):
    message: str
    chunks: int
    embedding_time_ms: float
    qdrant_time_ms: float
    elastic_time_ms: float
    queryweave_time_ms: float
