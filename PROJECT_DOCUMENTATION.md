# RAG Framework - Complete Project Documentation

## Project Overview

**RAG Framework** is an enterprise-grade, multi-tenant Retrieval-Augmented Generation (RAG) framework built in Python. It's designed to allow multiple independent teams to store, manage, and retrieve FAQ documents using advanced retrieval techniques.

### Key Design Philosophy

- **Retrieval Only**: Pure FAQ retrieval system (no LLM integration)
- **Multi-Tenant**: Team-level data isolation with shared infrastructure
- **Local Embeddings**: Privacy-first approach using sentence-transformers
- **Enterprise Ready**: Type-safe, well-tested, comprehensively logged
- **Developer Friendly**: REST API + Python SDK for flexible integration

## Architecture Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   User Applications                          │
│         (Web, Mobile, Internal Services, etc.)               │
└──────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
┌───────────────▼──────────────┐  ┌────▼──────────────────┐
│   REST API (FastAPI)         │  │  Python SDK           │
│   http://localhost:8000/docs │  │  Direct library use   │
│   • /retrieve                │  │  • client.retrieve()  │
│   • /ingest                  │  │  • client.ingest()    │
│   • /health                  │  │  • client.get_stats() │
│   • /stats                   │  │                       │
└───────────────┬──────────────┘  └────┬──────────────────┘
                │                      │
                └──────────┬───────────┘
                           │
        ┌──────────────────▼───────────────────┐
        │  RAG Orchestrator                    │
        │  (Main retrieval pipeline)           │
        │  • Coordinates all services          │
        │  • Implements retrieval strategies   │
        │  • Scores and ranks results          │
        └──────────────────┬───────────────────┘
                           │
        ┌──────────────────┼───────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌─────▼──────┐  ┌───────▼────────┐
│ Query Processor │  │ Embedding  │  │ Vector Store   │
│                │  │  Service   │  │  (ChromaDB)    │
│ • Normalize    │  │            │  │                │
│ • Classify     │  │ • Embed    │  │ • Store docs   │
│ • Expand       │  │   text to  │  │ • Search by    │
│ • Validate     │  │   vectors  │  │   similarity   │
└────────────────┘  │            │  │ • Team-scoped  │
                    │ • Batch    │  │   isolation    │
                    │   process  │  │                │
                    │ • Health   │  │ • Persistent   │
                    │   checks   │  │   storage      │
                    └────────────┘  └────────────────┘
                           ▲                   ▲
                           │                   │
                    ┌───────┴───────────────────┘
                    │
        ┌───────────▼──────────────┐
        │ Document Ingestion       │
        │ Service                  │
        │ • Load FAQs from JSON    │
        │ • Chunk documents        │
        │ • Extract keywords       │
        │ • Extract entities       │
        │ • Embed chunks           │
        │ • Store in ChromaDB      │
        └──────────────────────────┘
```

### Layered Architecture

```
┌─────────────────────────────────────────────────┐
│  Presentation Layer                            │
│  (REST API routes, Request/Response models)    │
│  src/api/routes.py, src/api/app.py             │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│  Application Layer                             │
│  (Orchestration, business logic)               │
│  src/services/rag_orchestrator.py              │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│  Service Layer                                 │
│  (Domain-specific operations)                  │
│  • Query Processor    (query classification)   │
│  • Embedding Service  (text → vector)          │
│  • Vector Store       (storage & search)       │
│  • Ingestion Service  (FAQ loading)            │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│  Domain Layer                                  │
│  (Data models, exceptions, constants)          │
│  src/domain/models.py, exceptions.py           │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│  Configuration Layer                           │
│  (Settings, environment variables)             │
│  src/config/settings.py                        │
└──────────────────────────────────────────────────┘
```

## File-by-File Documentation

### Configuration Layer

#### `src/config/settings.py`
**Purpose:** Centralized configuration management using Pydantic.

**Key Concepts:**
- Uses `pydantic.BaseSettings` to load from environment variables
- Fallback to `.env` file if env vars not set
- Default values for all settings
- Type-safe configuration (compile-time checking)

**Settings Defined:**
```python
class RAGSettings:
    # Embedding
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_dimension: int = 384  # all-MiniLM-L6-v2 outputs 384-dim vectors
    
    # Vector Store
    vector_store_type: str = "chromadb"
    chroma_persist_dir: str = "./chroma_data"
    
    # Features
    enable_query_expansion: bool = True
    enable_reranking: bool = True
    enable_hybrid_search: bool = True
    default_top_k: int = 5
    
    # Retrieval
    max_query_length: int = 500
