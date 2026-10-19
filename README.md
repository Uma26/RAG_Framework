# RAG Framework - Multi-Tenant Retrieval-Augmented Generation

An enterprise-grade, multi-tenant Retrieval-Augmented Generation (RAG) framework for Python. Perfect for teams that need to search and retrieve FAQ documents efficiently.

## Features

✅ **Retrieval Only** - No LLM integration, pure FAQ retrieval system
✅ **Multi-Tenant** - Team-level data isolation with ChromaDB collections
✅ **Local Embeddings** - Using sentence-transformers (offline, private, free)
✅ **Vector Search** - Fast semantic similarity search via ChromaDB
✅ **Query Processing** - Normalization, classification, and expansion
✅ **REST API** - FastAPI with automatic Swagger UI documentation
✅ **Python SDK** - Direct library usage for Python services
✅ **Adaptive Retrieval** - Different strategies for different query types
✅ **Enterprise Ready** - Type-safe (Pydantic), comprehensive error handling, logging

## Quick Start

### Installation

1. Clone/download the framework
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (optional):
```bash
cp .env.example .env
# Edit .env if needed
```

### Usage - Python SDK

```python
from src.sdk.client import RAGClient

# Create client
client = RAGClient()

# Ingest FAQs
client.ingest_faqs(
    team_id="team-1",
    faqs=[
        {
            "id": "faq-001",
            "question": "How do I reset my password?",
            "answer": "Click Settings > Security > Change Password",
            "category": "account"
        }
    ]
)

# Retrieve
results = client.retrieve(
    query="How to reset password?",
    team_id="team-1",
    top_k=5
)

# Process results
for result in results.results:
    print(f"{result.rank}. {result.content} (score: {result.relevance_score:.1%})")
```

### Usage - REST API

Start the server:
```bash
python run_api.py
```

Then use the API:
```bash
# Retrieve
curl -X POST http://localhost:8000/api/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to reset password?",
    "team_id": "team-1",
    "top_k": 5
  }'

# Ingest
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team-1",
    "faqs": [...]
  }'

# Health check
curl http://localhost:8000/api/v1/health

# Statistics
curl http://localhost:8000/api/v1/stats/team-1
```

Visit API docs: http://localhost:8000/docs

## Architecture

### Layered Design

```
┌─────────────────────────────────────────┐
│     REST API / Python SDK               │
│   (FastAPI routes, SDK client)          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   RAG Orchestrator                      │
│   (Coordinates retrieval pipeline)      │
└────────────────┬────────────────────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
┌─────▼──┐  ┌────▼──────┐  ┌─────▼─────┐
│ Query  │  │ Embedding │  │  Vector   │
│Process │  │  Service  │  │  Store    │
└────────┘  └───────────┘  └───────────┘
                             (ChromaDB)
```

### Core Components

1. **Embedding Service** (`src/services/embedding_service.py`)
   - Local text-to-vector conversion
   - Uses sentence-transformers (all-MiniLM-L6-v2)
   - 384-dimensional vectors
   - Free, offline, private

2. **Vector Store** (`src/services/chroma_vector_store.py`)
   - ChromaDB-based vector storage
   - Team-scoped collections (isolation)
   - Persistent storage (survives restarts)
   - Fast kNN search

3. **Ingestion Service** (`src/services/ingestion_service.py`)
   - Load FAQs from JSON/file
   - Chunk long documents
   - Extract keywords and entities
   - Embed and store

4. **Query Processor** (`src/services/query_processor.py`)
   - Normalize queries
   - Classify query type (HOW_TO, TROUBLESHOOTING, SEARCH, GENERAL)
   - Expand queries with synonyms
   - Validate and sanitize

5. **RAG Orchestrator** (`src/services/rag_orchestrator.py`)
   - Main retrieval pipeline
   - Combines all services
   - Scores and ranks results
   - Multi-pass retrieval with expansion

6. **REST API** (`src/api/routes.py`)
   - FastAPI endpoints
   - Automatic Swagger UI docs
   - Error handling

7. **Python SDK** (`src/sdk/client.py`)
   - Simple Python interface
   - Direct library usage
   - Type hints for IDE support

## Data Flow Examples

### Ingestion Flow

