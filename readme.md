# Hybrid Search Lab — Qdrant vs Elasticsearch vs QueryWeave

A containerized retrieval laboratory that compares three engines using **the same parsed chunks and the same query/document embeddings**:

- **Qdrant** — dense + SPLADE sparse retrieval with RRF;
- **Elasticsearch** — BM25 + dense kNN hybrid retrieval;
- **QueryWeave** — Rust adaptive lexical+sparse+dense retrieval with AQF, early exit and confidence-triggered reranking.

## Why v2 is a fairer benchmark

The original implementation compared Qdrant and Elasticsearch, but each search function generated its own query embedding. v2 performs dense and sparse query encoding **once**, outside the engine timers, and then sends the same vectors to every backend.

```text
query
  │
  ├── BGE dense vector ─────────┐
  └── SPLADE sparse vector ─────┼─────────────────────────┐
                               │                         │
             ┌─────────────────┼───────────────┐         │
             ▼                 ▼               ▼         │
          Qdrant          Elasticsearch    QueryWeave     │
        dense+sparse       BM25+dense     BM25+sparse+dense
             │                 │               │
             └─────────────────┴───────────────┘
                      separately timed
```

Embedding time is reported separately.

## QueryWeave integration

The Compose stack builds QueryWeave from its implementation branch and exposes it internally at `http://queryweave:7777`. Hybrid-Search reuses the existing FastEmbed models:

- dense: `BAAI/bge-small-en-v1.5`;
- sparse: `prithivida/Splade_PP_en_v1`.

Documents are sent to QueryWeave with both vectors, so its adaptive fusion logic is benchmarked rather than its zero-model fallback encoders.

## Start

```bash
docker compose up --build
```

Open:

- UI: `http://localhost:4300`
- benchmark API: `http://localhost:4800`
- QueryWeave direct: `http://localhost:4777`
- Qdrant direct: `http://localhost:4633`
- Elasticsearch direct: `http://localhost:4920`

## Search modes

The UI can force QueryWeave ablations:

- `auto` — adaptive route selection;
- `lexical` — BM25-style only;
- `hybrid` — lexical+sparse+dense AQF;
- `deep` — AQF + reranking path.

This makes the app useful for both engine comparison and QueryWeave algorithm ablations.

## Timing contract

- parsing time: excluded from backend write comparison;
- document embedding time: reported separately;
- backend ingestion: timed independently;
- query embedding time: computed once and reported separately;
- engine retrieval: Qdrant, Elasticsearch and QueryWeave run concurrently and are individually timed.

For publication-grade experiments, run repeated queries, warm caches consistently, pin container versions, collect p50/p95/p99 and add relevance judgments (nDCG/MRR/Recall). QueryWeave's repository contains the broader BEIR/engine-comparison methodology.

## Architecture

```text
React benchmark dashboard :4300
              │
              ▼
FastAPI comparison backend :4800
      │          │          │
      ▼          ▼          ▼
  Qdrant      Elastic    QueryWeave
   :6333       :9200       :7777
```

## Research direction

The key comparison is not simply “which database is fastest?” It is whether QueryWeave can move the quality/cost Pareto frontier by avoiding expensive retrieval stages for easy queries while invoking deeper fusion/reranking only when retrievers disagree.
