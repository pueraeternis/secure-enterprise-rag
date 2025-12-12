# ADR 001: Technology Stack Selection for Secure Enterprise RAG

## Status
Accepted

## Context
We need to build a secure, self-hosted Retrieval-Augmented Generation (RAG) system for an enterprise environment.
**Constraints:**
1.  **Data Privacy:** No external APIs (OpenAI, Anthropic) allowed. Data must not leave the perimeter.
2.  **Scalability:** The system must handle thousands of documents.
3.  **Accuracy:** Requires hybrid search (Semantic + Keyword) to support specific domain terminology.

## Decision

### 1. LLM Engine: vLLM
We selected **vLLM** over Ollama or HuggingFace TGI.
*   **Pros:** State-of-the-art throughput (PagedAttention), OpenAI-compatible API, supports distributed inference (tensor parallel).
*   **Cons:** Higher VRAM requirement than llama.cpp.
*   **Verdict:** Critical for production-grade latency.

### 2. Vector Database: Milvus (Standalone)
We selected **Milvus** over Qdrant or pgvector.
*   **Pros:** Native support for Hybrid Search (Dense + Sparse BM25), separate scaling of storage/compute nodes (in cluster mode), proven widely in enterprise.
*   **Cons:** Complex infrastructure (requires etcd, MinIO).
*   **Verdict:** Chosen for robustness and advanced indexing capabilities.

### 3. Backend Framework: FastAPI
*   **Pros:** Native Async I/O (critical for handling concurrent LLM streams), Pydantic validation, auto-generated Swagger UI.

### 4. RAG Framework: Custom implementation (LlamaIndex as a library)
We use **LlamaIndex** core components but wrap them in a custom Service Layer.
*   **Reason:** Gives full control over the ingestion pipeline and prompt construction while leveraging LlamaIndex's SOTA retrievers.

## Consequences
*   **Infrastructure Complexity:** Deploying Milvus and vLLM requires Docker Compose and NVIDIA Container Toolkit.
*   **Hardware Requirements:** Requires at least one NVIDIA GPU (24GB+ recommended) for the LLM.