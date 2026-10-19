"""
Complete Example - Using RAG Framework Python SDK.

This example demonstrates:
1. Creating a client
2. Ingesting FAQs
3. Retrieving documents
4. Getting statistics
5. Health checks

Run this example:
    python example_sdk_usage.py
"""

import sys
sys.path.insert(0, '.')

from src.sdk.client import RAGClient


def main():
    """Complete example workflow."""

    print("\n" + "=" * 70)
    print("RAG Framework - Python SDK Example")
    print("=" * 70 + "\n")

    # Step 1: Create client
    print("1. Creating RAG client...")
    client = RAGClient()
    print("   ✓ Client created\n")

    # Step 2: Health check
    print("2. Running health check...")
    health = client.health_check()
    print(f"   Embedding service: {health['embedding_service']}")
    print(f"   Vector store: {health['vector_store']}")
    print(f"   Overall status: {health['overall']}\n")

    # Step 3: Prepare FAQ data
    print("3. Preparing FAQ data for team-1...")
    team1_faqs = [
        {
            "id": "faq-account-001",
            "question": "How do I reset my password?",
            "answer": "Click Settings > Security > Change Password. Enter your email and follow the verification steps. You'll receive a reset link via email.",
            "category": "account",
            "keywords": ["password", "reset", "account", "security"]
        },
        {
            "id": "faq-account-002",
            "question": "How do I create an account?",
            "answer": "Visit our signup page, enter your email, choose a strong password, and click Create Account. Check your email for verification.",
            "category": "account",
            "keywords": ["account", "create", "signup", "register"]
        },
        {
            "id": "faq-security-001",
            "question": "How do I enable two-factor authentication?",
            "answer": "Go to Settings > Security > Two-Factor Auth. Scan the QR code with an authenticator app and enter the 6-digit code to confirm.",
            "category": "security",
            "keywords": ["authentication", "2fa", "security", "mfa"]
        },
        {
            "id": "faq-account-003",
            "question": "How do I delete my account?",
            "answer": "Go to Settings > Privacy > Delete Account. Enter your password and confirm. Your data will be permanently removed.",
            "category": "account",
            "keywords": ["delete", "account", "remove", "privacy"]
        }
    ]

    print(f"   Prepared {len(team1_faqs)} FAQs\n")

    # Step 4: Ingest FAQs for Team 1
    print("4. Ingesting FAQs for team-1...")
    stats = client.ingest_faqs(
        team_id="team-1",
        faqs=team1_faqs
    )
    print(f"   ✓ Ingested {stats['total_faqs']} FAQs")
    print(f"   ✓ Created {stats['total_documents']} documents")
    if stats['errors']:
        print(f"   ⚠ Errors: {len(stats['errors'])}")
    print()

    # Step 5: Ingest different FAQs for Team 2
    print("5. Ingesting FAQs for team-2 (different domain)...")
    team2_faqs = [
        {
            "id": "faq-api-001",
            "question": "What is the GET /users endpoint?",
            "answer": "Retrieves a list of users. Requires authentication. Returns paginated results (page, limit parameters).",
            "category": "api",
            "keywords": ["api", "get", "users", "endpoint"]
        },
        {
            "id": "faq-api-002",
            "question": "How do I authenticate with the API?",
            "answer": "Use Bearer token authentication. Include Authorization: Bearer {token} in request headers.",
            "category": "api",
            "keywords": ["api", "authentication", "bearer", "token"]
        }
    ]

    stats = client.ingest_faqs(
        team_id="team-2",
        faqs=team2_faqs
    )
    print(f"   ✓ Ingested {stats['total_faqs']} FAQs for team-2\n")

    # Step 6: Get statistics
    print("6. Getting team statistics...")
    stats_team1 = client.get_stats("team-1")
    stats_team2 = client.get_stats("team-2")
    print(f"   Team 1: {stats_team1['document_count']} documents")
    print(f"   Team 2: {stats_team2['document_count']} documents")
    print(f"   Vector dimension: {stats_team1['vector_dimension']}\n")

    # Step 7: Retrieve for Team 1 (Account question)
    print("7. Retrieving for team-1: 'How do I reset my password?'")
    results = client.retrieve(
        query="How do I reset my password?",
        team_id="team-1",
        top_k=3
    )

    print(f"   Found {len(results.results)} results in {results.execution_time_ms:.1f}ms\n")
    for result in results.results:
        print(f"   #{result.rank}. Score: {result.relevance_score:.1%}")
        print(f"      Category: {result.category}")
        print(f"      Content: {result.content[:60]}...")
        print()

    # Step 8: Retrieve for Team 1 (Different question)
    print("8. Retrieving for team-1: 'How do I delete my account?'")
    results = client.retrieve(
        query="delete account",
        team_id="team-1",
        top_k=2
    )

    print(f"   Found {len(results.results)} results\n")
    for result in results.results:
        print(f"   #{result.rank}. Score: {result.relevance_score:.1%}")
        print(f"      {result.content[:70]}...\n")

    # Step 9: Retrieve for Team 2 (API question - should NOT see Team 1's results)
    print("9. Retrieving for team-2: 'How do I authenticate?'")
    print("   (Should ONLY get Team 2's API-related docs, NOT Team 1's account docs)")
    results = client.retrieve(
        query="How do I authenticate?",
        team_id="team-2",
        top_k=3
    )

    print(f"   Found {len(results.results)} results\n")
    for result in results.results:
        print(f"   #{result.rank}. Score: {result.relevance_score:.1%}")
        print(f"      Category: {result.category}")
        print(f"      Content: {result.content[:60]}...")
        print()

    # Step 10: Multi-pass retrieval with expansion
    print("10. Multi-pass retrieval (with query expansion)...")
    print("    Query: 'password change problem'")
    results = client.retrieve_expanded(
        query="password change problem",
        team_id="team-1",
        top_k=3
    )

    print(f"    Found {len(results.results)} results with expansion\n")
    for result in results.results:
        print(f"    #{result.rank}. Score: {result.relevance_score:.1%}")
        print(f"       {result.content[:60]}...\n")

    # Step 11: Error handling - Invalid team
    print("11. Testing error handling...")
    try:
        results = client.retrieve(
            query="test query",
            team_id="team-999"  # Non-existent team
        )
        # This creates an empty collection if it doesn't exist
        print(f"    Retrieved {len(results.results)} results (empty collection created)\n")
    except Exception as e:
        print(f"    Error (expected for non-existent team): {e}\n")

    print("=" * 70)
    print("✓ Example completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Run API server: python run_api.py")
    print("2. Visit API docs: http://localhost:8000/docs")
    print("3. Try REST endpoints via Swagger UI")
    print()


if __name__ == "__main__":
    main()