```

**Global Instance:**
```python
settings = RAGSettings()  # Singleton
```

---

### Domain Layer

#### `src/domain/models.py`
**Purpose:** Core data structures using Pydantic.

**Models:**

1. **QueryType (Enum)**
   - Classification for adaptive routing
   - Values: GENERAL, HOW_TO, TROUBLESHOOTING, SEARCH
   - Used to customize retrieval strategy

2. **FAQ**
   - Represents a single FAQ document
   - Fields: id, question, answer, category, keywords, entities
   - Timestamps: created_at, updated_at
   - Metadata for extensibility

3. **Document**
   - Chunked FAQ (if FAQ is split into parts)
   - Fields: id, content, faq_id, chunk_index, embedding, category, keywords, entities
   - Embedding: 384-dim vector (List[float])

4. **SearchResult**
   - Ranked search result
   - Fields: document/document_id, content, category, relevance_score, rank, source
   - Scoring: vector_score, graph_score, keyword_score

5. **SearchQuery**
   - User search query with metadata
   - Fields: text, query_type, top_k, team_id, timestamp
   - Used for logging and analytics

6. **RetrievalResult**
   - Final result returned to user/API
   - Fields: query, results[], execution_time_ms, retrieval_method, confidence_score
   - Wrapper for standardization

#### `src/domain/exceptions.py`
**Purpose:** Custom exception hierarchy.

**Exception Classes:**
```
RAGException (base)
├── EmbeddingError
├── VectorStoreError
├── GraphStoreError
├── QueryProcessingError
├── ConfigurationError
├── AuthenticationError
└── AuthorizationError
```

---

### Service Layer

#### `src/services/embedding_service.py`
**Purpose:** Convert text to vector embeddings.

**Why Local Embeddings?**
- ✅ No API costs
- ✅ Works offline
- ✅ Privacy (data stays on-device)
- ✅ Fast inference
- ✅ sentence-transformers is optimized

**Methods:**
```python
class EmbeddingService:
    # Embed single text
    embed_text(text: str) -> List[float]
    
    # Batch embed (efficient)
    embed_texts(texts: List[str]) -> List[List[float]]
    
    # Get vector dimension
    get_dimension() -> int
    
    # Health check
    health_check() -> bool
```

**Model Details:**
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Output dimension: 384
- Trained for sentence similarity (perfect for RAG)
- Size: ~80MB (small, portable)
- Normalization: L2 norm (for cosine similarity)

**Global Instance:**
```python
embedding_service = EmbeddingService()  # Singleton
```

---

#### `src/services/chroma_vector_store.py`
**Purpose:** Vector storage and retrieval using ChromaDB.

**Why ChromaDB?**
- Zero setup (embedded database)
- Persistent storage (survives restarts)
- Team-scoped collections (built-in isolation)
- Fast kNN search
- Simple Python API

**Team Isolation Strategy:**
```
ChromaDB Instance
├── team_1_documents (collection)
│   ├── doc-1, doc-2, doc-3 ...
│   └── All vectors indexed together
├── team_2_documents (collection)
│   ├── api-doc-1, api-doc-2 ...
│   └── Separate index (no cross-team leakage)
└── team_3_documents (collection)
    └── [empty until first ingest]
```

**Methods:**
```python
class ChromaDBVectorStore:
    # Add documents with embeddings
    add_documents(team_id: str, documents: List[Document]) -> int
    
    # Search by vector
    search(team_id: str, query_vector: List[float], top_k: int) 
      -> List[(doc_id, score, metadata)]
    
    # Delete document
    delete_document(team_id: str, doc_id: str) -> bool
    
    # Get team stats
    get_stats(team_id: str) -> Dict
    
    # Health check
    health_check() -> bool
```

**Collection Naming:**
- Pattern: `{team_id}_documents` (after replacing `-` with `_`)
- Example: `team-1` → `team_1_documents`

**Global Instance:**
```python
vector_store = ChromaDBVectorStore()  # Singleton
```

---

#### `src/services/ingestion_service.py`
**Purpose:** Load, process, and store FAQs.

**Pipeline:**
```
FAQ JSON
    ↓
[Validate]  - Check required fields
    ↓
