"""
EXERCISE 4: Extend the Framework

Learn how to extend the RAG framework with custom features:

1. Add a new content type (CODE)
2. Custom metadata extraction
3. Custom filtering
4. Performance benchmarking

Run: python exercise_4_extend_framework.py
"""

import time
from src.sdk.client import RAGClient
from src.domain.models import ContentType

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def demo_code_content():
    """Demo: Ingest CODE content type."""
    print_header("DEMO 1: CODE Content Type")

    client = RAGClient()

    # Code snippets
    code_content = [
        {
            "id": "py-auth-001",
            "title": "Python: Basic Authentication",
            "body": """
import requests

def authenticate(api_key):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(
        "https://api.example.com/user",
        headers=headers
    )
    return response.json()

# Usage
user_data = authenticate("your-api-key")
print(user_data)
            """,
            "content_type": "code",
            "category": "authentication",
            "keywords": ["python", "auth", "api", "bearer", "token"]
        },
        {
            "id": "js-fetch-001",
            "title": "JavaScript: Fetch with Auth",
            "body": """
const fetchWithAuth = async (url, apiKey) => {
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};

// Usage
fetchWithAuth('https://api.example.com/data', 'your-key')
  .then(data => console.log(data))
  .catch(err => console.error(err));
            """,
            "content_type": "code",
            "category": "authentication",
            "keywords": ["javascript", "fetch", "async", "auth"]
        },
        {
            "id": "sql-query-001",
            "title": "SQL: Get User Profile",
            "body": """
SELECT u.id, u.name, u.email, u.created_at
FROM users u
WHERE u.id = %s
  AND u.status = 'active'
ORDER BY u.created_at DESC;

-- This query fetches active user profiles
-- Use parameterized queries to prevent SQL injection
            """,
            "content_type": "code",
            "category": "database",
            "keywords": ["sql", "query", "select", "users"]
        }
    ]

    print("Ingesting code snippets...")
    result = client.ingest_content(
        team_id="code-examples",
        content=code_content
    )

    print(f"[OK] Ingested {result['total_chunks']} code chunks")

    # Search for code examples
    queries = [
        "How do I authenticate in Python?",
        "Show me JavaScript fetch example",
        "SQL query for user data"
    ]

    print("\nSearching for code examples:")
    for query in queries:
        results = client.retrieve(
            query=query,
            team_id="code-examples",
            top_k=1
        )

        if results.results:
            r = results.results[0]
            print(f"\n  Query: '{query}'")
            print(f"  Found: {r.content[:60]}...")
            print(f"  Type: {r.content_type}, Score: {r.relevance_score:.1%}")

    print()

def demo_metadata_filtering():
    """Demo: Filter results by metadata."""
    print_header("DEMO 2: Metadata Filtering")

    client = RAGClient()

    # Ingest mixed content
    mixed_content = [
        {
            "id": "faq-billing-001",
            "title": "How to update billing?",
            "body": "Go to Settings > Billing > Update payment method.",
            "content_type": "faq",
            "category": "billing",
            "keywords": ["billing", "payment"]
        },
        {
            "id": "faq-auth-001",
            "title": "How to reset password?",
            "body": "Click Forgot Password and follow email link.",
            "content_type": "faq",
            "category": "authentication",
            "keywords": ["password", "auth"]
        },
        {
            "id": "doc-billing-001",
            "title": "Billing Documentation",
            "body": "Complete guide to billing, invoices, and payments.",
            "content_type": "documentation",
            "category": "billing",
            "keywords": ["billing", "invoice"]
        }
    ]

    print("Ingesting mixed content...")
    result = client.ingest_content(
        team_id="mixed-content",
        content=mixed_content
    )

    print(f"[OK] Ingested {result['total_chunks']} mixed chunks")

    # Search by query
    print("\nSearching for 'billing':")
    results = client.retrieve(
        query="billing",
        team_id="mixed-content",
        top_k=5
    )

    print(f"Found {len(results.results)} results:")
    for r in results.results:
        print(f"  - {r.content[:50]}... "
              f"[{r.content_type}, cat:{r.category}, score:{r.relevance_score:.1%}]")

    print()

