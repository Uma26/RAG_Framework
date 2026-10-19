# Practical Training Guide - RAG Framework

## Overview

This guide contains 4 hands-on exercises progressing from basic SDK usage to building real applications on the RAG framework.

**Total Time:** ~45 minutes  
**Level:** Beginner to Intermediate

---

## Quick Start

```bash
# Navigate to framework directory
cd C:\Users\DELL\Documents\uma\code\rag_framework

# Run exercises (no setup needed!)
python exercise_1_basic_sdk.py
python exercise_2_cli_app.py
python exercise_3_rest_api.py
python exercise_4_extend_framework.py
```

---

## EXERCISE 1: Basic SDK Usage (10 min)

**What you'll learn:**
- Create a RAG client
- Ingest FAQ content
- Retrieve relevant answers
- Understand multi-tenancy isolation

**Run:**
```bash
python exercise_1_basic_sdk.py
```

**What happens:**
1. Creates RAG client
2. Ingests 5 FAQ items (~1500 words each)
3. Tests retrieval with 4 different queries
4. Demonstrates query expansion (multi-pass search)
5. Shows team isolation (same questions searched in different teams)

**Output:**
```
[STEP 1] Creating RAG client...
[OK] Client created successfully

[STEP 3] Ingesting content into team 'support-demo'...
[OK] Ingestion successful!
  - Total content items: 5
  - Total chunks created: 5

[STEP 5] Testing retrieval with sample queries...
  Query 1: 'How can I reset my password?'
    Rank 1: ...
    Score: 52.7%
    ...
```

**Key Concepts Demonstrated:**
- SDK usage (direct Python library)
- Vector embeddings (sentence-transformers)
- Semantic search (matching meaning, not just keywords)
- Multi-tenancy (team isolation at storage level)

**Performance Metrics:**
- Ingestion: ~5 FAQs in <1 second
- Retrieval: Each query answers in <50ms
- No HTTP overhead (direct library calls)

---

## EXERCISE 2: Build a CLI App (15 min)

**What you'll learn:**
- Build interactive CLI applications
- Handle user input and output
- Real-time question answering
- Multiple team support

**Run:**
```bash
python exercise_2_cli_app.py
```

**Interactive Demo:**
```
Choose a team:
  1. Support Team (general support FAQs)
  2. Sales Team (sales FAQs)
  3. Exit

Enter choice (1-3): 1

==============================================================
  Support Bot - Team: support-team
==============================================================

You: How do I reset my password?

Bot (found 3 results in 12ms):

  1. To reset your password: 1) Click 'Forgot Password' on login...
     Confidence: [=================== ] 85%
     Type: faq, Category: authentication
```

**Features to Try:**
- Ask different support questions
- Type "stats" to see team statistics
- Type "clear" to clear screen
- Type "quit" to exit

**Real-World Applications:**
- Customer support chatbots
- Internal knowledge bases
- Help desk automation
- FAQ systems

**Performance:**
- Real-time answers (<50ms)
- Handles follow-up questions
- Scales to thousands of FAQs

---

## EXERCISE 3: REST API Testing (12 min)

**What you'll learn:**
- Test FastAPI REST endpoints
- Make HTTP requests programmatically
- Handle JSON payloads
- Understand API error handling

**Setup (Two Terminal Windows):**

**Terminal 1 - Start the API Server:**
```bash
cd C:\Users\DELL\Documents\uma\code\rag_framework
python run_api.py
```

Output:
```
INFO:     Started server process [1234]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Run Tests:**
```bash
cd C:\Users\DELL\Documents\uma\code\rag_framework
python exercise_3_rest_api.py
```

**What Gets Tested:**
1. `GET /health` - Health check endpoint
2. `POST /ingest` - Ingest documentation
3. `POST /retrieve` - Search for answers
4. `GET /stats/{team_id}` - Team statistics
5. Multi-team isolation via API

**Example HTTP Requests:**

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Ingest content
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "my-team",
    "content": [
      {
        "id": "doc-1",
        "title": "Question",
        "body": "Answer here",
        "content_type": "faq",
        "category": "general"
      }
    ]
  }'

# Retrieve answers
curl -X POST http://localhost:8000/api/v1/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I...?",
    "team_id": "my-team",
    "top_k": 5
  }'
```

