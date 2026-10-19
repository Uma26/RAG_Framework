# RAG Framework - Complete Directory Structure

## Project Layout

```
rag_framework/
│
├── src/
│   ├── __init__.py
│   │   └── Package initialization with framework overview
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   │   └── Re-export settings singleton
│   │   └── settings.py
│   │       └── RAGSettings class (Pydantic-based configuration)
│   │           - Loading from env vars → .env → defaults
│   │           - Settings for embedding, vector store, RAG features
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   │   └── Re-export models and exceptions
│   │   ├── models.py
│   │   │   └── Core data structures (Pydantic models)
│   │   │       - QueryType enum (GENERAL, HOW_TO, TROUBLESHOOTING, SEARCH)
│   │   │       - FAQ model (question, answer, category, keywords, entities)
│   │   │       - Document model (chunked FAQ with embedding)
│   │   │       - SearchResult model (ranked result with scores)
│   │   │       - SearchQuery model (processed user query)
│   │   │       - RetrievalResult model (final output)
│   │   └── exceptions.py
│   │       └── Custom exception hierarchy
│   │           - RAGException (base)
│   │           - EmbeddingError, VectorStoreError, QueryProcessingError, etc.
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   │   └── Re-export all service singletons
│   │   ├── embedding_service.py
│   │   │   └── EmbeddingService class
│   │   │       - Load sentence-transformers model
│   │   │       - embed_text() - single text to vector
│   │   │       - embed_texts() - batch embedding (efficient)
│   │   │       - get_dimension() - return 384 dims
│   │   │       - health_check() - verify model working
│   │   │
│   │   ├── chroma_vector_store.py
│   │   │   └── ChromaDBVectorStore class
│   │   │       - Team-scoped collections for isolation
│   │   │       - add_documents() - store documents with embeddings
│   │   │       - search() - vector similarity search
│   │   │       - delete_document() - GDPR compliance
│   │   │       - get_stats() - team statistics
│   │   │       - health_check() - ChromaDB health
│   │   │
│   │   ├── ingestion_service.py
│   │   │   └── DocumentIngestionService class
│   │   │       - Load FAQs from JSON/file
│   │   │       - Chunk long documents (>500 chars)
│   │   │       - Extract keywords and entities
│   │   │       - Embed documents
│   │   │       - Store in team's ChromaDB collection
│   │   │
│   │   ├── query_processor.py
│   │   │   └── QueryProcessor class
│   │   │       - Normalize queries (lowercase, remove punctuation)
│   │   │       - Classify query type (adaptive routing)
│   │   │       - Expand queries with synonyms (multi-pass retrieval)
│   │   │       - Extract key terms
│   │   │       - Validate queries (security + sanity checks)
│   │   │
│   │   └── rag_orchestrator.py
│   │       └── RAGOrchestrator class
│   │           - Main retrieval pipeline
│   │           - Orchestrates all services
│   │           - Score and rank results
│   │           - retrieve() - basic retrieval
│   │           - retrieve_with_expansion() - multi-pass retrieval
│   │           - health_check() - overall system health
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   │   └── Re-export router
│   │   ├── routes.py
│   │   │   └── FastAPI endpoints
│   │   │       - POST /api/v1/retrieve - main retrieval
│   │   │       - POST /api/v1/retrieve-expanded - multi-pass
│   │   │       - POST /api/v1/ingest - ingest FAQs
│   │   │       - GET /api/v1/health - health check
│   │   │       - GET /api/v1/stats/{team_id} - team stats
│   │   │       - Request/Response models with validation
│   │   │
│   │   └── app.py
│   │       └── FastAPI application setup
│   │           - Lifespan events (startup/shutdown)
│   │           - CORS middleware
│   │           - Root endpoint
│   │           - Kubernetes probes (readiness, liveness)
│   │
│   └── sdk/
│       ├── __init__.py
│       │   └── Re-export RAGClient
│       └── client.py
│           └── RAGClient class (Python SDK)
│               - ingest_faqs() - load FAQs
│               - ingest_faqs_from_file() - from JSON file
│               - retrieve() - basic retrieval
│               - retrieve_expanded() - multi-pass retrieval
│               - get_stats() - team statistics
│               - health_check() - system health
│               - delete_faq() - delete FAQ
│
├── requirements.txt
│   └── All Python dependencies
│       - chromadb, sentence-transformers, fastapi, uvicorn
│       - pydantic, numpy, pandas, networkx
│       - pytest for testing
│       - Optional: openai (commented out)
│
├── .env.example
│   └── Configuration template
│       - EMBEDDING_MODEL, VECTOR_DIMENSION
│       - CHROMA_PERSIST_DIR
│       - RAG feature flags
│       - Logging level
│
├── run_api.py
│   └── Start REST API server
│       - python run_api.py
│       - Starts uvicorn on localhost:8000
│       - Shows API endpoints
│
├── example_usage.py
│   └── Step 2 example (vector store usage)
│       - Demonstrates embedding documents
│       - Storing in ChromaDB (team-scoped)
│       - Searching by vector similarity
│
├── example_sdk_usage.py
│   └── Complete SDK usage example
│       - Creating client
│       - Ingesting FAQs for multiple teams
│       - Retrieving documents
│       - Getting statistics
│       - Health checks
│       - Team isolation demo
│
├── README.md
│   └── Quick start guide
│       - Features overview
│       - Installation
│       - Usage examples (Python SDK + REST API)
│       - Architecture diagram
│       - Multi-tenancy model
│       - Performance benchmarks
│       - API endpoints reference
│
├── PROJECT_DOCUMENTATION.md
│   └── Complete technical documentation
│       - Architecture overview (high-level + layered)
│       - File-by-file documentation (every class, method, constant)
│       - Data flow examples (ingestion, retrieval)
│       - Multi-tenancy model details
│       - Performance characteristics
│       - Security model
│       - Testing strategy
│       - Configuration reference
│       - Deployment guide
│       - Troubleshooting guide
│       - Code examples
│       - Future roadmap
│
└── FRAMEWORK_STRUCTURE.md  (this file)
    └── Directory structure and file descriptions
```

