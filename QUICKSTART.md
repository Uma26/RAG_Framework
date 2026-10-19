# Quick Start - RAG Framework in 5 Minutes

## Installation (1 minute)

```bash
# Navigate to framework directory
cd rag_framework

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import chromadb; import sentence_transformers; print('✓ Dependencies installed')"
```

## Method 1: Python SDK (2 minutes)

```python
# Create file: test_sdk.py
from src.sdk.client import RAGClient

# Initialize client
client = RAGClient()

# Ingest FAQs
faqs = [
    {
        "id": "faq-001",
        "question": "How do I reset my password?",
        "answer": "Click Settings > Security > Change Password",
        "category": "account"
    },
    {
        "id": "faq-002",
        "question": "How do I create an account?",
        "answer": "Visit signup page and enter your email",
        "category": "account"
    }
]

print("Ingesting FAQs...")
stats = client.ingest_faqs("team-1", faqs)
print(f"✓ Ingested {stats['total_documents']} documents\n")

# Retrieve
print("Searching for: 'How to reset password?'")
results = client.retrieve(
    query="How to reset password?",
    team_id="team-1",
    top_k=3
)

print(f"✓ Found {len(results.results)} results:\n")
for r in results.results:
    print(f"  #{r.rank} (Score: {r.relevance_score:.1%})")
    print(f"  → {r.content[:60]}...\n")

# Get stats
print("Team Statistics:")
stats = client.get_stats("team-1")
print(f"  Documents: {stats['document_count']}")
print(f"  Vector dimension: {stats['vector_dimension']}")
```

**Run it:**
```bash
python test_sdk.py
```

**Expected output:**
```
Ingesting FAQs...
✓ Ingested 2 documents

Searching for: 'How to reset password?'
✓ Found 2 results:

  #1 (Score: 92%)
  → Click Settings > Security > Change Password

  #2 (Score: 78%)
  → Visit signup page and enter your email

Team Statistics:
  Documents: 2
  Vector dimension: 384
```

---

## Method 2: REST API (3 minutes)

### Start the API server

```bash
python run_api.py
```

**Output:**
```
======================================================================
RAG Framework API Server
======================================================================

Starting server on http://localhost:8000

API Documentation:
  - Swagger UI:  http://localhost:8000/docs
  - ReDoc:       http://localhost:8000/redoc

Endpoints:
  - POST   /api/v1/retrieve          - Main retrieval
  - POST   /api/v1/retrieve-expanded - Multi-pass retrieval
  - POST   /api/v1/ingest            - Ingest FAQs
  - GET    /api/v1/health            - Health check
  - GET    /api/v1/stats/{team_id}   - Team statistics

Press Ctrl+C to stop the server
======================================================================
```

### In another terminal, use the API

```bash
# Ingest FAQs
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team-1",
    "faqs": [
      {
        "id": "faq-001",
        "question": "How do I reset my password?",
        "answer": "Click Settings > Security > Change Password",
        "category": "account"
      }
    ]
  }'

# Response:
# {
#   "team_id": "team-1",
#   "total_faqs": 1,
#   "total_documents": 1,
#   "errors": [],
#   "success": true
# }
```

```bash
# Retrieve
curl -X POST http://localhost:8000/api/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to reset password?",
    "team_id": "team-1",
    "top_k": 5
  }'

# Response:
# {
#   "query": "reset password",
#   "results": [
#     {
#       "rank": 1,
#       "relevance_score": 0.92,
#       "content": "Click Settings > Security > Change Password",
#       "category": "account",
#       ...
#     }
#   ],
#   "execution_time_ms": 42.5,
#   "retrieval_method": "vector_search",
#   "confidence_score": 0.92
# }
```

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Response:
# {
#   "status": "healthy",
#   "components": {
#     "embedding_service": "healthy",
#     "vector_store": "healthy",
#     "overall": "healthy"
#   },
#   "message": "All systems operational"
# }
```

### Visit the Interactive Docs

Open browser: **http://localhost:8000/docs**

You can test all endpoints directly from the Swagger UI!

---

## Try the Examples

### Example 1: Vector Store Usage
```bash
python example_usage.py
```
Demonstrates:
- Creating documents with embeddings
- Team-scoped storage
- Vector similarity search

### Example 2: Complete SDK Workflow
```bash
python example_sdk_usage.py
```
Demonstrates:
- Multi-team ingestion
- Retrieving documents
- Statistics
- Health checks
- Team isolation

---

## Common Tasks

### Task 1: Ingest from JSON File

Create `faqs.json`:
```json
[
  {
    "id": "faq-001",
    "question": "How do I reset my password?",
    "answer": "Click Settings > Security > Change Password",
    "category": "account"
  },
  {
    "id": "faq-002",
    "question": "How do I delete my account?",
    "answer": "Go to Settings > Privacy > Delete Account",
    "category": "account"
  }
]
```

Load it:
```python
from src.sdk.client import RAGClient

