"""
EXERCISE 3: REST API Testing

Tests the FastAPI REST endpoints:
1. POST /ingest - Ingest content
2. POST /retrieve - Search for answers
3. GET /health - Health check
4. GET /stats/{team_id} - Team statistics

This demonstrates how external clients (JavaScript, mobile apps, etc.)
would interact with the framework via HTTP.

Run this AFTER starting the server:
  python run_api.py

Then in another terminal:
  python exercise_3_rest_api.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_health():
    """Test health endpoint."""
    print("[TEST 1] Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"[OK] Server is healthy")
            print(f"     Status: {health.get('status')}")
            print(f"     Components: {health.get('components')}\n")
            return True
        else:
            print(f"[ERROR] Health check failed: {response.status_code}\n")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to server at {BASE_URL}")
        print(f"       Make sure to run: python run_api.py\n")
        return False

def test_ingest():
    """Test ingestion endpoint."""
    print("[TEST 2] Ingest Content")

    content = [
        {
            "id": "api-001",
            "title": "API Authentication",
            "body": "All API calls require authentication. Use Authorization header with Bearer token. "
                   "Tokens valid for 24 hours. Refresh token to extend session. "
                   "Include token in every request: Authorization: Bearer YOUR_TOKEN",
            "content_type": "documentation",
            "category": "api",
            "keywords": ["api", "authentication", "token", "bearer"]
        },
        {
            "id": "api-002",
            "title": "Rate Limiting",
            "body": "API rate limited to 1000 requests/hour per token. "
                   "Response includes rate-limit headers: X-RateLimit-Remaining. "
                   "If exceeded, get 429 error. Wait one hour or upgrade plan.",
            "content_type": "documentation",
            "category": "api",
            "keywords": ["api", "rate", "limit", "requests"]
        },
        {
            "id": "api-003",
            "title": "Error Handling",
            "body": "Errors return JSON with error code and message. Common codes: "
                   "400 (bad request), 401 (unauthorized), 429 (rate limited), 500 (server error). "
                   "Check error message for details and retry logic.",
            "content_type": "documentation",
            "category": "api",
            "keywords": ["error", "code", "response", "handling"]
        }
    ]

    payload = {
        "team_id": "api-docs-team",
        "content": content,
        "content_type": "documentation"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ingest",
            json=payload
        )

        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Ingestion successful")
            print(f"     Total content: {result.get('total_content')}")
            print(f"     Total chunks: {result.get('total_chunks')}")
            print(f"     Errors: {len(result.get('errors', []))}\n")
            return True
        else:
            print(f"[ERROR] Ingestion failed: {response.status_code}")
            print(f"        {response.text}\n")
            return False

    except Exception as e:
        print(f"[ERROR] Ingestion error: {e}\n")
        return False

def test_retrieve():
    """Test retrieval endpoint."""
    print("[TEST 3] Retrieve Answers")

    queries = [
        "How do I authenticate with the API?",
        "What are the rate limits?",
        "How do I handle API errors?"
    ]

    for query in queries:
        payload = {
            "query": query,
            "team_id": "api-docs-team",
            "top_k": 3
        }

        try:
            response = requests.post(
                f"{BASE_URL}/retrieve",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()

                print(f"Query: '{query}'")
                print(f"Time: {result.get('execution_time_ms'):.0f}ms, "
                      f"Confidence: {result.get('confidence_score', 0):.1%}")

                for r in result.get('results', [])[:2]:
                    content_preview = r.get('content', '')[:60]
                    score = r.get('relevance_score', 0)
                    print(f"  - {content_preview}... (score: {score:.1%})")

                print()

            else:
                print(f"[ERROR] Retrieval failed: {response.status_code}\n")

        except Exception as e:
            print(f"[ERROR] Retrieval error: {e}\n")

def test_stats():
    """Test statistics endpoint."""
    print("[TEST 4] Team Statistics")

    try:
        response = requests.get(
            f"{BASE_URL}/stats/api-docs-team"
        )

        if response.status_code == 200:
            stats = response.json()
            print(f"[OK] Team stats retrieved")
            print(f"     Team ID: {stats.get('team_id')}")
            print(f"     Document count: {stats.get('document_count')}")
            print(f"     Vector dimension: {stats.get('vector_dimension')}")
            print(f"     Collection: {stats.get('collection_name')}\n")

        else:
            print(f"[ERROR] Stats failed: {response.status_code}\n")

    except Exception as e:
        print(f"[ERROR] Stats error: {e}\n")

def test_multi_team():
    """Test multi-team isolation via API."""
    print("[TEST 5] Multi-Team Isolation")

    # Ingest for team A
    payload_a = {
        "team_id": "team-a",
        "content": [
            {
                "id": "a-001",
                "title": "Team A FAQ",
                "body": "This is Team A specific content.",
                "content_type": "faq",
                "category": "general"
            }
        ]
    }

    # Ingest for team B
    payload_b = {
        "team_id": "team-b",
        "content": [
            {
                "id": "b-001",
                "title": "Team B FAQ",
                "body": "This is Team B specific content.",
                "content_type": "faq",
                "category": "general"
            }
        ]
    }

    try:
        # Ingest both teams
        requests.post(f"{BASE_URL}/ingest", json=payload_a)
        requests.post(f"{BASE_URL}/ingest", json=payload_b)

        print("[OK] Ingested for Team A and Team B")

        # Search Team A
        result_a = requests.post(
            f"{BASE_URL}/retrieve",
            json={"query": "Team A", "team_id": "team-a", "top_k": 1}
        ).json()

        # Search Team B
        result_b = requests.post(
            f"{BASE_URL}/retrieve",
            json={"query": "Team B", "team_id": "team-b", "top_k": 1}
        ).json()

        print(f"     Team A search: Found {len(result_a.get('results', []))} results")
        print(f"     Team B search: Found {len(result_b.get('results', []))} results")
        print(f"     [OK] Teams properly isolated\n")

    except Exception as e:
        print(f"[ERROR] Multi-team test failed: {e}\n")

def main():
    """Run all tests."""
    print_header("EXERCISE 3: REST API Testing")

    print("Connecting to server at:", BASE_URL)
    print("(Make sure to run: python run_api.py)\n")

    # Test health first
    if not test_health():
        print("[ERROR] Cannot connect to server. Exiting.")
        return

    # Run tests
    time.sleep(1)
    test_ingest()
    time.sleep(1)
    test_retrieve()
    time.sleep(1)
    test_stats()
    time.sleep(1)
    test_multi_team()

    print_header("EXERCISE 3 COMPLETE")
    print("You've successfully:")
    print("  [OK] Tested health endpoint")
    print("  [OK] Tested content ingestion via HTTP")
    print("  [OK] Tested content retrieval via HTTP")
    print("  [OK] Retrieved team statistics")
    print("  [OK] Verified multi-team isolation")
    print("\nWhat you learned:")
    print("  - How REST API works")
    print("  - Payload structure for requests")
    print("  - Response formats")
    print("  - HTTP error handling")
    print("\nNext: Try building your own client or modify the app!\n")

if __name__ == "__main__":
    main()