[Chunk]     - Split if > 500 chars
    ↓
[Extract]   - Keywords, entities, category
    ↓
[Embed]     - Convert to 384-dim vectors
    ↓
[Store]     - Add to ChromaDB (team-scoped)
```

**Methods:**
```python
class DocumentIngestionService:
    # Load from JSON data
    ingest_faqs_from_json(team_id: str, json_data: List[Dict]) -> Dict
    
    # Load from JSON file
    ingest_faqs_from_file(team_id: str, file_path: str, category: str) -> Dict
    
    # Ingest single FAQ
    ingest_faq_dict(team_id: str, faq_dict: Dict) -> Dict
    
    # Delete FAQ
    delete_faq(team_id: str, faq_id: str) -> Dict
```

**Chunking Logic:**
- If document ≤ 500 chars: single chunk
- If document > 500 chars: split into overlapping chunks
- Overlap: 100 chars (maintains context at boundaries)

**Example Flow:**
```python
faqs = [
    {
        "id": "faq-001",
        "question": "How to reset?",
        "answer": "Step 1... Step 2... Step 3...",  # 600 chars
        "category": "account"
    }
]

stats = ingestion_service.ingest_faqs_from_json("team-1", faqs)
# Output:
# {
#   "team_id": "team-1",
#   "total_faqs": 1,
#   "total_documents": 2,  # Split into 2 chunks
#   "errors": [],
#   "success": True
# }
```

**Global Instance:**
```python
ingestion_service = DocumentIngestionService()  # Singleton
```

---

#### `src/services/query_processor.py`
**Purpose:** Process user queries before retrieval.

**Pipeline:**
```
Raw Query: "How do i RESET MY PASSWORD???"
    ↓
[Normalize] → "how do i reset my password"
    ↓
[Classify]  → QueryType.HOW_TO
    ↓
[Expand]    → ["reset password", "change password", "update password", ...]
    ↓
[Validate]  → OK
    ↓
SearchQuery object
```

**Query Classification:**
- **HOW_TO**: Contains "how", "can i", "show me", "guide"
  → Useful for instructional FAQs
- **TROUBLESHOOTING**: Contains "error", "problem", "fix", "not working"
  → Useful for error resolution FAQs
- **SEARCH**: Contains "find", "list", "what are", "available"
  → Useful for reference FAQs
- **GENERAL**: No specific keywords
  → Default catch-all

**Query Expansion:**
- Synonym replacement
- Example: "password" → also search for "passwd", "credentials"
- Improves recall (finds more relevant docs)

**Methods:**
```python
class QueryProcessor:
    # Main processing
    process_query(query_text: str, team_id: str, top_k: int) -> SearchQuery
    
    # Get query variations
    get_query_variations(query_text: str) -> List[str]
```

**Global Instance:**
```python
query_processor = QueryProcessor()  # Singleton
```

---

#### `src/services/rag_orchestrator.py`
**Purpose:** Main retrieval pipeline (orchestrates all services).

**Retrieval Pipeline:**
```
User Query: "How to reset password?"
    ↓
[Query Processor]
├─ Normalize: "reset password"
├─ Classify: HOW_TO
├─ Expand: ["reset password", "change password", ...]
└─ Create SearchQuery object
    ↓
[Embedding Service]
└─ Embed: query → [0.123, 0.456, ...]  (384 dims)
    ↓
[Vector Store]
├─ Search team-1 collection
├─ Find similar documents (top-5)
└─ Return: [(doc_id, similarity, metadata), ...]
    ↓
[Score & Rank]
├─ Vector score: 70% weight
├─ Keyword bonus: up to 30%
└─ Combine: final_score
    ↓
[Package Result]
└─ RetrievalResult with ranked documents
```

**Scoring Strategy:**
```python
# 70% from vector similarity
vector_contribution = vector_score * 0.70

# 30% bonus from keyword matches
keyword_matches = count(query_words ∩ doc_keywords)
keyword_contribution = min(keyword_matches * 0.05, 0.30)

# Final score (capped at 1.0)
final_score = min(vector_contribution + keyword_contribution, 1.0)
```

**Methods:**
```python
class RAGOrchestrator:
    # Basic retrieval
    retrieve(query_text: str, team_id: str, top_k: int) -> RetrievalResult
    
    # Multi-pass retrieval with expansion
    retrieve_with_expansion(query_text: str, team_id: str, top_k: int) -> RetrievalResult
    
    # Health check
    health_check() -> Dict