```
FAQ JSON
├─ ID: "faq-001"
├─ Question: "How do I reset my password?"
├─ Answer: "Click Settings > Security > Change Password..."
├─ Category: "account"
└─ Keywords: ["password", "reset", "account"]
        ↓
[Document Ingestion Service]
├─ Chunk (if needed)
├─ Extract keywords/entities
├─ Embed text
└─ Create Document objects
        ↓
{
  "id": "faq-001-chunk-0",
  "content": "Click Settings > Security > Change Password",
  "embedding": [0.123, 0.456, ...],  // 384 dims
  "category": "account",
  "keywords": ["password", "reset"]
}
        ↓
[ChromaDB - Team 1 Collection]
├─ Persistent storage
└─ Ready for vector search
```

### Retrieval Flow

```
User Query: "How do I reset my password?"
        ↓
[Query Processor]
├─ Normalize → "reset password"
├─ Classify → QueryType.HOW_TO
├─ Expand → ["reset password", "change password", ...]
└─ Validate → OK
        ↓
[Embedding Service]
└─ Convert to vector [0.234, 0.567, ...]
        ↓
[Vector Store - Team 1 Collection]
├─ Search for similar vectors
└─ Return top-5 (doc_id, score, metadata)
        ↓
[RAG Orchestrator]
├─ Score results
├─ Rank by relevance
└─ Create SearchResult objects
        ↓
RetrievalResult
├─ Query: "reset password"
├─ Results: [
│   {
│     "rank": 1,
│     "relevance_score": 0.92,
│     "content": "Click Settings > Security...",
│     "category": "account"
│   }
│ ]
└─ execution_time_ms: 42.5
```

## Configuration

Edit `.env.example` or environment variables:

```env
# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Free, 80MB
VECTOR_DIMENSION=384

# Vector Store
VECTOR_STORE_TYPE=chromadb
CHROMA_PERSIST_DIR=./chroma_data

# RAG Features
ENABLE_QUERY_EXPANSION=true
ENABLE_RERANKING=true
ENABLE_HYBRID_SEARCH=true
DEFAULT_TOP_K=5

# Logging
LOG_LEVEL=INFO
```

## Multi-Tenancy Model

Team-level isolation (NOT organization-level):

```
RAG Framework
├─ team-1 (Collection: "team_1_documents")
│  ├─ doc-1: "How to reset password"
│  ├─ doc-2: "How to create account"
│  └─ doc-3: "Two-factor authentication"
├─ team-2 (Collection: "team_2_documents")
│  ├─ doc-1: "GET /users endpoint"
│  └─ doc-2: "API authentication"
└─ team-3 (Collection: "team_3_documents")
   └─ [empty - collection created on first ingest]

Key: Same FAQ pool (each team manages their own), separate ChromaDB collections
Benefits: Data isolation, team autonomy, scalability
```

## Examples

### Example 1: Basic Retrieval

```python
from src.sdk.client import RAGClient

client = RAGClient()

# Search for password reset help
results = client.retrieve(
    query="I forgot my password, how to reset?",
    team_id="team-1"
)

print(f"Found {len(results.results)} results")
for r in results.results:
    print(f"- {r.content}")
```

### Example 2: Batch Ingestion

```python
import json

# Load FAQs from file
with open("faqs.json") as f:
    faqs = json.load(f)

# Ingest for team
stats = client.ingest_faqs(
    team_id="team-1",
    faqs=faqs,
    category="support"  # Override category
)

print(f"Ingested {stats['total_documents']} documents")
```

### Example 3: Health Monitoring

```python
health = client.health_check()

if health["overall"] == "healthy":
    print("✓ All systems operational")
else:
    print("⚠ Service degraded:")
    print(health)
```

### Example 4: REST API Usage

```bash
# Retrieve via curl
curl -X POST http://localhost:8000/api/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to reset password",
    "team_id": "team-1",
    "top_k": 5
  }'

# Ingest via curl
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team-1",
    "faqs": [
      {
        "id": "faq-001",
        "question": "How to reset?",
        "answer": "Click Settings...",
        "category": "account"
      }
    ]
  }'
```

## Project Structure

```
rag_framework/
├── src/
│   ├── config/
│   │   ├── settings.py          # Configuration management
│   │   └── __init__.py
│   ├── domain/
│   │   ├── models.py            # Pydantic data models
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── __init__.py
│   ├── services/
│   │   ├── embedding_service.py     # Text → Vector
│   │   ├── chroma_vector_store.py   # Vector storage
│   │   ├── ingestion_service.py     # FAQ loading
│   │   ├── query_processor.py       # Query processing
│   │   ├── rag_orchestrator.py      # Main pipeline
│   │   └── __init__.py
│   ├── api/
│   │   ├── routes.py            # FastAPI endpoints
│   │   ├── app.py               # FastAPI setup
│   │   └── __init__.py
│   ├── sdk/
│   │   ├── client.py            # Python SDK
│   │   └── __init__.py
│   └── __init__.py
├── requirements.txt              # Dependencies
├── .env.example                  # Configuration template
├── run_api.py                    # Start REST API
├── example_usage.py              # Example: vector store usage
├── example_sdk_usage.py          # Example: SDK usage
└── README.md                     # This file
```

