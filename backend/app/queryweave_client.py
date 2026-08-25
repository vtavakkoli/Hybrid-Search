from __future__ import annotations

import time
from typing import Any

import requests

from .config import settings


class QueryWeaveClient:
    """Small adapter around the QueryWeave HTTP API.

    Hybrid-Search supplies its existing BGE and SPLADE vectors so all engines are compared with
    identical representations rather than different model stacks.
    """

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.QUERYWEAVE_URL).rstrip("/")
        self.session = requests.Session()

    def health(self) -> dict[str, Any]:
        response = self.session.get(f"{self.base_url}/health", timeout=5)
        response.raise_for_status()
        return response.json()

    def reset(self) -> None:
        response = self.session.delete(f"{self.base_url}/v1/index", timeout=10)
        response.raise_for_status()

    def upsert(self, documents: list[dict[str, Any]]) -> float:
        start = time.perf_counter()
        response = self.session.post(
            f"{self.base_url}/v1/documents:upsert",
            json={"documents": documents},
            timeout=120,
        )
        response.raise_for_status()
        return (time.perf_counter() - start) * 1000

    def search(
        self,
        query: str,
        dense: list[float],
        sparse: dict[str, list],
        limit: int,
        *,
        mode: str = "auto",
    ) -> tuple[list[dict[str, Any]], float, dict[str, Any]]:
        start = time.perf_counter()
        response = self.session.post(
            f"{self.base_url}/v1/search",
            json={
                "query": query,
                "limit": limit,
                "mode": mode,
                "dense": dense,
                "sparse": sparse,
                "filter": {},
                "explain": True,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        elapsed_ms = (time.perf_counter() - start) * 1000
        return payload.get("hits", []), elapsed_ms, {
            "route": payload.get("route", "unknown"),
            "engine_elapsed_ms": payload.get("elapsed_ms"),
            "indexed_documents": payload.get("indexed_documents", 0),
        }


queryweave_client = QueryWeaveClient()