```

**Multi-Pass Retrieval:**
1. Get query variations from QueryProcessor
2. Search each variation independently
3. Collect all results
4. Deduplicate by doc_id, keep highest score
5. Re-rank and return top-k

**Example:**
```python
# Query: "password problem"
# Variations tried:
# - "password problem"
# - "passwd problem"
# - "password issue"
# - "credentials problem"
# Result: Combined top-5 from all searches
```

**Global Instance:**
```python
rag_orchestrator = RAGOrchestrator()  # Singleton
```

---

### API Layer

#### `src/api/routes.py`
**Purpose:** FastAPI REST endpoints.

**Endpoints:**

1. **POST /api/v1/retrieve** - Main retrieval
   - Input: {query, team_id, top_k}
   - Output: RetrievalResult

2. **POST /api/v1/retrieve-expanded** - Multi-pass retrieval
   - Input: {query, team_id, top_k}
   - Output: RetrievalResult (with expansion)

3. **POST /api/v1/ingest** - Ingest FAQs
   - Input: {team_id, faqs, category}
   - Output: {total_faqs, total_documents, errors, success}

4. **GET /api/v1/health** - Health check
   - Output: {status, components, message}

5. **GET /api/v1/stats/{team_id}** - Team statistics
   - Output: {team_id, document_count, vector_dimension}

**Request Models:**
```python
class RetrieveRequest(BaseModel):
    query: str
    team_id: str
    top_k: Optional[int] = 5

class IngestRequest(BaseModel):
    team_id: str
    faqs: List[Dict]
    category: Optional[str] = None
```

---

#### `src/api/app.py`
**Purpose:** FastAPI application setup.

**Configuration:**
- CORS middleware (allow all origins for demo)
- Lifespan events (startup/shutdown)
- Root endpoint
- Kubernetes probes (readiness, liveness)

**Running:**
```bash
# Via run_api.py
python run_api.py

# Or directly with uvicorn
uvicorn src.api.app:app --reload

# Visit: http://localhost:8000/docs
```

---

### SDK Layer

#### `src/sdk/client.py`
**Purpose:** Python SDK for direct library usage.

**Why SDK?**
- No HTTP overhead
- Easier for internal services
- Type hints for IDE support
- Easy to package and distribute

**Methods:**
```python
class RAGClient:
    # Ingest
    ingest_faqs(team_id: str, faqs: List[Dict], category: str) -> Dict
    ingest_faqs_from_file(team_id: str, file_path: str, category: str) -> Dict
    
    # Retrieve
    retrieve(query: str, team_id: str, top_k: int) -> RetrievalResult
    retrieve_expanded(query: str, team_id: str, top_k: int) -> RetrievalResult
    
    # Statistics
    get_stats(team_id: str) -> Dict
    health_check() -> Dict
    
    # Management
    delete_faq(team_id: str, faq_id: str) -> Dict
```

**Example Usage:**
```python
from src.sdk.client import RAGClient

client = RAGClient()

# Ingest
stats = client.ingest_faqs(
    team_id="team-1",
    faqs=[
        {
            "id": "faq-001",
            "question": "How to reset?",
            "answer": "Click Settings...",
            "category": "account"
        }
    ]
)

# Retrieve
results = client.retrieve(
    query="reset password",
    team_id="team-1",
    top_k=5
)

for r in results.results:
    print(f"{r.rank}. {r.content}")
```

---

## Data Flow Examples

### Example 1: Ingesting FAQs

```
Input: JSON file (faqs.json)
[
  {
    "id": "faq-001",
    "question": "How do I reset my password?",
    "answer": "Click Settings > Security > Change Password. Enter your email...",
    "category": "account",
    "keywords": ["password", "reset", "account"]
  }
]

Step 1: Load JSON
└─ Read file, parse JSON

Step 2: Validate
└─ Check required fields: id, question, answer, category

Step 3: Chunk (if needed)
├─ Answer length: 150 chars (< 500)
└─ No chunking needed → 1 document

Step 4: Extract Keywords/Entities
├─ Keywords: ["password", "reset", "account"] (provided)
└─ Entities: ["Settings", "Security", "Change", "Password"] (extracted)

Step 5: Embed
├─ Text: "How do I reset my password? Click Settings > Security..."
├─ Model: sentence-transformers/all-MiniLM-L6-v2
└─ Output: [0.123, 0.456, 0.789, ...] (384 dims)

