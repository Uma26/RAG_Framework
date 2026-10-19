# RAG Framework - Module-by-Module Architecture Guide
## Deep Dive into Each Folder, Design Patterns, and Responsibilities

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Module 1: Config (`src/config/`)](#module-1-config)
3. [Module 2: Domain (`src/domain/`)](#module-2-domain)
4. [Module 3: Services (`src/services/`)](#module-3-services)
5. [Module 4: API (`src/api/`)](#module-4-api)
6. [Module 5: SDK (`src/sdk/`)](#module-5-sdk)
7. [Module Interactions](#module-interactions)
8. [Design Patterns Summary](#design-patterns-summary)

---

# OVERVIEW

## Project Module Structure

```
rag_framework/
│
├── src/
│   ├── config/              ← Module 1: Configuration Layer
│   │   ├── settings.py
│   │   └── __init__.py
│   │
│   ├── domain/              ← Module 2: Domain Model Layer
│   │   ├── models.py
│   │   ├── exceptions.py
│   │   └── __init__.py
│   │
│   ├── services/            ← Module 3: Service/Business Logic Layer
│   │   ├── embedding_service.py
│   │   ├── chroma_vector_store.py
│   │   ├── ingestion_service.py
│   │   ├── query_processor.py
│   │   ├── rag_orchestrator.py
│   │   └── __init__.py
│   │
│   ├── api/                 ← Module 4: API/Presentation Layer
│   │   ├── routes.py
│   │   ├── app.py
│   │   └── __init__.py
│   │
│   ├── sdk/                 ← Module 5: SDK/Client Layer
│   │   ├── client.py
│   │   └── __init__.py
│   │
│   └── __init__.py          ← Main package
│
└── (configuration & examples at root level)
```

## Architectural Pattern: Layered Architecture

```
┌─────────────────────────────────────┐
│  Presentation Layer                 │ ← API Routes & SDK Client
├─────────────────────────────────────┤
│  Application/Business Logic Layer   │ ← Orchestrator
├─────────────────────────────────────┤
│  Service Layer                      │ ← 5 Services
├─────────────────────────────────────┤
│  Domain Model Layer                 │ ← Data Models & Exceptions
├─────────────────────────────────────┤
│  Configuration Layer                │ ← Settings Management
└─────────────────────────────────────┘

Dependencies flow DOWNWARD only:
  API → Orchestrator → Services → Domain → Config
  SDK → Orchestrator → Services → Domain → Config

No upward dependencies (Config doesn't depend on Services, etc.)
```

---

# MODULE 1: CONFIG (`src/config/`)

## Module Purpose

**"Single Source of Truth for Configuration"**

The Config module manages ALL application settings in one place. Instead of hardcoding values or reading from multiple places, all configuration comes through this module.

## Why This Module Exists

### Problems It Solves

```
❌ WITHOUT Config Module:
  - Settings scattered everywhere
  - Hardcoded values in code
  - Difficult to change behavior
  - No validation of config values
  - Environment setup is confusing

✓ WITH Config Module:
  - All settings in one place
  - Type-safe (validated by Pydantic)
  - Environment variable support
  - Easy to change without code modification
  - Clear defaults and documentation
```

## Files in This Module

### 1. `settings.py` (55 lines)

**Purpose:** Define and load all configuration

**Design Pattern Used: SINGLETON**

```python
# Why Singleton?
# - Only one settings instance needed
# - Shared across entire application
# - Guaranteed consistent configuration
# - No duplicated state

# Implementation:
class RAGSettings(BaseSettings):
    """Central configuration class"""
    # All settings as class attributes
    pass

# Global singleton instance
settings = RAGSettings()  # Created once, reused everywhere
```

**What It Contains:**

```python
class RAGSettings(BaseSettings):
    
    # 1. EMBEDDING SETTINGS
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_dimension: int = 384
    
    # 2. VECTOR STORE SETTINGS
    vector_store_type: str = "chromadb"
    chroma_persist_dir: str = "./chroma_data"
    
    # 3. RAG FEATURE FLAGS
    enable_query_expansion: bool = True
    enable_reranking: bool = True
    enable_hybrid_search: bool = True
    
    # 4. RETRIEVAL SETTINGS
    default_top_k: int = 5
    max_query_length: int = 500
    
    # 5. LOGGING SETTINGS
    log_level: str = "INFO"
    
    class Config:
        # Load from: env vars → .env file → defaults
        env_file = ".env"
        case_sensitive = False
```

**How It Works:**

```
Configuration Priority (Top wins):
1. Environment Variables  → os.environ.get('EMBEDDING_MODEL')
2. .env File             → EMBEDDING_MODEL=...
3. Default Values        → embedding_model: str = "..."

Example:
┌─────────────────┐
│ Environment     │  No match
│ EMBEDDING_MODEL │  
└─────────────────┘
         ↓
┌─────────────────┐
│ .env File       │  EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
└─────────────────┘
         ↓
✓ USE THIS VALUE
```

**Why Pydantic BaseSettings?**

```
Problem without Pydantic:
  config = {
      'embedding_model': os.environ.get('EMBEDDING_MODEL'),
      'vector_dimension': int(os.environ.get('VECTOR_DIMENSION', '384')),
      'enable_query_expansion': os.environ.get('ENABLE_QUERY_EXPANSION', 'true').lower() == 'true'
  }
  # Manual type conversion, error-prone

Solution with Pydantic BaseSettings:
  class RAGSettings(BaseSettings):
      embedding_model: str
      vector_dimension: int
      enable_query_expansion: bool
  
  # Automatic type conversion and validation!
  settings = RAGSettings()  # All config loaded and validated
```

### 2. `__init__.py` (8 lines)

**Purpose:** Export singleton for easy import

**Design Pattern Used: FACADE**

```python
# Instead of:
from src.config.settings import RAGSettings
settings = RAGSettings()

# Users write:
from src.config import settings
# Much cleaner!
```

## Design Patterns in Config Module

### 1. **Singleton Pattern**
```
Purpose: Ensure only one instance of settings exists
Benefit: No duplicated state, consistent configuration
Implementation: Global instance created once at module load

settings = RAGSettings()  # Created once
# Used everywhere:
from src.config import settings
print(settings.embedding_model)
print(settings.vector_dimension)
```

### 2. **Strategy Pattern (via Feature Flags)**
```python
# Different retrieval strategies can be enabled/disabled
if settings.enable_query_expansion:
    results = orchestrator.retrieve_with_expansion(...)
else:
    results = orchestrator.retrieve(...)

if settings.enable_reranking:
    results = rerank_results(results)
```

### 3. **Builder Pattern (via BaseSettings)**
```
Pydantic builds configuration object from multiple sources:
- Environment variables
- .env file
- Default values

Builds complete, validated settings object in one place
```

## How Config Module Is Used

```
Every other module imports from config:

src/services/embedding_service.py:
  from src.config import settings
  model_name = settings.embedding_model
  vector_dim = settings.vector_dimension

src/services/chroma_vector_store.py:
  from src.config import settings
  persist_dir = settings.chroma_persist_dir

src/api/routes.py:
  from src.config import settings
  top_k = settings.default_top_k
```

## Configuration Files

### `.env.example` (Template)
```env
# Show users what settings are available
# Users copy to .env and fill in values

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DIMENSION=384
CHROMA_PERSIST_DIR=./chroma_data
ENABLE_QUERY_EXPANSION=true
LOG_LEVEL=INFO
```

### `.env` (Actual, never committed)
```env
# User's actual configuration
# This file is in .gitignore
# Each environment has different .env

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PERSIST_DIR=/production/chroma_data
LOG_LEVEL=WARNING
```

---

# MODULE 2: DOMAIN (`src/domain/`)

## Module Purpose

**"Define Data Structures and Business Rules"**

The Domain module defines WHAT data the system works with and WHAT exceptions can occur. It's pure data and rules, no implementation logic.

## Why This Module Exists

### Problems It Solves

```
❌ WITHOUT Domain Module:
  - Data structures scattered everywhere
  - No validation of data
  - Unclear what exceptions can happen
  - No single source of truth for data schema
  - Type errors at runtime (missed by IDE)

✓ WITH Domain Module:
  - All data models in one place
  - Type-safe (IDE catches errors)
  - Automatic validation (Pydantic)
  - Clear schema documentation
  - Exceptions are well-defined
```

## Files in This Module

### 1. `models.py` (200 lines)

**Purpose:** Define all data structures

**Design Pattern Used: VALUE OBJECT**

```python
# Value Objects: Objects that represent values, not entities
# Immutable, defined by their content

class FAQ(BaseModel):  # Value Object
    """Represents an FAQ, defined by its content"""
    id: str
    question: str
    answer: str
    category: str
    keywords: List[str]
    
    # Two FAQs with same content = equal (value semantics)
    # faq1 = FAQ(id="1", question="Reset?", ...)
    # faq2 = FAQ(id="1", question="Reset?", ...)
    # faq1 == faq2  (True - same content)
```

**All Models Defined:**

```python
1. QueryType (Enum)
   ├─ GENERAL
   ├─ HOW_TO
   ├─ TROUBLESHOOTING
   └─ SEARCH

2. FAQ (Model)
   ├─ id: str
   ├─ question: str
   ├─ answer: str
   ├─ category: str
   ├─ keywords: List[str]
   ├─ entities: List[str]
   └─ timestamps & metadata

3. Document (Model)
   ├─ id: str
   ├─ content: str
   ├─ faq_id: str (reference to FAQ)
   ├─ chunk_index: int
   ├─ embedding: List[float]
   ├─ category: str
   ├─ keywords: List[str]
   └─ entities: List[str]

4. SearchResult (Model)
   ├─ rank: int
   ├─ relevance_score: float
   ├─ content: str
   ├─ category: str
   ├─ source: str (which retrieval method)
   ├─ vector_score: float
   └─ ranking_explanation: str

5. SearchQuery (Model)
   ├─ text: str
   ├─ query_type: QueryType
   ├─ top_k: int
   ├─ team_id: str
   └─ timestamp: datetime

6. RetrievalResult (Model)
   ├─ query: str
   ├─ results: List[SearchResult]
   ├─ execution_time_ms: float
   ├─ retrieval_method: str
   └─ confidence_score: float
```

**Why Use Pydantic Models?**

```python
# WITHOUT Pydantic:
def process_faq(faq_dict):
    id = faq_dict.get('id')
    question = faq_dict.get('question')
    keywords = faq_dict.get('keywords', [])
    # What if 'question' is missing? Returns None
    # What if 'keywords' is a string instead of list? Crashes later
    # No validation!

# WITH Pydantic:
class FAQ(BaseModel):
    id: str
    question: str  # Required, must be str
    keywords: List[str]  # Required, must be list of strings

# Automatic validation:
faq = FAQ(id="1", question="Reset?", keywords=["password"])  # ✓ OK
faq = FAQ(id="1", question="Reset?")  # ✗ ValidationError - keywords missing
faq = FAQ(id="1", question="Reset?", keywords="password")  # ✗ ValidationError - not list
```

### 2. `exceptions.py` (40 lines)

**Purpose:** Define custom exceptions

**Design Pattern Used: CUSTOM EXCEPTION HIERARCHY**

```python
# Exception Hierarchy:
# Allows catching errors at different levels

RAGException (base)
├── EmbeddingError           ← Embedding service problems
├── VectorStoreError         ← ChromaDB problems
├── QueryProcessingError     ← Query processing problems
├── GraphStoreError          ← Future: graph database problems
├── ConfigurationError       ← Settings problems
├── AuthenticationError      ← Auth problems (future)
└── AuthorizationError       ← Permission problems (future)
```

**Why Custom Exceptions?**

```python
# Catch specific errors:
try:
    vector = embedding_service.embed_text("query")
except EmbeddingError as e:
    logger.error(f"Embedding failed: {e}")
    # Handle embedding-specific error
except VectorStoreError as e:
    logger.error(f"Vector store failed: {e}")
    # Handle vector store-specific error

# Clear intent - different errors, different handling
```

### 3. `__init__.py` (20 lines)

**Purpose:** Export all models and exceptions

**Design Pattern Used: FACADE**

```python
# Users write:
from src.domain import FAQ, Document, SearchResult, EmbeddingError

# Instead of:
from src.domain.models import FAQ, Document, SearchResult
from src.domain.exceptions import EmbeddingError
```

## Design Patterns in Domain Module

### 1. **Value Object Pattern**
```
Models represent values (data), not entities (objects with identity)

FAQ is a value object:
- Two FAQs with same data = equivalent
- Immutable (Pydantic validates and freezes)
- No methods to "do things", just data structure

vs. Entity (has identity):
class User:  # Entity (identity matters)
    id: str
    name: str
    # Two users with same data but different IDs = different users
```

### 2. **Data Validation Pattern**
```
Pydantic provides declarative validation:

class SearchResult(BaseModel):
    rank: int = Field(..., ge=1)  # Must be >= 1
    relevance_score: float = Field(..., ge=0.0, le=1.0)  # Between 0 and 1
    top_k: int = Field(5, ge=1, le=50)  # Between 1 and 50

Errors caught at model creation, not later
```

### 3. **Exception Hierarchy Pattern**
```
Custom exceptions organized by layer:

try:
    embedding_service.embed_text(text)  # Could raise EmbeddingError
    vector_store.search(...)             # Could raise VectorStoreError
except EmbeddingError:
    pass  # Handle embedding error
except RAGException:
    pass  # Catch-all for any RAG error
```

## How Domain Module Is Used

```
Every other module imports from domain:

src/services/embedding_service.py:
  from src.domain.exceptions import EmbeddingError
  raise EmbeddingError("Model load failed")

src/services/chroma_vector_store.py:
  from src.domain.models import Document
  from src.domain.exceptions import VectorStoreError
  
  def add_documents(self, documents: List[Document]) -> int:
      # Type hint shows we expect Document objects
      # IDE autocomplete helps

src/api/routes.py:
  from src.domain.models import SearchResult, RetrievalResult
  
  @app.post('/retrieve')
  async def retrieve(...) -> RetrievalResult:
      # Return type is documented and validated
```

---

# MODULE 3: SERVICES (`src/services/`)

## Module Purpose

**"Implement Business Logic and Core Operations"**

The Services module contains all the actual work - processing queries, embedding text, storing vectors, orchestrating retrieval. Each service has one clear responsibility.

## Why This Module Exists

### Problems It Solves

```
❌ WITHOUT Services Module:
  - Logic scattered everywhere
  - Hard to test
  - Hard to reuse
  - Dependencies tangled
  - No clear responsibilities

✓ WITH Services Module:
  - Each service has one job
  - Easy to test
  - Easy to reuse
  - Clear dependencies
  - Easy to understand
```

## Architectural Pattern in Services: SINGLE RESPONSIBILITY PRINCIPLE

```
Each service = one clear responsibility

┌─ EmbeddingService
│  └─ ONLY: Convert text to vectors
│
├─ ChromaDBVectorStore
│  └─ ONLY: Store and search vectors
│
├─ DocumentIngestionService
│  └─ ONLY: Load FAQs and prepare for storage
│
├─ QueryProcessor
│  └─ ONLY: Process user queries
│
└─ RAGOrchestrator
   └─ ONLY: Coordinate all services
```

## Files in This Module

### 1. `embedding_service.py` (188 lines)

**Responsibility:** Convert text to vector embeddings

**Design Pattern Used: ADAPTER**

```
Why Adapter?
- sentence-transformers is external library
- We create a wrapper (adapter) around it
- Our code depends on EmbeddingService, not sentence-transformers
- Easy to swap implementation later

+─────────────────────────────┐
│ Our Application Code        │
├─────────────────────────────┤
│ EmbeddingService (Adapter)  │ ← Adapter pattern
├─────────────────────────────┤
│ sentence-transformers lib   │ ← External dependency
└─────────────────────────────┘
```

**What It Does:**

```python
class EmbeddingService:
    
    def __init__(self):
        # Load model once on startup (expensive operation)
        self._model = SentenceTransformer(model_name)
    
    def embed_text(text: str) -> List[float]:
        # Single text: Simple interface
        # Returns: 384-dimensional normalized vector
    
    def embed_texts(texts: List[str]) -> List[List[float]]:
        # Batch: Efficient processing
        # Uses batch_size=32 for optimal performance
    
    def health_check() -> bool:
        # Can we still embed?
        # Used for monitoring
```

**Design Pattern Details:**

```python
# ADAPTER Pattern Implementation:

# External library interface:
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(...)
vectors = model.encode(texts)  # Returns numpy arrays

# Our adapter interface:
class EmbeddingService:
    def embed_text(text: str) -> List[float]:
        # Convert external interface to our interface
        vectors = self._model.encode(text, normalize_embeddings=True)
        return vectors.tolist()  # Convert numpy → list

# Application code depends on OUR interface:
from src.services import embedding_service
vectors = embedding_service.embed_text(text)  # Not sentence-transformers
```

**Singleton Usage:**

```python
# Global singleton instance
embedding_service = EmbeddingService()

# Used everywhere:
from src.services import embedding_service
embedding_service.embed_text(text)

# Why singleton?
# - Model is expensive to load (~500MB)
# - Want to load once, reuse everywhere
# - Guaranteed same model instance
```

### 2. `chroma_vector_store.py` (370 lines)

**Responsibility:** Store and search vectors with team isolation

**Design Pattern Used: REPOSITORY**

```
Repository Pattern: Abstracts data storage

+──────────────────────┐
│ Application Code     │
├──────────────────────┤
│ ChromaDBVectorStore  │ ← Repository
│ (abstraction)        │
├──────────────────────┤
│ ChromaDB             │ ← Actual storage
└──────────────────────┘

Benefits:
- Application code doesn't know it's using ChromaDB
- Could swap for PostgreSQL, Elasticsearch, etc.
- Testing: can mock repository
```

**What It Does:**

```python
class ChromaDBVectorStore:
    
    def add_documents(team_id: str, documents: List[Document]) -> int:
        # Store vectors in team-scoped collection
        # Returns: number of documents stored
    
    def search(team_id: str, query_vector: List[float], top_k: int) -> List[Tuple]:
        # Find similar vectors for this team ONLY
        # Returns: [(doc_id, similarity_score, metadata), ...]
    
    def delete_document(team_id: str, doc_id: str) -> bool:
        # Remove document from team's collection
        # GDPR compliance
    
    def get_stats(team_id: str) -> Dict:
        # Get collection statistics
        # Monitoring and debugging
    
    def health_check() -> bool:
        # Can we access ChromaDB?
        # Used for monitoring
```

**Team Isolation Design:**

```python
# Key design: Per-team collections

def _get_collection_name(self, team_id: str) -> str:
    # Convert team_id to collection name
    # "team-1" → "team_1_documents"
    return f"{team_id.replace('-', '_')}_documents"

# Result:
ChromaDB Instance
├─ team_1_documents (Team 1's vectors only)
├─ team_2_documents (Team 2's vectors only)
└─ team_3_documents (Team 3's vectors only)

# Search always specifies team_id:
def search(self, team_id: str, query_vector, top_k):
    collection = self._get_or_create_collection(team_id)
    results = collection.query(...)  # Only searches this team's collection
    # Guaranteed isolation!
```

**Design Pattern Details:**

```python
# REPOSITORY Pattern Implementation:

# Application code:
from src.services import vector_store
vector_store.add_documents("team-1", docs)
results = vector_store.search("team-1", query_vec)

# Application doesn't know about ChromaDB
# Repository handles storage details

# Benefits:
# 1. Swap storage without changing application
# 2. Easy to test (mock repository)
# 3. Clear interface between storage and application
```

### 3. `ingestion_service.py` (330 lines)

**Responsibility:** Load FAQs and prepare for storage

**Design Pattern Used: STRATEGY**

```
Strategy Pattern: Different ways to ingest data

IngestionService
├─ Strategy 1: ingest_faqs_from_json()
├─ Strategy 2: ingest_faqs_from_file()
└─ Strategy 3: ingest_faq_dict()

All achieve same goal (store FAQs) but via different input sources
```

**What It Does:**

```python
class DocumentIngestionService:
    
    def ingest_faqs_from_json(team_id: str, json_data: List[Dict]):
        # Strategy 1: JSON array input
        # Process each FAQ in array
    
    def ingest_faqs_from_file(team_id: str, file_path: str):
        # Strategy 2: File input
        # Load file, then use Strategy 1
    
    def ingest_faq_dict(team_id: str, faq_dict: Dict):
        # Strategy 3: Single FAQ input
        # Wrap in list, then use Strategy 1
    
    # Helper methods:
    def _chunk_text(text: str) -> List[str]:
        # Split long answers into 500-char chunks
    
    def _extract_keywords(question, answer) -> List[str]:
        # Auto-extract keywords
    
    def _extract_entities(question, answer) -> List[str]:
        # Auto-extract named entities
```

**Processing Pipeline:**

```
FAQ Input
    ↓
[Validate Fields]
    ↓
[Chunk Text]
    ↓
[Extract Metadata]
    ├─ Keywords
    └─ Entities
    ↓
[Embed Each Chunk]
    ↓
[Create Document Objects]
    ↓
[Store in ChromaDB]
    ↓
Return Stats
```

**Design Pattern Details:**

```python
# STRATEGY Pattern Implementation:

# Different input strategies:
def ingest_faqs_from_json(self, team_id, json_data):
    # Strategy 1
    for faq in json_data:
        doc = self._create_documents_from_faq(faq)
        vector_store.add_documents(team_id, doc)

def ingest_faqs_from_file(self, team_id, file_path):
    # Strategy 2: uses Strategy 1 internally
    json_data = load_json_file(file_path)
    return self.ingest_faqs_from_json(team_id, json_data)

def ingest_faq_dict(self, team_id, faq_dict):
    # Strategy 3: uses Strategy 1 internally
    return self.ingest_faqs_from_json(team_id, [faq_dict])

# Application chooses strategy based on input source
# All achieve same result
```

### 4. `query_processor.py` (300 lines)

**Responsibility:** Process and prepare user queries

**Design Pattern Used: CHAIN OF RESPONSIBILITY**

```
Chain of Responsibility: Pass through series of processors

User Query
    ↓
[Normalize] ← Step 1: Cleanup
    ↓
[Validate] ← Step 2: Validation
    ↓
[Classify] ← Step 3: Determine type
    ↓
[Expand] ← Step 4: Add variations
    ↓
Processed Query
```

**What It Does:**

```python
class QueryProcessor:
    
    def process_query(text: str, team_id: str, top_k: int) -> SearchQuery:
        # Main method: execute chain
        
        1. _validate_query(text)
           # Check: not empty, not too long, no injection
        
        2. _normalize_text(text)
           # Lowercase, remove punctuation
        
        3. _classify_query_type(text)
           # Detect: HOW_TO, TROUBLESHOOTING, SEARCH, GENERAL
        
        4. _expand_query(text)
           # Add synonyms: "password" → "passwd", "credentials"
        
        5. _extract_key_terms(text)
           # Remove stop words, keep meaningful terms
        
        return SearchQuery(...)  # Final processed query
    
    def get_query_variations(text: str) -> List[str]:
        # Get all variations for multi-pass search
```

**Design Pattern Details:**

```python
# CHAIN OF RESPONSIBILITY Pattern:

def process_query(self, text, team_id, top_k):
    # Each step in chain calls next step
    
    is_valid, error = self._validate_query(text)
    if not is_valid:
        raise QueryProcessingError(error)
    # Step 1 complete, pass to step 2
    
    normalized = self._normalize_text(text)
    # Step 2 complete, pass to step 3
    
    query_type = self._classify_query_type(normalized)
    # Step 3 complete, pass to step 4
    
    expanded = self._expand_query(normalized)
    # Step 4 complete, pass to step 5
    
    key_terms = self._extract_key_terms(normalized)
    # Step 5 complete, create result
    
    return SearchQuery(text=normalized, query_type=query_type, ...)

# Each handler (step) is independent
# Easy to add/remove steps
# Easy to test each step separately
```

### 5. `rag_orchestrator.py` (330 lines)

**Responsibility:** Coordinate all services to implement retrieval

**Design Pattern Used: ORCHESTRATOR/FACADE**

```
Orchestrator Pattern: Coordinates multiple services

+─────────────────────────────────┐
│ RAG Orchestrator                │ ← Facade
├─────────────────────────────────┤
│ Coordinates:                    │
├─ Query Processor               │
├─ Embedding Service             │
├─ Vector Store                  │
└─ Scoring Logic                 │
```

**What It Does:**

```python
class RAGOrchestrator:
    
    def retrieve(query: str, team_id: str, top_k: int) -> RetrievalResult:
        # Main retrieval method
        # Orchestrates the pipeline:
        
        1. query_processor.process_query(query)
           # Step 1: Process
        
        2. embedding_service.embed_text(processed_query)
           # Step 2: Embed
        
        3. vector_store.search(team_id, query_vector, top_k)
           # Step 3: Search
        
        4. _score_document(...) for each result
           # Step 4: Score
        
        5. Return RetrievalResult(...)
           # Step 5: Package
    
    def retrieve_with_expansion(...) -> RetrievalResult:
        # Multi-pass retrieval
        # Try multiple query variations
        # Combine results
    
    def health_check() -> Dict:
        # Check all services healthy
```

**Orchestration Flow:**

```python
def retrieve(self, query_text, team_id, top_k):
    start_time = time.time()
    
    # Step 1: Process query
    search_query = query_processor.process_query(query_text, team_id, top_k)
    # Returns: SearchQuery with normalized text, type, expanded versions
    
    # Step 2: Embed query
    query_vector = embedding_service.embed_text(search_query.text)
    # Returns: [0.123, 0.456, ..., 0.999]  (384 dimensions)
    
    # Step 3: Search vectors
    search_results = vector_store.search(team_id, query_vector, top_k)
    # Returns: [(doc_id, similarity, metadata), ...]
    
    # Step 4: Score and rank
    results = []
    for rank, (doc_id, score, metadata) in enumerate(search_results, 1):
        scored = self._score_document(doc_id, score, metadata, search_query.text)
        result = SearchResult(rank=rank, relevance_score=scored, ...)
        results.append(result)
    
    # Step 5: Package and return
    execution_time = time.time() - start_time
    return RetrievalResult(
        query=search_query.text,
        results=results,
        execution_time_ms=execution_time * 1000,
        confidence_score=results[0].relevance_score if results else 0.0
    )
```

**Design Pattern Details:**

```python
# ORCHESTRATOR Pattern Implementation:

class RAGOrchestrator:
    # Single class coordinates all services
    # Application only calls orchestrator
    
    def retrieve(self, query, team_id, top_k):
        # Inside: coordinates 4-5 other services
        # Outside: looks like single operation
    
    # Benefits:
    # 1. Complex orchestration hidden from application
    # 2. Easy to change workflow (all in one place)
    # 3. Application code is simple
    # 4. Services are independent and reusable
```

### 6. `__init__.py` (15 lines)

**Purpose:** Export all service singletons

**Design Pattern Used: FACADE**

```python
from .embedding_service import embedding_service
from .chroma_vector_store import vector_store
from .ingestion_service import ingestion_service
from .query_processor import query_processor
from .rag_orchestrator import rag_orchestrator

# Users write:
from src.services import embedding_service, vector_store

# Instead of:
from src.services.embedding_service import embedding_service
from src.services.chroma_vector_store import vector_store
```

## Design Patterns in Services Module

### 1. **Singleton Pattern (All Services)**
```
Each service = single global instance

embedding_service = EmbeddingService()  # Created once
vector_store = ChromaDBVectorStore()    # Created once
ingestion_service = DocumentIngestionService()  # Created once

Benefits:
- Expensive resources (embedding model) loaded once
- Shared state guaranteed
- No duplicate instances
```

### 2. **Adapter Pattern (EmbeddingService)**
```
Wraps external sentence-transformers library
Provides our own interface
Easy to swap implementations
```

### 3. **Repository Pattern (Vector Store)**
```
Abstracts data storage
Application code independent of storage technology
Easy to test (can mock)
```

### 4. **Strategy Pattern (Ingestion Service)**
```
Different input strategies (file, JSON, dict)
Same outcome (store FAQs)
Easy to add new strategies
```

### 5. **Chain of Responsibility (Query Processor)**
```
Series of processing steps
Each step independent
Easy to modify pipeline
```

### 6. **Orchestrator/Facade Pattern (RAG Orchestrator)**
```
Coordinates multiple services
Hides complexity from caller
Single entry point for retrieval
```

---

# MODULE 4: API (`src/api/`)

## Module Purpose

**"Expose Services via HTTP REST API"**

The API module lets external applications (websites, mobile apps, other services) use the framework via HTTP requests.

## Why This Module Exists

### Problems It Solves

```
❌ WITHOUT API Module:
  - Only Python applications can use framework
  - Hard to integrate with other technologies
  - No standard HTTP interface
  - No documentation
  - Hard to scale (no web server)

✓ WITH API Module:
  - Any technology can use via HTTP
  - REST standard (well-known)
  - Auto-generated documentation (Swagger)
  - Scalable (FastAPI + Uvicorn)
  - Type-safe (Pydantic validation)
```

## Files in This Module

### 1. `routes.py` (300 lines)

**Responsibility:** Define REST endpoints

**Design Pattern Used: REQUEST-RESPONSE**

```
REST API follows Request-Response pattern

Client                          Server
  │                              │
  ├─ HTTP Request ───────────→   │
  │                              ├─ Parse request
  │                              ├─ Validate data
  │                              ├─ Call business logic
  │                              └─ Format response
  │    ← HTTP Response ──────────┤
  └─ Parse response              │
```

**What It Contains:**

```python
# Request Models (Pydantic - auto-validated)
class RetrieveRequest(BaseModel):
    query: str
    team_id: str
    top_k: Optional[int] = 5

class IngestRequest(BaseModel):
    team_id: str
    faqs: List[Dict]
    category: Optional[str] = None

# Response Models (Pydantic - auto-formatted)
class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]
    message: str

class StatsResponse(BaseModel):
    team_id: str
    document_count: int
    vector_dimension: int

# Endpoints
@app.post("/api/v1/retrieve")
async def retrieve(request: RetrieveRequest) -> RetrievalResult:
    # Retrieve documents
    
@app.post("/api/v1/ingest")
async def ingest(request: IngestRequest) -> IngestResponse:
    # Ingest FAQs
    
@app.get("/api/v1/health")
async def health_check() -> HealthResponse:
    # Health check
    
@app.get("/api/v1/stats/{team_id}")
async def get_stats(team_id: str) -> StatsResponse:
    # Get statistics
```

**Design Pattern Details:**

```python
# REQUEST-RESPONSE Pattern:

@app.post("/api/v1/retrieve")
async def retrieve(request: RetrieveRequest) -> RetrievalResult:
    
    # Step 1: Receive and validate request
    # FastAPI automatically validates:
    # - request.query is string
    # - request.team_id is string
    # - request.top_k is optional int
    
    try:
        # Step 2: Call business logic
        result = rag_orchestrator.retrieve(
            query_text=request.query,
            team_id=request.team_id,
            top_k=request.top_k
        )
        
        # Step 3: Return response (auto-serialized to JSON)
        return result  # FastAPI serializes RetrievalResult to JSON
        
    except QueryProcessingError as e:
        # Step 4: Handle errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error")
```

### 2. `app.py` (100 lines)

**Responsibility:** Configure FastAPI application

**Design Pattern Used: APPLICATION FACTORY**

```
Factory Pattern: Create and configure application

def create_app():
    app = FastAPI(...)
    
    # Configure
    app.add_middleware(CORSMiddleware, ...)
    app.include_router(router)
    
    # Add endpoints
    @app.get("/")
    async def root():
        return {"status": "ready"}
    
    return app

# Usage:
app = create_app()
# Can create multiple instances with different configs
```

**What It Contains:**

```python
def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG Framework API",
        description="...",
        version="1.0.0",
        lifespan=lifespan  # Startup/shutdown events
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,  # Allow cross-origin requests
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Include routes
    app.include_router(router)
    
    # Add health endpoints
    @app.get("/alive")
    async def liveness():
        return {"status": "alive"}
    
    return app

# Global instance
app = create_app()
```

**Lifespan Events:**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print("Starting RAG Framework API...")
    # Initialize resources, load models, etc.
    
    yield  # Application runs here
    
    # SHUTDOWN
    print("Shutting down...")
    # Cleanup resources
```

### 3. `__init__.py` (5 lines)

**Purpose:** Export router

```python
from .routes import router

__all__ = ["router"]
```

## Design Patterns in API Module

### 1. **Request-Response Pattern**
```
HTTP standard pattern
Validate input, call logic, format output
Consistent error handling
```

### 2. **Application Factory Pattern**
```
create_app() returns configured application
Easy to test
Can create multiple instances
```

### 3. **Dependency Injection (FastAPI feature)**
```python
@app.get("/stats/{team_id}")
async def get_stats(team_id: str):
    # FastAPI extracts team_id from URL path
    # Validates type
    # Injects into function
    
    # Could also do:
    def get_stats(team_id: str = Path(...)):
        pass  # More explicit
```

---

# MODULE 5: SDK (`src/sdk/`)

## Module Purpose

**"Provide Python Library Interface"**

The SDK allows Python developers to use the framework as a library, without HTTP overhead.

## Why This Module Exists

### Problems It Solves

```
❌ WITHOUT SDK Module:
  - Python code must use REST API (HTTP overhead)
  - Need to handle JSON serialization
  - No direct library access
  - Slower (network latency)

✓ WITH SDK Module:
  - Direct Python library access
  - No HTTP overhead
  - Type-safe (IDE autocomplete)
  - Familiar Python interface
  - Fast (in-process)
```

## Files in This Module

### 1. `client.py` (250 lines)

**Responsibility:** Provide Python client interface

**Design Pattern Used: FACADE**

```
Facade Pattern: Simple interface to complex subsystem

+─────────────────────────────────┐
│ RAGClient (Facade)              │ ← Simple interface
├─────────────────────────────────┤
│ Coordinates:                    │
├─ rag_orchestrator             │
├─ ingestion_service            │
├─ vector_store                 │
└─ (other services)             │
└─────────────────────────────────┘
```

**What It Contains:**

```python
class RAGClient:
    """Python SDK client"""
    
    def ingest_faqs(team_id: str, faqs: List[Dict]) -> Dict:
        # Ingest FAQ documents
        return ingestion_service.ingest_faqs_from_json(team_id, faqs)
    
    def ingest_faqs_from_file(team_id: str, file_path: str) -> Dict:
        # Load from file
        return ingestion_service.ingest_faqs_from_file(team_id, file_path)
    
    def retrieve(query: str, team_id: str, top_k: int) -> RetrievalResult:
        # Main retrieval
        return rag_orchestrator.retrieve(query, team_id, top_k)
    
    def retrieve_expanded(query: str, team_id: str, top_k: int) -> RetrievalResult:
        # Multi-pass retrieval
        return rag_orchestrator.retrieve_with_expansion(query, team_id, top_k)
    
    def get_stats(team_id: str) -> Dict:
        # Team statistics
        return vector_store.get_stats(team_id)
    
    def health_check() -> Dict:
        # System health
        return rag_orchestrator.health_check()
    
    def delete_faq(team_id: str, faq_id: str) -> Dict:
        # Delete FAQ
        return ingestion_service.delete_faq(team_id, faq_id)
```

**Design Pattern Details:**

```python
# FACADE Pattern Implementation:

# Complex subsystem (many services):
from src.services import (
    ingestion_service,
    embedding_service,
    vector_store,
    rag_orchestrator,
    query_processor
)

class RAGClient:
    # Facade: Simple interface that coordinates services
    
    def retrieve(self, query, team_id, top_k):
        # User doesn't need to:
        # 1. Call query_processor
        # 2. Call embedding_service
        # 3. Call vector_store
        # 4. Calculate scores
        # 5. Package results
        
        # Just calls orchestrator:
        return rag_orchestrator.retrieve(query, team_id, top_k)
    
    # One line to user = multiple services behind the scenes

# Benefits:
# 1. Simple API for users
# 2. Complex logic hidden
# 3. User code is clean
# 4. Easy to change internal organization
```

### 2. `__init__.py` (5 lines)

**Purpose:** Export client

```python
from .client import RAGClient, create_client

__all__ = ["RAGClient", "create_client"]
```

## Design Patterns in SDK Module

### 1. **Facade Pattern**
```
Simple interface hiding complex subsystem
User calls client.retrieve()
Behind scenes: multiple services coordinate
```

### 2. **Wrapper Pattern**
```
Wraps orchestrator and other services
Provides Python-native interface
No JSON serialization needed
```

---

# MODULE INTERACTIONS

## Dependency Graph

```
API Routes
    ├─ Calls: RAG Orchestrator
    └─ Uses: Domain Models
         └─ Imports: QueryProcessingError

SDK Client
    ├─ Calls: RAG Orchestrator
    ├─ Calls: Ingestion Service
    ├─ Calls: Vector Store
    └─ Uses: Domain Models

RAG Orchestrator
    ├─ Calls: Query Processor
    ├─ Calls: Embedding Service
    ├─ Calls: Vector Store
    └─ Uses: Domain Models

Ingestion Service
    ├─ Calls: Embedding Service
    ├─ Calls: Vector Store
    └─ Uses: Domain Models

Vector Store
    └─ Uses: Domain Models

Query Processor
    ├─ Uses: Domain Models
    └─ Imports: QueryProcessingError

Embedding Service
    ├─ Uses: Domain Models
    └─ Imports: EmbeddingError

All Services
    └─ Import: Settings from Config
```

## Data Flow Example: Retrieval Request

```
User API Request
    ↓
API Routes (routes.py)
    ├─ Validate request (RetrieveRequest model)
    └─ Call: rag_orchestrator.retrieve()
         ↓
    RAG Orchestrator (rag_orchestrator.py)
         ├─ Call: query_processor.process_query()
         │    ├─ Normalize query
         │    ├─ Classify type
         │    ├─ Expand query
         │    └─ Return: SearchQuery
         │
         ├─ Call: embedding_service.embed_text()
         │    ├─ Load model (cached)
         │    ├─ Encode text
         │    ├─ Normalize vectors
         │    └─ Return: List[float]
         │
         ├─ Call: vector_store.search()
         │    ├─ Get team's collection
         │    ├─ Query HNSW index
         │    ├─ Convert distances to similarities
         │    └─ Return: [(doc_id, score, metadata), ...]
         │
         ├─ Call: _score_document() for each result
         │    ├─ Calculate: vector_score * 0.70
         │    ├─ Add: keyword_bonus up to 0.30
         │    └─ Return: final_score
         │
         └─ Create: RetrievalResult object
              ├─ Pack: query, results, timing, confidence
              └─ Return: RetrievalResult
         ↓
API Routes
    └─ Serialize: RetrievalResult → JSON
         ↓
HTTP Response
    └─ Send: JSON to client
```

## Data Flow Example: Ingestion Request

```
User API Request
    ↓
API Routes (routes.py)
    ├─ Validate request (IngestRequest model)
    └─ Call: ingestion_service.ingest_faqs_from_json()
         ↓
    Ingestion Service (ingestion_service.py)
         ├─ For each FAQ:
         │  ├─ Validate fields
         │  ├─ Call: _chunk_text()
         │  │  └─ Split > 500 chars
         │  │
         │  ├─ Call: _extract_keywords()
         │  │  └─ Auto-extract meaningful words
         │  │
         │  ├─ Call: embedding_service.embed_texts()
         │  │  └─ Embed chunks (batch efficient)
         │  │
         │  └─ Create: Document objects
         │
         └─ Call: vector_store.add_documents()
              ├─ Get team's collection
              ├─ Add embeddings, metadata
              ├─ Build HNSW index
              └─ Persist to disk
         ↓
API Routes
    └─ Return: IngestResponse (stats)
         ↓
HTTP Response
    └─ Send: JSON with results
```

---

# DESIGN PATTERNS SUMMARY

## All Patterns Used

### 1. **LAYERED ARCHITECTURE**
```
Config → Domain → Services → API/SDK
Dependencies flow downward only
Each layer has clear responsibility
```

### 2. **SINGLETON PATTERN**
- Settings instance
- All service instances
- Embedding model (expensive to load)
- Vector store client

### 3. **ADAPTER PATTERN**
- EmbeddingService wraps sentence-transformers
- Abstracts external library

### 4. **REPOSITORY PATTERN**
- ChromaDBVectorStore abstracts data storage
- Application independent of storage tech

### 5. **STRATEGY PATTERN**
- IngestionService: multiple input sources
- QueryProcessor: multiple classification strategies

### 6. **CHAIN OF RESPONSIBILITY PATTERN**
- QueryProcessor: series of processing steps
- Each step independent

### 7. **ORCHESTRATOR/FACADE PATTERN**
- RAGOrchestrator: coordinates services
- RAGClient: simple Python interface

### 8. **VALUE OBJECT PATTERN**
- Domain models (FAQ, Document, SearchResult)
- Immutable, defined by content

### 9. **REQUEST-RESPONSE PATTERN**
- REST API endpoints
- Input validation, output serialization

### 10. **APPLICATION FACTORY PATTERN**
- create_app() configures FastAPI

## Why Multiple Patterns?

```
Each pattern solves specific problem:

Config Module:
└─ Singleton: One instance, shared state

Services Module:
├─ Adapter: Wrap external libraries
├─ Repository: Abstract storage
├─ Strategy: Multiple ways to do same thing
├─ Chain of Responsibility: Sequential processing
└─ Orchestrator: Coordinate multiple services

API Module:
└─ Request-Response: HTTP standard

SDK Module:
└─ Facade: Simple interface

Domain Module:
├─ Value Object: Data structures
└─ Exception Hierarchy: Error handling

No single pattern solves everything!
Each pattern = tool for specific job
Combined = clean, maintainable architecture
```

---

## EXAMPLE: How It All Works Together

### Scenario: Retrieve FAQ Documents

```
┌─────────────────────────────────────────────────────────────────┐
│ User calls via REST API                                         │
│ POST /api/v1/retrieve                                           │
│ {                                                               │
│   "query": "How to reset password?",                            │
│   "team_id": "team-1",                                          │
│   "top_k": 5                                                    │
│ }                                                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │ API Routes (routes.py)            │
         ├───────────────────────────────────┤
         │ 1. Validate (RetrieveRequest)     │
         │    - query: string ✓              │
         │    - team_id: string ✓            │
         │    - top_k: int (1-50) ✓          │
         │                                   │
         │ 2. Call rag_orchestrator.retrieve()
         └──────────────┬──────────────────┘
                        │
        ┌───────────────▼──────────────────┐
        │ RAG Orchestrator                 │
        │ (rag_orchestrator.py)            │
        ├──────────────────────────────────┤
        │ 1. query_processor.process_query()
        │    ├─ Normalize: "reset password"
        │    ├─ Classify: HOW_TO
        │    ├─ Expand: ["reset password",
        │    │           "change password",
        │    │           ...]
        │    └─ Return: SearchQuery
        │
        │ 2. embedding_service.embed_text()
        │    ├─ Load model (cached)
        │    ├─ Encode: "reset password"
        │    ├─ Normalize (L2 norm)
        │    └─ Return: [0.1, 0.2, ..., 0.9]
        │               (384 dims)
        │
        │ 3. vector_store.search()
        │    ├─ Get collection: "team_1_documents"
        │    ├─ Query HNSW index
        │    ├─ Top-5 similar vectors
        │    └─ Return:
        │        [("doc-1", 0.92, {...}),
        │         ("doc-2", 0.85, {...}),
        │         ...]
        │
        │ 4. For each result:
        │    _score_document()
        │    ├─ vector: 0.92 * 0.70 = 0.644
        │    ├─ keyword: 2 matches * 0.05 = 0.1
        │    └─ final: 0.744
        │
        │ 5. Create SearchResult objects
        │    └─ Rank 1: score 0.924
        │       Rank 2: score 0.596
        │       ...
        │
        │ 6. Create RetrievalResult
        │    ├─ query: "reset password"
        │    ├─ results: [SearchResult, ...]
        │    ├─ execution_time: 45.3ms
        │    ├─ confidence: 0.924
        │    └─ Return: RetrievalResult
        └──────────────┬──────────────────┘
                       │
         ┌─────────────▼────────────────┐
         │ API Routes (serialize)       │
         ├──────────────────────────────┤
         │ RetrievalResult → JSON       │
         └──────────────┬───────────────┘
                        │
         ┌──────────────▼───────────────┐
         │ HTTP Response                │
         │ {                            │
         │   "query": "reset password", │
         │   "results": [               │
         │     {                        │
         │       "rank": 1,             │
         │       "score": 0.924,        │
         │       "content": "Click...", │
         │       "category": "account"  │
         │     },                       │
         │     ...                      │
         │   ],                         │
         │   "execution_time_ms": 45.3  │
         │ }                            │
         └──────────────────────────────┘
```

---

## Summary: Why This Architecture?

```
Config Module
└─ Why: Central configuration management
   └─ Pattern: Singleton
      └─ Benefit: One source of truth

Domain Module
└─ Why: Define data structures
   └─ Pattern: Value Objects + Exception Hierarchy
      └─ Benefit: Type safety, clear schema

Services Module
└─ Why: Implement business logic
   └─ Patterns:
      ├─ Singleton: Share expensive resources
      ├─ Adapter: Wrap external libraries
      ├─ Repository: Abstract storage
      ├─ Strategy: Multiple approaches
      ├─ Chain of Responsibility: Sequential processing
      └─ Orchestrator: Coordinate services
   └─ Benefit: Testable, reusable, maintainable

API Module
└─ Why: Expose services via HTTP
   └─ Patterns:
      ├─ Request-Response: HTTP standard
      └─ Application Factory: Configurable app
   └─ Benefit: Universal access, documented, scalable

SDK Module
└─ Why: Python library interface
   └─ Pattern: Facade
      └─ Benefit: Simple, fast, no HTTP overhead

Result: Clean, maintainable, scalable architecture!
```
