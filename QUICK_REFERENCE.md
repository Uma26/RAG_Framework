# Quick Reference Card

## Setup & Run

```bash
cd C:\Users\DELL\Documents\uma\code\rag_framework

# Exercise 1: SDK Basics (10 min)
python exercise_1_basic_sdk.py

# Exercise 2: CLI App (15 min)
python exercise_2_cli_app.py

# Exercise 3: REST API (12 min) - needs 2 terminals
python run_api.py                    # Terminal 1
python exercise_3_rest_api.py        # Terminal 2

# Exercise 4: Extensions (10 min)
python exercise_4_extend_framework.py
```

---

## Core SDK Patterns

### Pattern 1: Ingest Content
```python
from src.sdk.client import RAGClient

client = RAGClient()

# Single item
client.ingest_single(
    team_id="my-team",
    content={
        "id": "doc-001",
        "title": "Question",
        "body": "Answer here...",
        "content_type": "faq",
        "category": "general"
    }
)

# Multiple items
client.ingest_content(
    team_id="my-team",
    content=[...],  # List of dicts
    content_type="faq"
)

# From file
client.ingest_from_file(
    team_id="my-team",
    file_path="data.json"
)
```

### Pattern 2: Retrieve Answers
```python
# Standard retrieval
results = client.retrieve(
    query="How do I...?",
    team_id="my-team",
    top_k=5
)

# With expansion (multi-pass)
results = client.retrieve_expanded(
    query="topic",
    team_id="my-team"
)

# Process results
for result in results.results:
    print(f"Rank {result.rank}: {result.content}")
    print(f"Score: {result.relevance_score:.1%}")
    print(f"Type: {result.content_type}")
```

### Pattern 3: Team Management
```python
# Get team statistics
stats = client.get_stats("my-team")
# {
#   "team_id": "my-team",
#   "document_count": 1523,
#   "vector_dimension": 384,
#   "collection_name": "my_team_documents"
# }

# Health check
health = client.health_check()

# Delete content
result = client.delete_content("my-team", "doc-001")
```

---

## REST API Endpoints

```bash
# Health
GET /api/v1/health

# Ingest
POST /api/v1/ingest
{
  "team_id": "team-1",
  "content": [{...}, {...}],
  "content_type": "faq"
}

# Retrieve
POST /api/v1/retrieve
{
  "query": "...",
  "team_id": "team-1",
  "top_k": 5
}

# Retrieve Expanded
POST /api/v1/retrieve-expanded
{
  "query": "...",
  "team_id": "team-1",
  "top_k": 5
}

# Stats
GET /api/v1/stats/{team_id}
```

---

## Content Types

```python
from src.domain.models import ContentType

# Available types
ContentType.FAQ              # Q&A pairs
ContentType.DOCUMENTATION   # Technical docs
ContentType.CODE            # Code snippets
ContentType.RESEARCH        # Papers, articles
ContentType.KNOWLEDGE_BASE  # Wiki entries
ContentType.TRANSCRIPT      # Meetings, videos
ContentType.LOG             # Event logs
ContentType.GENERIC         # Unknown type

# Use in content
{
    "id": "doc-001",
    "title": "...",
    "body": "...",
    "content_type": "documentation",  # Enum value
    "category": "api"
}
```

---

## Configuration (in .env)

```bash
# Embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DIMENSION=384

# ChromaDB storage
CHROMA_PERSIST_DIR=./chroma_data

# API settings
DEFAULT_TOP_K=5
ENABLE_QUERY_EXPANSION=true
ENABLE_RERANKING=false

# Features
ENABLE_HYBRID_SEARCH=false
```

---

## Performance Metrics

```
Ingestion:
  - 68.6 documents/second
  - 14.6ms per document
  - Throughput: 4,116 docs/minute

Retrieval:
  - 78.5 queries/second
  - 12.7ms per query
  - Latency: <50ms (p95)

Scalability:
  - No HTTP overhead with SDK
  - Team isolation at storage layer
  - Supports millions of vectors
```

---

## Architecture Layers