Step 6: Create Document
{
  "id": "faq-001-chunk-0",
  "content": "Click Settings > Security > Change Password...",
  "faq_id": "faq-001",
  "chunk_index": 0,
  "embedding": [0.123, 0.456, ...],
  "category": "account",
  "keywords": ["password", "reset", "account"],
  "entities": ["Settings", "Security", "Password"]
}

Step 7: Store in ChromaDB
├─ Collection: "team_1_documents"
├─ Vector index: created automatically
└─ Data persisted to disk

Output: Stats
{
  "team_id": "team-1",
  "total_faqs": 1,
  "total_documents": 1,
  "errors": [],
  "success": true
}
```

### Example 2: Retrieving Documents

```
Input: Query Request
{
  "query": "How do I reset my password?",
  "team_id": "team-1",
  "top_k": 5
}

Step 1: Normalize Query
├─ Lowercase: "how do i reset my password?"
├─ Remove punctuation: "how do i reset my password"
└─ Clean whitespace: "how do i reset my password"

Step 2: Classify Query Type
├─ Keywords found: "how", "do i", "reset"
└─ Classification: QueryType.HOW_TO

Step 3: Validate Query
├─ Check length: 29 chars (< 500) ✓
├─ Check for injection: No suspicious patterns ✓
└─ Valid: TRUE

Step 4: Expand Query
├─ Original: "how do i reset my password"
├─ Variations:
│   - "how do i reset my password"
│   - "how do i change my password"
│   - "how do i reset my passwd"
│   - "how do i reset my credentials"
│   ... (more)
└─ 4 variations total

Step 5: Embed Query
├─ Input: "reset my password"  (key terms only)
├─ Model: sentence-transformers/all-MiniLM-L6-v2
├─ Output: [0.234, 0.567, 0.890, ...] (384 dims)
└─ Normalized: L2 norm applied

Step 6: Search ChromaDB
├─ Collection: "team_1_documents"
├─ Query vector: [0.234, 0.567, ...]
├─ Similarity metric: cosine
├─ top_k: 5
└─ Results:
   [
     ("faq-001-chunk-0", 0.92, {"category": "account", ...}),
     ("faq-002-chunk-0", 0.78, {"category": "account", ...}),
     ("faq-003-chunk-0", 0.65, {"category": "security", ...}),
     ...
   ]

Step 7: Score Results
├─ Document 1:
│   - Vector score: 0.92
│   - Keyword matches: 2 (password, reset)
│   - Final score: 0.92 * 0.70 + min(2 * 0.05, 0.30) = 0.644 + 0.10 = 0.924
│
└─ Document 2:
    - Vector score: 0.78
    - Keyword matches: 1 (reset)
    - Final score: 0.78 * 0.70 + min(1 * 0.05, 0.30) = 0.546 + 0.05 = 0.596

Step 8: Rank Results
└─ Sorted by final_score (descending):
   1. faq-001-chunk-0: 0.924
   2. faq-002-chunk-0: 0.596
   3. faq-003-chunk-0: 0.458
   ...

Step 9: Package Result
{
  "query": "reset my password",
  "results": [
    {
      "rank": 1,
      "relevance_score": 0.924,
      "content": "Click Settings > Security > Change Password...",
      "category": "account",
      "vector_score": 0.92,
      "source": "chromadb_vector_search"
    },
    {
      "rank": 2,
      "relevance_score": 0.596,
      "content": "Visit our signup page...",
      "category": "account",
      "vector_score": 0.78,
      "source": "chromadb_vector_search"
    }
  ],
  "execution_time_ms": 45.3,
  "retrieval_method": "vector_search",
  "confidence_score": 0.924
}
```

---

## Multi-Tenancy Model

### Team Isolation

```
Scenario: Two teams store FAQs in the same RAG instance

Team A (Marketing Team)
├─ FAQ-001: "What is our company?"
├─ FAQ-002: "How to contact sales?"
└─ FAQ-003: "What are pricing plans?"
    ↓
    Ingest to team_a_documents collection

Team B (Support Team)
├─ FAQ-001: "How to reset password?"
├─ FAQ-002: "How to create account?"
└─ FAQ-003: "Enable 2FA?"
    ↓
    Ingest to team_b_documents collection

