# ⚔️ Hybrid Search Benchmark: Qdrant vs Elasticsearch

A fully containerized, on-premise solution to perform **Hybrid Search** (Semantic + Keyword) on your local documents. This project allows you to ingest files and compare the search relevance and performance latency between **Qdrant** (using SPLADE) and **Elasticsearch** (using BM25).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue)
![Python](https://img.shields.io/badge/Python-3.12-yellow)
![React](https://img.shields.io/badge/React-18-cyan)

## 🚀 Features

*   **100% Local & On-Premise:** No Cloud APIs or API keys required. Models run locally on your CPU.
*   **Dual Vector Stores:**
    *   **Qdrant:** Uses Dense Vectors (`bge-small`) + Sparse Vectors (`SPLADE`) with Reciprocal Rank Fusion (RRF).
    *   **Elasticsearch:** Uses Dense Vectors (`bge-small`) + Keyword Search (`BM25`) with Linear Combination.
*   **File Ingestion:** Supports **PDF**, **TXT**, and **CSV** via Unstructured and LangChain.
*   **Performance Benchmarking:** Real-time measurement of ingestion speed and search latency in milliseconds.
*   **Modern UI:** React-based split-screen comparison to visually validate search results.

---

## 🏗️ Architecture

The solution uses a Microservices architecture orchestrated via Docker Compose.

| Service | Technology | Internal Port | **External Port** | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | React + Vite (Node 22) | 3000 | **4300** | The Web User Interface |
| **Backend** | FastAPI (Python 3.12) | 8000 | **4800** | Logic, Embeddings, OCR |
| **Qdrant** | Qdrant Vector DB | 6333 | **4633** | Vector Store 1 |
| **Elastic** | Elasticsearch 9.2 | 9200 | **4920** | Vector Store 2 |

---

## 🛠️ Prerequisites

*   **Docker Desktop** (or Docker Engine + Compose plugin)
*   **4GB+ RAM** available (Elasticsearch and Embedding models require memory).

---

## 📦 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone Hybrid-Search
    cd Hybrid-Search
    ```

2.  **Build and Run**
    ```bash
    docker-compose up --build
    ```
    *First run will take a few minutes to download the base images and the Embedding models.*

3.  **Access the Application**
    Open your browser to: **[http://localhost:4300](http://localhost:4300)**

---

## 📖 Usage Guide

### 1. Ingestion Tab
1.  Click **"Data Ingestion"**.
2.  Drag and drop or select **PDFs** or **Text files**.
3.  Click **"Start Ingestion Benchmark"**.
4.  The system will:
    *   OCR/Parse the files.
    *   Split text into chunks.
    *   Generate Dense Vectors (Semantics).
    *   Generate Sparse Vectors (Keywords).
    *   Write to both Qdrant and Elasticsearch.
5.  View the write latency comparison.

### 2. Hybrid Search Tab
1.  Click **"Hybrid Search"**.
2.  Type a query (e.g., *"What are the termination conditions?"*).
3.  Click **"Compare Performance"**.
4.  View side-by-side results:
    *   **Qdrant (Pink):** Results sorted by RRF fusion of Semantic + SPLADE scores.
    *   **Elasticsearch (Teal):** Results sorted by Linear Combination of Semantic + BM25 scores.

---

## 🧠 Technical Details

### Embedding Models
*   **Dense:** `BAAI/bge-small-en-v1.5` (384 dimensions).
*   **Sparse:** `prithivida/Splade_PP_en_v1` (Learned Sparse Representations).
*   *Models are cached locally in the `./models_cache` folder to prevent re-downloading.*

### Search Logic
*   **Qdrant:**
    ```python
    models.FusionQuery(fusion=models.Fusion.RRF)
    ```
    Combines dense and sparse vector results using Reciprocal Rank Fusion.

*   **Elasticsearch:**
    Uses a standard Hybrid approach compatible with the Basic License:
    ```json
    {
      "knn": { ...vector_search... },
      "query": { "match": { "text": ...keyword_search... } }
    }
    ```

---

## 🔧 Troubleshooting

**1. `libGL.so.1: cannot open shared object file`**
*   This indicates the Backend Docker container wasn't built correctly.
*   **Fix:** Run `docker-compose up --build` to ensure `libgl1` is installed via `apt-get`.

**2. Frontend connection error / Network Warning**
*   If you see "Network request failed", ensure you are accessing `http://localhost:4300`.
*   Chrome may warn about "Private Network Access". This is normal for local development tools accessing local APIs.

**3. Elasticsearch exits with code 137**
*   This means OOM (Out of Memory).
*   **Fix:** Increase Docker Desktop memory limit to at least 4GB.

---

## 📂 Project Structure

```text
hybrid_search/
├── docker-compose.yml       # Orchestration & Port Config
├── models_cache/            # Local storage for AI models
├── backend/
│   ├── Dockerfile           # Python env with OCR libs
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # API Routes
│       ├── services.py      # Business Logic (Ingest/Search)
│       ├── ml_engine.py     # Model Loader
│       ├── database.py      # Qdrant Setup
│       ├── elastic_db.py    # Elastic Setup
│       └── config.py        # Settings
└── frontend/
    ├── Dockerfile           # Node Alpine with Cert fix
    └── src/
        └── App.jsx          # React UI Components