```
┌─────────────────────────────┐
│  Application (Your Code)    │
├─────────────────────────────┤
│  API/SDK Layer              │
│  ├─ FastAPI Routes          │
│  └─ RAGClient               │
├─────────────────────────────┤
│  Services (5 Core)          │
│  ├─ ContentIngestionService │
│  ├─ EmbeddingService        │
│  ├─ ChromaDBVectorStore     │
│  ├─ QueryProcessorService   │
│  └─ RAGOrchestratorService  │
├─────────────────────────────┤
│  Domain Models              │
│  ├─ Content                 │
│  ├─ Chunk                   │
│  └─ SearchResult            │
├─────────────────────────────┤
│  Configuration (Singleton)  │
├─────────────────────────────┤
│  External Systems           │
│  ├─ ChromaDB                │
│  └─ sentence-transformers   │
└─────────────────────────────┘
```

---

## Common Tasks

### Task 1: Build a Support Bot
```python
client = RAGClient()

# Ingest FAQs
client.ingest_content("support", faqs)

# Answer user questions
def answer(question):
    results = client.retrieve(question, "support")
    if results.results:
        return results.results[0].content
    return "Sorry, I don't know that."
```

### Task 2: Search Multiple Content Types
```python
# Ingest mixed content
client.ingest_content("docs", [
    faq_item,           # FAQ
    code_snippet,       # CODE
    documentation       # DOCUMENTATION
])

# Search finds all types
results = client.retrieve("query", "docs")
# Results include all content types
```

### Task 3: Multi-Team System
```python
# Each team has isolated data
client.ingest_content("team-a", team_a_faqs)
client.ingest_content("team-b", team_b_faqs)

# Search returns only team data
results_a = client.retrieve("query", "team-a")  # Only team-a
results_b = client.retrieve("query", "team-b")  # Only team-b
```

### Task 4: Performance Analysis
```python
# Benchmark ingestion
import time
start = time.time()
client.ingest_content("test", big_content_list)
print(f"Ingestion: {(time.time()-start):.2f}s")

# Check retrieval time
results = client.retrieve("query", "test")
print(f"Query time: {results.execution_time_ms:.0f}ms")
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ChromaDB errors | Ensure `chroma_data/` exists and is writable |
| Low scores | Try `retrieve_expanded()` or improve keywords |
| API connection | Ensure `python run_api.py` is running |
| Slow queries | Check team size with `get_stats()` |
| Wrong results | Add more specific keywords to content |

---

## Files Location

```
C:\Users\DELL\Documents\uma\code\rag_framework\

├── exercise_1_basic_sdk.py          # SDK demo
├── exercise_2_cli_app.py            # CLI app
├── exercise_3_rest_api.py           # API testing
├── exercise_4_extend_framework.py   # Extensions

├── PRACTICAL_TRAINING_GUIDE.md      # Full guide
├── TRAINING_COMPLETION_SUMMARY.md   # Summary
├── QUICK_REFERENCE.md               # This file

├── run_api.py                       # Start server
├── src/
│   ├── config/settings.py           # Configuration
│   ├── domain/models.py             # Data models
│   ├── services/                    # 5 core services
│   ├── api/routes.py                # REST endpoints
│   └── sdk/client.py                # Python SDK

└── chroma_data/                     # Vector storage
```

---

## Key Concepts

**ContentType:** Tag indicating what kind of content (FAQ, Code, Docs, etc.)

**Chunk:** Piece of content with embedding vector, used for storage & search

**Team Isolation:** Each team has separate ChromaDB collection, completely isolated

**Relevance Score:** 0-1 indicating how well result matches query

**Query Expansion:** Try multiple query variations to find more results

**Semantic Search:** Match by meaning, not just keywords

**Vector:** 384-dimensional number representing text meaning

**Embedding:** Process of converting text to vector

---

## Next: Try It!

1. **Start with Exercise 1** - See it work
2. **Try Exercise 2** - Build interactive app
3. **Test Exercise 3** - Use REST API
4. **Explore Exercise 4** - Add features

**Total time: ~45 minutes**

---

**Questions? Check the full guides in the framework directory! 🚀**