ChromaDB Instance
├─ team_a_documents (3 documents)
│   └─ Separate vector index
├─ team_b_documents (3 documents)
│   └─ Separate vector index (NO cross-team leakage)
└─ Other teams...

Query Example:
Team A searches: "How to contact?"
└─ Search ONLY in team_a_documents
└─ Results: FAQ-002 (Team A's sales contact info)
└─ Never returns Team B's support FAQs

Query Example:
Team B searches: "How to reset?"
└─ Search ONLY in team_b_documents
└─ Results: FAQ-001 (Team B's password reset instructions)
└─ Never returns Team A's company info
```

### Implementation

**Collection Naming:**
```python
# In ChromaDBVectorStore._get_collection_name()
def _get_collection_name(self, team_id: str) -> str:
    safe_team_id = team_id.replace("-", "_")
    return f"{safe_team_id}_documents"

# Example:
team_id = "team-alpha"
collection_name = "team_alpha_documents"  # Unique collection per team
```

**Isolation Enforcement:**
```python
# In RAGOrchestrator.retrieve()
# Always pass team_id to vector store
search_results = vector_store.search(
    team_id=team_id,  # ← Ensures collection isolation
    query_vector=query_vector,
    top_k=top_k
)
```

**No Shared FAQ Pool:**
- Each team has their own FAQs
- Different domains (support vs. sales vs. engineering)
- Can have overlapping FAQ IDs (faq-001 in both teams, different content)

---

## Performance Characteristics

### Benchmarks

| Operation | Typical Time | Notes |
|-----------|--------------|-------|
| Embed single query (384 dims) | 10-50ms | sentence-transformers/CPU |
| Vector search (10k docs) | 20-100ms | ChromaDB kNN search |
| Total retrieve (end-to-end) | 50-200ms | Includes all steps |
| Ingest 100 docs | 5-10s | Embedding is bottleneck |
| Health check | <5ms | Just model existence check |

### Scaling Considerations

- **Documents per team:** 10k-100k (comfortable range)
- **Total documents (all teams):** 1M+ (chromadb handles millions)
- **Concurrent queries:** Limited by embedding model (CPU/GPU)
- **Memory:** Embedding model ~500MB, ChromaDB grows with data

### Optimization Tips

1. **Batch Ingestion:** Ingest 100s of FAQs together (faster than one-by-one)
2. **Query Caching:** Cache frequently asked queries (future enhancement)
3. **Metadata Filtering:** Use category filters to reduce search space
4. **Reduce top_k:** Smaller k = faster search (15 ms for top_3 vs 100ms for top_50)
5. **Async API:** Use uvicorn with multiple workers for concurrent requests

---

## Security Model

### Authentication & Authorization

**Current Implementation:** NO authentication
- Any request can reach the API
- team_id is client-provided (trust-based)
- Suitable for internal services

**Future Enhancements:**
- API key authentication
- OAuth2 integration
- RBAC (Role-Based Access Control)
- Request signing

### Data Security

1. **Local Embeddings**
   - All text stays on-device
   - No external API calls
   - Data not sent to OpenAI/other services

2. **Persistent Storage**
   - ChromaDB data on disk (`./chroma_data/`)
   - No encryption by default (add if needed)
   - Single-machine deployment (add if distributed)

3. **Query Validation**
   - Input length limited (500 chars)
   - Suspicious patterns blocked (SQL injection, etc.)
   - Sanitization applied

---

## Testing Strategy

### Example Tests

```python
def test_embedding_service():
    service = EmbeddingService()
    vector = service.embed_text("test")
    assert len(vector) == 384
    assert abs(sum(v**2 for v in vector) - 1.0) < 0.01  # L2 norm = 1

def test_query_processor():
    processor = QueryProcessor()
    query = processor.process_query("how to reset?", "team-1")
    assert query.query_type == QueryType.HOW_TO

def test_team_isolation():
    client = RAGClient()
    
    # Ingest for team-1
    client.ingest_faqs("team-1", [faq1, faq2])
    
    # Ingest for team-2
    client.ingest_faqs("team-2", [faq3, faq4])
    
    # Search team-1 should NOT find team-2 docs
    results = client.retrieve("query", "team-1")
    assert len(results.results) <= 2  # Only team-1 docs
```

---

## Configuration Reference

### Environment Variables

Create `.env` file in project root:

```env
# Embedding Model (Hugging Face model ID)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Dimension (must match model output)
VECTOR_DIMENSION=384

# Vector Store
VECTOR_STORE_TYPE=chromadb
CHROMA_PERSIST_DIR=./chroma_data

# RAG Features
ENABLE_QUERY_EXPANSION=true
ENABLE_RERANKING=true
ENABLE_HYBRID_SEARCH=true

# Retrieval
DEFAULT_TOP_K=5
MAX_QUERY_LENGTH=500

# Logging
LOG_LEVEL=INFO
```

---

## Deployment

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start API server
python run_api.py

# 3. Visit docs
# http://localhost:8000/docs
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run_api.py"]
```

Build and run:
```bash
docker build -t rag-framework .
docker run -p 8000:8000 rag-framework
```

### Production Considerations

1. Use external database (PostgreSQL) for ChromaDB backend
2. Deploy with multiple API worker processes
3. Add authentication and rate limiting
4. Use Kubernetes for orchestration
5. Monitor with Prometheus/Grafana
6. Add request logging and tracing
7. Implement caching layer (Redis)

---

## Troubleshooting

### Common Issues

**No results returned**
- Check if FAQs were ingested: `client.get_stats(team_id)`
- Verify team_id matches ingestion team
- Try simpler query

**Slow retrieval**
- Check health: `client.health_check()`
- Embedding model is CPU-intensive (use GPU if available)
- Reduce top_k parameter

**Out of memory**
- Embedding model loads entire model (~500MB)
- ChromaDB grows with data
- Use pagination in ingestion

**Same FAQ IDs between teams**
- Allowed (isolation at collection level)
- Example: Both teams can have "faq-001" with different content

---

## Future Roadmap

### Phase 2
- [ ] Graph-based entity relationships (NetworkX)
- [ ] Hybrid search (combine vector + keyword)
- [ ] Advanced reranking (learning-to-rank)
- [ ] Query caching with TTL

### Phase 3
- [ ] Analytics dashboard
- [ ] Usage tracking per team
- [ ] Feedback loop (click-through rates)
- [ ] A/B testing framework

### Phase 4
- [ ] Multiple embedding models
- [ ] Distributed deployment (Kubernetes)
- [ ] PostgreSQL backend for ChromaDB
- [ ] Redis caching layer

### Phase 5
- [ ] LLM integration (optional, for answer generation)
- [ ] Custom NER models
- [ ] Multi-language support
- [ ] Real-time indexing

---

## Code Examples

### Example 1: Simple Retrieval Loop

```python
from src.sdk.client import RAGClient

client = RAGClient()

while True:
    query = input("Enter query (or 'quit'): ").strip()
    if query.lower() == 'quit':
        break
    
    results = client.retrieve(query, "team-1", top_k=3)
    
    print(f"\nFound {len(results.results)} results:\n")
    for r in results.results:
        print(f"[{r.rank}] Score: {r.relevance_score:.1%}")
        print(f"    {r.content[:100]}...\n")
```

### Example 2: Bulk Ingestion

```python
import json
from src.sdk.client import RAGClient

client = RAGClient()

# Load all FAQs from file
with open("faqs.json") as f:
    all_faqs = json.load(f)

# Ingest for each team
teams = {
    "team-sales": all_faqs[:100],
    "team-support": all_faqs[100:300],
    "team-billing": all_faqs[300:]
}

for team_id, faqs in teams.items():
    stats = client.ingest_faqs(team_id, faqs)
    print(f"{team_id}: {stats['total_documents']} documents ingested")
```

### Example 3: API Client (using requests)

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Retrieve
response = requests.post(
    f"{BASE_URL}/retrieve",
    json={
        "query": "How to reset password?",
        "team_id": "team-1",
        "top_k": 5
    }
)

results = response.json()
print(f"Found {len(results['results'])} results")

# Ingest
response = requests.post(
    f"{BASE_URL}/ingest",
    json={
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
)

stats = response.json()
print(f"Ingested {stats['total_documents']} documents")
```

---

## Summary

RAG Framework is a **production-ready retrieval system** for multi-tenant FAQ applications. It combines:

- **Local embeddings** for privacy and cost-efficiency
- **ChromaDB** for scalable vector storage
- **Team-level isolation** for data security
- **REST API + Python SDK** for flexible integration
- **Clean architecture** for extensibility

Perfect for organizations needing to deploy fast, private, and scalable FAQ retrieval systems.