## File Descriptions

### Core Framework Files

#### Configuration (`src/config/`)

| File | Purpose | Key Content |
|------|---------|-------------|
| `settings.py` | Configuration management | RAGSettings class, environment loading |
| `__init__.py` | Module export | Settings singleton |

#### Domain Models (`src/domain/`)

| File | Purpose | Key Content |
|------|---------|-------------|
| `models.py` | Data structures | 6 Pydantic models (FAQ, Document, SearchResult, etc.) |
| `exceptions.py` | Exception hierarchy | 8 custom exception classes |
| `__init__.py` | Module export | Re-exports models and exceptions |

#### Services (`src/services/`)

| File | Purpose | Lines | Key Methods |
|------|---------|-------|------------|
| `embedding_service.py` | Text → Vector conversion | ~188 | `embed_text()`, `embed_texts()`, `health_check()` |
| `chroma_vector_store.py` | Vector storage & search | ~370 | `add_documents()`, `search()`, `delete_document()`, `get_stats()` |
| `ingestion_service.py` | FAQ loading & processing | ~330 | `ingest_faqs_from_json()`, `ingest_faqs_from_file()`, `_chunk_text()` |
| `query_processor.py` | Query preprocessing | ~300 | `process_query()`, `_classify_query_type()`, `_expand_query()` |
| `rag_orchestrator.py` | Main retrieval pipeline | ~330 | `retrieve()`, `retrieve_with_expansion()`, `_score_document()` |
| `__init__.py` | Module export | ~10 | Re-exports all service singletons |

#### API (`src/api/`)

| File | Purpose | Lines | Key Methods |
|------|---------|-------|------------|
| `routes.py` | REST endpoints | ~300 | 5 endpoints + request/response models |
| `app.py` | FastAPI setup | ~100 | `create_app()`, lifespan, middleware |
| `__init__.py` | Module export | ~5 | Re-exports router |

#### SDK (`src/sdk/`)