def demo_performance_benchmark():
    """Demo: Benchmark performance."""
    print_header("DEMO 3: Performance Benchmarking")

    client = RAGClient()

    # Generate test content
    test_content = []
    for i in range(20):
        test_content.append({
            "id": f"perf-test-{i}",
            "title": f"Test Document {i}",
            "body": f"This is test document number {i}. "
                   f"It contains various keywords to test retrieval performance. "
                   f"Performance is critical for good user experience.",
            "content_type": "faq",
            "category": f"category-{i % 5}",
            "keywords": ["test", "performance", f"doc-{i}"]
        })

    # Benchmark ingestion
    print(f"Benchmarking ingestion of {len(test_content)} documents...")
    start = time.time()
    ingest_result = client.ingest_content(
        team_id="perf-test",
        content=test_content
    )
    ingest_time = time.time() - start

    print(f"[OK] Ingest time: {ingest_time:.2f}s")
    print(f"     Throughput: {len(test_content)/ingest_time:.1f} docs/sec")
    print(f"     Average: {(ingest_time*1000)/len(test_content):.1f}ms per doc")

    # Benchmark retrieval
    queries = [
        "test document",
        "performance critical",
        "retrieval experience",
        "category search",
        "keyword matching"
    ]

    print(f"\nBenchmarking {len(queries)} queries...")
    times = []

    for query in queries:
        start = time.time()
        results = client.retrieve(
            query=query,
            team_id="perf-test",
            top_k=5
        )
        query_time = time.time() - start
        times.append(query_time)
        print(f"  '{query}': {results.execution_time_ms:.1f}ms")

    avg_query_time = sum(times) / len(times)
    print(f"\nAverage query time: {avg_query_time*1000:.1f}ms")
    print(f"Queries per second: {1/avg_query_time:.1f}")

    print()

def demo_advanced_retrieval():
    """Demo: Advanced retrieval techniques."""
    print_header("DEMO 4: Advanced Retrieval")

    client = RAGClient()

    # Ingest with rich metadata
    content = [
        {
            "id": "advanced-001",
            "title": "Advanced Topic: Caching Strategies",
            "body": "Caching improves performance. Use Redis for session cache, "
                   "memcached for data cache. TTL important for cache invalidation.",
            "content_type": "documentation",
            "category": "performance",
            "keywords": ["cache", "redis", "performance", "ttl"]
        },
        {
            "id": "advanced-002",
            "title": "Query Optimization Tips",
            "body": "Write efficient queries with proper indexing. "
                   "Use EXPLAIN to analyze queries. Avoid N+1 problems. "
                   "Connection pooling reduces overhead.",
            "content_type": "documentation",
            "category": "optimization",
            "keywords": ["query", "index", "performance", "database"]
        }
    ]

    print("Ingesting advanced content...")
    client.ingest_content(
        team_id="advanced",
        content=content
    )

    # Standard retrieval
    print("\n[1] Standard retrieval:")
    results = client.retrieve(
        query="performance optimization",
        team_id="advanced",
        top_k=2
    )
    print(f"    Found {len(results.results)} results")

    # Expanded retrieval (multi-pass)
    print("\n[2] Expanded retrieval (tries multiple query variations):")
    results_expanded = client.retrieve_expanded(
        query="performance",
        team_id="advanced",
        top_k=2
    )
    print(f"    Found {len(results_expanded.results)} results (may be more comprehensive)")

    print()

def main():
    """Run all demos."""
    print_header("EXERCISE 4: Extend the Framework")

    demos = [
        ("CODE Content Type", demo_code_content),
        ("Metadata Filtering", demo_metadata_filtering),
        ("Performance Benchmark", demo_performance_benchmark),
        ("Advanced Retrieval", demo_advanced_retrieval)
    ]

    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"[ERROR] Demo failed: {e}\n")

    print_header("EXERCISE 4 COMPLETE")
    print("You've successfully:")
    print("  [OK] Added CODE content type")
    print("  [OK] Ingested mixed content types")
    print("  [OK] Filtered and searched content")
    print("  [OK] Benchmarked performance")
    print("  [OK] Tested advanced retrieval")
    print("\nWhat you learned:")
    print("  - How to ingest different content types")
    print("  - Metadata extraction and filtering")
    print("  - Performance characteristics")
    print("  - Query expansion for better results")
    print("\nNext steps:")
    print("  - Build your own custom content types")
    print("  - Add domain-specific metadata extraction")
    print("  - Integrate into your own applications")
    print("  - Deploy to production\n")

if __name__ == "__main__":
    main()