**Real-World Applications:**
- Frontend chatbots (JavaScript clients)
- Mobile apps (iOS/Android)
- Third-party integrations
- Microservices architecture

**Performance:**
- API response time: 50-100ms (includes network latency)
- Handles multiple concurrent requests
- Scales with load balancing

---

## EXERCISE 4: Extend the Framework (10 min)

**What you'll learn:**
- Add custom content types
- Work with mixed content
- Benchmark performance
- Use advanced retrieval techniques

**Run:**
```bash
python exercise_4_extend_framework.py
```

**Four Demos Included:**

### Demo 1: CODE Content Type
Ingest and search code examples (Python, JavaScript, SQL)

```
Query: 'How do I authenticate in Python?'
Found: Basic Authentication code snippet
Score: 29.4%
```

### Demo 2: Metadata Filtering
Mix FAQs, documentation, and code - search all at once

```
Ingesting mixed content...
Searching for 'billing':
  - Documentation (score: 15.8%)
  - FAQ (score: 72.0%)
  - Related content (score: 18.3%)
```

### Demo 3: Performance Benchmark
Measure ingestion and retrieval speed

```
Ingest: 68.6 docs/sec (14.6ms per doc)
Query:  78.5 queries/sec (12.7ms per query)
```

### Demo 4: Advanced Retrieval
Compare standard retrieval vs. query expansion

```
[1] Standard retrieval: 2 results
[2] Expanded retrieval: 2 results (may be more comprehensive)
```

---

## Framework Architecture (Quick Reference)

```
┌─────────────────────────────────────────┐
│         Your Application Code           │
│  (CLI app, REST API, Chatbot, etc.)     │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  API/SDK Layer (RAGClient, FastAPI)     │
│  - Ingestion endpoints                  │
│  - Retrieval endpoints                  │
│  - Health checks                        │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  Services Layer (5 core services)       │
│  1. ContentIngestionService             │
│  2. EmbeddingService                    │
│  3. ChromaDBVectorStore                 │
│  4. QueryProcessorService               │
│  5. RAGOrchestratorService              │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  Domain Layer (Data Models)             │
│  - Content, Chunk                       │
│  - ContentType enum                     │
│  - SearchResult, RetrievalResult        │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  External Systems                       │
│  - ChromaDB (vector storage)            │
│  - sentence-transformers (embeddings)   │
└─────────────────────────────────────────┘
```

---

## Key Features Demonstrated

### 1. Multi-Tenancy Isolation
Each team has separate data:
```python
client.retrieve("query", team_id="team-1")  # Only team-1 results
client.retrieve("query", team_id="team-2")  # Only team-2 results
```

### 2. Content Type Flexibility
Same framework handles any content:
```python
ContentType.FAQ
ContentType.DOCUMENTATION
ContentType.CODE
ContentType.RESEARCH
ContentType.TRANSCRIPT
# ... and more
```

### 3. Semantic Search
Understands meaning, not just keywords:
```
Query: "How do I reset my password?"
Result: "To change your password, click Forgot Password..."
(Same meaning, different wording)
```

### 4. Fast Retrieval
Millisecond-level query response:
```
Query time: 12-14ms (even with thousands of documents)
Ingestion: 68 docs/sec throughput
```

### 5. Easy Integration
Single client for all operations:
```python
from src.sdk.client import RAGClient

client = RAGClient()
client.ingest_content(team_id, content)
results = client.retrieve(query, team_id)
```

---

## Customization Ideas

### 1. Add Custom Metadata
```python
content = {
    "id": "doc-001",
    "title": "...",
    "body": "...",
    "content_type": "documentation",
    "category": "api",
    "custom_field": "value",  # Your custom metadata
    "metadata": {"version": "2.0"}  # Flexible metadata
}
```