| File | Purpose | Lines | Key Methods |
|------|---------|-------|------------|
| `client.py` | Python SDK | ~250 | 8 public methods for ingestion & retrieval |
| `__init__.py` | Module export | ~5 | Re-exports RAGClient |

### Entry Points

| File | Purpose | Usage |
|------|---------|-------|
| `run_api.py` | Start REST API | `python run_api.py` |
| `example_usage.py` | Example: Vector store | `python example_usage.py` |
| `example_sdk_usage.py` | Example: SDK usage | `python example_sdk_usage.py` |

### Configuration & Documentation

| File | Purpose | Contents |
|------|---------|----------|
| `requirements.txt` | Dependencies | 15+ packages with versions |
| `.env.example` | Config template | 10+ settings |
| `README.md` | Quick start | 400+ lines, getting started guide |
| `PROJECT_DOCUMENTATION.md` | Complete docs | 1000+ lines, technical deep-dive |
| `FRAMEWORK_STRUCTURE.md` | This file | Directory overview |

## Statistics

### Code Organization
- **Total Python files:** 18
- **Total lines of code:** ~2,500 (excluding examples & docs)
- **Main services:** 5
- **REST endpoints:** 5
- **SDK methods:** 8

### Dependencies
- **Total packages:** 15+
- **Core packages:** chromadb, sentence-transformers, fastapi
- **Data validation:** pydantic, pydantic-settings
- **Testing:** pytest, pytest-asyncio

### Documentation
- **README.md:** 450+ lines
- **PROJECT_DOCUMENTATION.md:** 1200+ lines
- **Inline code comments:** Comprehensive (WHY-focused)

## Data Flow Architecture

```
User Application
        ↓
    ┌───┴────┐
    │         │
REST API    Python SDK
    │         │
    └────┬────┘
         │
  RAG Orchestrator
  (Main pipeline)
         │
    ┌────┼────┬────────┐
    │    │    │        │
Query  Embed Vector  Document
Process Service Store Ingestion
    │    │    │        │
    └────┴────┼────────┘
             │
         ChromaDB
        (Persistent)
             │
      ┌──────┴──────┐
      │             │
   team_1_     team_2_
  documents   documents
      │             │
   [docs]       [docs]
```

## Deployment Architecture

```
┌─────────────────────────────────────┐
│   Production Environment             │
├─────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────┐   │
│  │  FastAPI Application         │   │
│  │  (uvicorn, multiple workers) │   │
│  └──────────────┬───────────────┘   │
│                 │                    │
│  ┌──────────────▼───────────────┐   │
│  │  ChromaDB (Persistent)       │   │
│  │  /chroma_data directory      │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  sentence-transformers Model │   │
│  │  (cached, ~500MB)            │   │
│  └──────────────────────────────┘   │
│                                      │
└─────────────────────────────────────┘
```

## Getting Started Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy env file: `cp .env.example .env`
- [ ] Try example: `python example_usage.py`
- [ ] Try SDK: `python example_sdk_usage.py`
- [ ] Start API: `python run_api.py`
- [ ] Visit docs: http://localhost:8000/docs
- [ ] Read README.md for quick start
- [ ] Read PROJECT_DOCUMENTATION.md for deep-dive

## Next Steps (Roadmap)

### Phase 1 (Current)
- ✅ Core retrieval pipeline
- ✅ Multi-tenant isolation
- ✅ REST API
- ✅ Python SDK
- ✅ Documentation

### Phase 2
- [ ] Graph-based entity relationships
- [ ] Hybrid search (vector + keyword)
- [ ] Advanced reranking
- [ ] Query caching

### Phase 3
- [ ] Analytics dashboard
- [ ] Distributed deployment
- [ ] Multiple embedding models
- [ ] PostgreSQL backend

### Phase 4
- [ ] LLM integration (optional)
- [ ] Real-time indexing
- [ ] Multi-language support
- [ ] Enterprise authentication

## Support

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Code Examples:** `example_usage.py`, `example_sdk_usage.py`
- **Full Documentation:** Read `PROJECT_DOCUMENTATION.md`
- **Quick Start:** Read `README.md`

---

**Framework built with ❤️ for enterprise-grade RAG applications**
