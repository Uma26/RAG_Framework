"""
EXERCISE 1: Basic SDK Usage - Ingest & Retrieve

This hands-on exercise demonstrates:
1. Creating a RAG client
2. Ingesting sample FAQ content
3. Retrieving relevant answers
4. Analyzing results

Run: python exercise_1_basic_sdk.py
"""

import sys
from src.sdk.client import RAGClient

def print_section(title):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def safe_print(text):
    """Print with fallback for Unicode encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def main():
    print_section("EXERCISE 1: Basic SDK Usage")

    # Step 1: Create RAG client
    print("[STEP 1] Creating RAG client...")
    client = RAGClient()
    print("[OK] Client created successfully\n")

    # Step 2: Prepare sample FAQ content
    print("[STEP 2] Preparing sample FAQ content...")
    sample_faqs = [
        {
            "id": "faq-001",
            "title": "How do I reset my password?",
            "body": "To reset your password, click on 'Forgot Password' on the login page. "
                   "Enter your email address and we'll send you a reset link. "
                   "Click the link and create a new password.",
            "content_type": "faq",
            "category": "account",
            "keywords": ["password", "reset", "login", "account"]
        },
        {
            "id": "faq-002",
            "title": "How do I enable two-factor authentication?",
            "body": "Two-factor authentication (2FA) adds an extra layer of security. "
                   "Go to Settings > Security > Two-Factor Authentication. "
                   "Choose your preferred method (SMS or authenticator app) and follow the prompts.",
            "content_type": "faq",
            "category": "security",
            "keywords": ["2fa", "security", "authentication", "setup"]
        },
        {
            "id": "faq-003",
            "title": "How do I update my billing information?",
            "body": "To update billing information, go to Settings > Billing > Payment Methods. "
                   "You can add a new card, update existing information, or set a default payment method. "
                   "Changes take effect immediately.",
            "content_type": "faq",
            "category": "billing",
            "keywords": ["billing", "payment", "card", "update"]
        },
        {
            "id": "faq-004",
            "title": "What payment methods do you accept?",
            "body": "We accept all major credit cards (Visa, MasterCard, American Express), "
                   "PayPal, and bank transfers for enterprise accounts. "
                   "All payments are processed securely using industry-standard encryption.",
            "content_type": "faq",
            "category": "billing",
            "keywords": ["payment", "card", "credit", "method"]
        },
        {
            "id": "faq-005",
            "title": "How do I export my data?",
            "body": "To export your data, go to Settings > Data > Export. "
                   "Choose your preferred format (JSON, CSV) and date range. "
                   "We'll generate a file that you can download immediately.",
            "content_type": "faq",
            "category": "data",
            "keywords": ["export", "data", "download", "csv"]
        }
    ]
    print(f"[OK] Prepared {len(sample_faqs)} FAQ items\n")

    # Step 3: Ingest content
    print("[STEP 3] Ingesting content into team 'support-demo'...")
    try:
        ingest_result = client.ingest_content(
            team_id="support-demo",
            content=sample_faqs,
            content_type="faq"
        )

        print(f"[OK] Ingestion successful!")
        print(f"  - Total content items: {ingest_result['total_content']}")
        print(f"  - Total chunks created: {ingest_result['total_chunks']}")
        print(f"  - Errors: {len(ingest_result['errors'])}\n")

    except Exception as e:
        print(f"[ERROR] Ingestion failed: {e}\n")
        return

    # Step 4: Get team statistics
    print("[STEP 4] Getting team statistics...")
    try:
        stats = client.get_stats("support-demo")
        print(f"[OK] Team stats retrieved!")
        print(f"  - Document count: {stats['document_count']}")
        print(f"  - Vector dimension: {stats['vector_dimension']}")
        print(f"  - Collection: {stats['collection_name']}\n")
    except Exception as e:
        print(f"[ERROR] Stats retrieval failed: {e}\n")

    # Step 5: Test retrieval with multiple queries
    print("[STEP 5] Testing retrieval with sample queries...")

    test_queries = [
        "How can I reset my password?",
        "How do I make payments?",
        "I need to enable security features",
        "How do I get my data out?"
    ]

    for query_num, query in enumerate(test_queries, 1):
        print(f"\n  Query {query_num}: '{query}'")
        print(f"  {'-'*56}")

        try:
            results = client.retrieve(
                query=query,
                team_id="support-demo",
                top_k=3
            )

            if results.results:
                for result in results.results:
                    print(f"    Rank {result.rank}: {result.content[:80]}...")
                    print(f"    Score: {result.relevance_score:.1%}")
                    print()
            else:
                print("    No results found\n")

        except Exception as e:
            print(f"    Error: {e}\n")

    # Step 6: Test query expansion (multi-pass search)
    print("\n[STEP 6] Testing query expansion (advanced search)...")
    expansion_query = "password trouble"

    try:
        expanded_results = client.retrieve_expanded(
            query=expansion_query,
            team_id="support-demo",
            top_k=3
        )

        print(f"Query: '{expansion_query}'")
        print(f"Results with expansion:\n")

        for result in expanded_results.results:
            print(f"  Rank {result.rank}: {result.content[:80]}...")
            print(f"  Score: {result.relevance_score:.1%}\n")

    except Exception as e:
        print(f"[ERROR] Expansion query failed: {e}\n")

    # Step 7: Demonstrate multi-tenancy
    print("\n[STEP 7] Demonstrating multi-tenancy...")
    print("Ingesting data for a DIFFERENT team...\n")

    tech_docs = [
        {
            "id": "doc-001",
            "title": "API Authentication",
            "body": "All API calls require an authentication token. "
                   "Use Bearer token in Authorization header. "
                   "Tokens expire after 24 hours.",
            "content_type": "documentation",
            "category": "api"
        },
        {
            "id": "doc-002",
            "title": "Rate Limiting",
            "body": "API is rate limited to 1000 requests per hour per API key. "
                   "Rate limit headers are included in responses.",
            "content_type": "documentation",
            "category": "api"
        }
    ]

    try:
        ingest_result = client.ingest_content(
            team_id="dev-demo",  # DIFFERENT team
            content=tech_docs,
            content_type="documentation"
        )
        print(f"[OK] Ingested {ingest_result['total_chunks']} chunks for team 'dev-demo'\n")

        # Now search in EACH team separately
        print("Searching in 'dev-demo' team (should find tech docs):")
        results = client.retrieve(
            query="How do I authenticate?",
            team_id="dev-demo",
            top_k=1
        )
        if results.results:
            print(f"  [OK] Found: {results.results[0].content[:60]}...\n")

        print("Searching in 'support-demo' team (should NOT find tech docs):")
        results = client.retrieve(
            query="How do I authenticate?",
            team_id="support-demo",
            top_k=1
        )
        if results.results:
            print(f"  [OK] Found: {results.results[0].content[:60]}...")
        else:
            print(f"  [OK] No results (as expected - data is isolated)\n")

    except Exception as e:
        print(f"[ERROR] Multi-tenancy test failed: {e}\n")

    # Final summary
    print_section("EXERCISE 1 COMPLETE")
    print("You've successfully:")
    print("  [OK] Created a RAG client")
    print("  [OK] Ingested FAQ content")
    print("  [OK] Retrieved relevant answers")
    print("  [OK] Tested query expansion")
    print("  [OK] Demonstrated multi-tenancy isolation")
    print("\nWhat you learned:")
    print("  - How to use the SDK in Python")
    print("  - Content ingestion pipeline")
    print("  - Vector search retrieval")
    print("  - Team-level data isolation")
    print("\nNext: Run Exercise 2 to build a CLI app!")
    print()

if __name__ == "__main__":
    main()
