from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SingleResult(BaseModel):
    score: float
    text: str
    source: str

class ComparisonResponse(BaseModel):
    qdrant_time_ms: float
    elastic_time_ms: float
    qdrant_results: List[SingleResult]
    elastic_results: List[SingleResult]

class IngestResponse(BaseModel):
    message: str
    chunks: int
    qdrant_time_ms: float
    elastic_time_ms: float