### 2. Custom Content Types
Edit `src/domain/models.py`:
```python
class ContentType(str, Enum):
    FAQ = "faq"
    VIDEO = "video"  # Add new type
    PODCAST = "podcast"
```

### 3. Implement Custom Retrieval
```python
# Override RAGOrchestrator.retrieve() for custom ranking
def retrieve(self, query_text, team_id, top_k):
    results = super().retrieve(query_text, team_id, top_k)
    # Your custom re-ranking logic here
    return results
```

### 4. Add Caching
```python
# Cache frequently asked questions
from functools import lru_cache

@lru_cache(maxsize=1000)
def retrieve_cached(query, team_id):
    return client.retrieve(query, team_id)
```

---

## Performance Tips

### 1. Batch Ingestion
```python
# Good: Batch ingest
client.ingest_content(team_id, [item1, item2, ..., item100])

# Slower: One at a time
for item in items:
    client.ingest_single(team_id, item)
```

### 2. Tune top_k
```python
# Balance between quality and speed
client.retrieve(query, team_id, top_k=3)  # Fast, decent
client.retrieve(query, team_id, top_k=10)  # Slower, more results
```

### 3. Query Expansion Selectively
```python
# Standard (fast)
client.retrieve(query, team_id)

# Expanded (thorough but slower)
client.retrieve_expanded(query, team_id)
```

### 4. Monitor Team Size
```python
stats = client.get_stats(team_id)
if stats['document_count'] > 10000:
    # Consider archiving old data
```

---

## Troubleshooting

### Issue: "Cannot connect to ChromaDB"
**Solution:** Ensure ChromaDB initialization is working
```bash
python -c "import chromadb; print('OK')"
```

### Issue: "API server not responding"
**Solution:** Start the API server first
```bash
python run_api.py
```

### Issue: "Low relevance scores"
**Solution:** Try query expansion or improve content keywords
```python
# Standard query
results = client.retrieve(query, team_id)

# Expanded query (finds more variations)
results = client.retrieve_expanded(query, team_id)
```

### Issue: "Performance degradation"
**Solution:** Check team size and consider splitting
```python
stats = client.get_stats(team_id)
print(f"Documents in team: {stats['document_count']}")
```

---

## Next Steps

### 1. Production Deployment
- Containerize with Docker
- Deploy to AWS/GCP/Azure
- Scale services independently
- Add monitoring & logging

### 2. Advanced Features
- Re-ranking with LLM
- Hybrid search (vector + keyword)
- Query intent classification
- Answer generation

### 3. Integration
- Build web frontend
- Mobile app support
- Slack bot integration
- Teams bot integration

### 4. Custom Applications
- Industry-specific FAQs
- Documentation search
- Code search engine
- Knowledge base

---

## Exercise Summary

| Exercise | Duration | Topic | Files |
|----------|----------|-------|-------|
| 1 | 10 min | Basic SDK | exercise_1_basic_sdk.py |
| 2 | 15 min | CLI App | exercise_2_cli_app.py |
| 3 | 12 min | REST API | exercise_3_rest_api.py |
| 4 | 10 min | Extensions | exercise_4_extend_framework.py |

**Total Time: ~45 minutes**

---

## Learning Outcomes

After completing these exercises, you can:

✓ Use the RAG SDK in Python applications  
✓ Build interactive CLI tools  
✓ Test REST APIs programmatically  
✓ Ingest different content types  
✓ Retrieve answers with semantic search  
✓ Handle multi-tenant scenarios  
✓ Benchmark performance  
✓ Extend the framework with custom features  

---

## Resources

- **Framework Documentation:** `MODULE_ARCHITECTURE.md`
- **API Documentation:** `QUICKSTART.md`
- **Configuration:** `src/config/settings.py`
- **Source Code:** `src/` directory

---

**Ready to build? Start with Exercise 1!** 🚀