client = RAGClient()
stats = client.ingest_faqs_from_file("team-1", "faqs.json")
print(f"Ingested {stats['total_documents']} documents")
```

### Task 2: Multi-Team Setup

```python
from src.sdk.client import RAGClient

client = RAGClient()

# Team 1: Support
support_faqs = [
    {"id": "faq-001", "question": "How to reset?", "answer": "...", "category": "account"},
    ...
]
client.ingest_faqs("team-support", support_faqs)

# Team 2: Sales
sales_faqs = [
    {"id": "faq-001", "question": "What are pricing plans?", "answer": "...", "category": "pricing"},
    ...
]
client.ingest_faqs("team-sales", sales_faqs)

# Teams are isolated
support_results = client.retrieve("reset password", "team-support")    # Support FAQs only
sales_results = client.retrieve("reset password", "team-sales")        # Sales FAQs only (different docs)
```

### Task 3: Advanced Retrieval

```python
from src.sdk.client import RAGClient

client = RAGClient()

# Basic retrieval
results = client.retrieve(
    query="password reset",
    team_id="team-1",
    top_k=5
)

# Multi-pass retrieval with query expansion
results = client.retrieve_expanded(
    query="password problems",
    team_id="team-1",
    top_k=5
)

# Process results
for result in results.results:
    print(f"{result.rank}. {result.content} (score: {result.relevance_score:.1%})")
```

### Task 4: Monitor Team Health

```python
from src.sdk.client import RAGClient

client = RAGClient()

# System health
health = client.health_check()
print(health)

# Team statistics
stats = client.get_stats("team-1")
print(f"Team 1 has {stats['document_count']} documents")

stats = client.get_stats("team-2")
print(f"Team 2 has {stats['document_count']} documents")
```

---

## Troubleshooting

### "No results returned"
```python
# Check if FAQs were ingested
stats = client.get_stats("team-1")
print(f"Documents: {stats['document_count']}")  # Should be > 0

# Try a simpler query
results = client.retrieve("reset password", "team-1")  # Don't use punctuation
```

### "Connection refused" (API server)
```bash
# Make sure server is running
python run_api.py

# Check it's listening
curl http://localhost:8000/api/v1/health
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Verify installation
python -c "import chromadb; import sentence_transformers"
```

### "Out of memory"
- Embedding model uses ~500MB
- ChromaDB grows with data
- Reduce the number of documents being ingested

---

## Next Steps

1. **Read README.md** - Overview and architecture
2. **Read PROJECT_DOCUMENTATION.md** - Deep technical dive
3. **Explore examples** - `example_usage.py`, `example_sdk_usage.py`
4. **Try the API docs** - http://localhost:8000/docs
5. **Integrate into your app** - Use SDK or REST API

---

## Key Concepts

### What is RAG?
Retrieval-Augmented Generation: Finding relevant documents for a query. This framework focuses on the **Retrieval** part (no LLM integration).

### Why Multi-Tenant?
Multiple independent teams can use the same framework without seeing each other's data.

### Why Local Embeddings?
- No API costs (free)
- No external API calls (private)
- Works offline
- Fast (cached model)

### Why ChromaDB?
- Simple (no setup needed)
- Persistent (data survives restarts)
- Fast (optimized for similarity search)
- Team isolation built-in

---

## Architecture at a Glance

```
User Query: "How to reset password?"
    ↓
Normalize: "reset password"
    ↓
Embed: [0.123, 0.456, ...] (384 dimensions)
    ↓
Search ChromaDB: Find similar vectors
    ↓
Results:
  #1: "Click Settings > Security" (92% match)
  #2: "Go to Account settings" (85% match)
    ↓
Return to user/API
```

---

## Support

- **Quick answers:** See README.md
- **Deep knowledge:** See PROJECT_DOCUMENTATION.md
- **API reference:** Visit http://localhost:8000/docs
- **Code examples:** `example_usage.py`, `example_sdk_usage.py`

---

**🎉 You're ready to use RAG Framework!**

Choose your path:
- 🐍 Python: Use `RAGClient` in your code
- 🌐 REST: Call HTTP endpoints
- 📚 Learn: Read the documentation