## Dependencies

See `requirements.txt`:
- **chromadb** - Vector database
- **sentence-transformers** - Local embeddings
- **FastAPI** - REST API framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **pydantic-settings** - Configuration
- **numpy, pandas** - Data processing
- **networkx** - Graph operations (future)
- **pytest** - Testing

## API Endpoints

### POST `/api/v1/retrieve`
Main retrieval endpoint. Search for relevant FAQs.

**Request:**
```json
{
  "query": "How do I reset my password?",
  "team_id": "team-1",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": "reset password",
  "results": [
    {
      "rank": 1,
      "relevance_score": 0.92,
      "content": "Click Settings > Security > Change Password",
      "category": "account",
      "source": "chromadb_vector_search"
    }
  ],
  "execution_time_ms": 42.5,
  "retrieval_method": "vector_search",
  "confidence_score": 0.92
}
```

### POST `/api/v1/ingest`
Ingest FAQ documents.

**Request:**
```json
{
  "team_id": "team-1",
  "faqs": [
    {
      "id": "faq-001",
      "question": "How to reset?",
      "answer": "Click Settings...",
      "category": "account"
    }
  ]
}
```

**Response:**
```json
{
  "team_id": "team-1",
  "total_faqs": 1,
  "total_documents": 1,
  "errors": [],
  "success": true
}
```

### GET `/api/v1/health`
Health check for all components.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "embedding_service": "healthy",
    "vector_store": "healthy",
    "overall": "healthy"
  },
  "message": "All systems operational"
}
```

### GET `/api/v1/stats/:team_id`
Get statistics for a team.

**Response:**
```json
{
  "team_id": "team-1",
  "document_count": 1523,
  "vector_dimension": 384,
  "collection_name": "team_1_documents"
}
```

### POST `/api/v1/retrieve-expanded`
Multi-pass retrieval with query expansion.

**Request:** Same as `/retrieve`

**Response:** Same as `/retrieve` (but with expanded search)

## Troubleshooting

### No results returned
1. Check if FAQs were ingested: `GET /api/v1/stats/team-id`
2. Verify team_id in request matches ingestion team_id
3. Try a simpler query: "password reset" instead of complex sentence

### Slow retrieval
1. Check health: `GET /api/v1/health`
2. Monitor Embedding Service load
3. Reduce top_k parameter

### Memory usage
1. Reduce number of ingested documents
2. Use filtering/metadata queries
3. Monitor ChromaDB via `get_stats`

## Performance

Benchmarks (on standard hardware):

| Operation | Time |
|-----------|------|
| Embed single query (384 dims) | ~10-50ms |
| Vector search (10k docs) | ~20-100ms |
| Total retrieve (end-to-end) | ~50-200ms |
| Ingest (100 docs) | ~5-10s |

## Security Considerations

1. **Team Isolation:** Enforced at ChromaDB collection level
2. **Query Validation:** Input sanitization + max length check
3. **No External APIs:** Everything runs locally
4. **Embedding Privacy:** All data processed on-device

## Future Enhancements

- [ ] Graph-based entity relationships (NetworkX)
- [ ] Keyword search hybrid (combining with vector search)
- [ ] Advanced reranking algorithms
- [ ] Query caching
- [ ] Analytics and usage tracking
- [ ] Advanced NER for entity extraction
- [ ] Support for different embedding models
- [ ] Batch processing optimizations
- [ ] Elasticsearch backend support
- [ ] Redis caching layer

## Contributing

The framework is modular and extensible:

1. **Add new retrieval strategy:** Create new service, update orchestrator
2. **Add new API endpoint:** Edit `src/api/routes.py`
3. **Add new embedding model:** Update `src/config/settings.py`
4. **Add new query processor:** Create new class in `src/services/`

## License

MIT License

## Support

- API Docs: http://localhost:8000/docs
- Examples: `example_usage.py`, `example_sdk_usage.py`
- Code: Well-documented with inline comments
