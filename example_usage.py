"""
Example usage of RAG Framework - Step 2

This example shows how to:
1. Create documents with embeddings
2. Store them in ChromaDB (team-scoped)
3. Search for relevant FAQs

Run this example:
    python example_usage.py
"""

import sys
sys.path.insert(0, '.')

from src.services.embedding_service import embedding_service
from src.services.chroma_vector_store import vector_store
from src.domain.models import Document
from src.config.settings import settings

def main():
    """Example: Store and retrieve FAQs."""

    print("=" * 70)
    print("RAG Framework - Step 2 Example")
    print("=" * 70)

    # ===== Step 1: Create FAQ documents =====
    print("\n1. Creating FAQ documents...")

    faqs_team_1 = [
        {
            "id": "faq-001",
            "question": "How do I reset my password?",
            "answer": "Click Settings > Security > Change Password. Enter your email and follow the verification steps.",
            "category": "account",
            "keywords": ["password", "reset", "account", "security"]
        },
        {
            "id": "faq-002",
            "question": "How do I create an account?",
            "answer": "Visit our signup page, enter your email, choose a password, and click Create Account. Check your email for verification.",
            "category": "account",
            "keywords": ["account", "create", "signup", "register"]
        },
        {
            "id": "faq-003",
            "question": "How do I enable two-factor authentication?",
            "answer": "Go to Settings > Security > Two-Factor Auth. Scan the QR code with your authenticator app and enter the code to confirm.",
            "category": "security",
            "keywords": ["authentication", "2fa", "security", "mfa"]
        }
    ]

    # ===== Step 2: Embed documents =====
    print("2. Generating embeddings for FAQ content...")

    documents_team_1 = []
    for faq in faqs_team_1:
        # Embed the full FAQ (question + answer)
        full_text = f"{faq['question']} {faq['answer']}"
        embedding = embedding_service.embed_text(full_text)

        # Create document
        doc = Document(
            id=f"{faq['id']}-chunk-0",
            content=faq['answer'],
            faq_id=faq['id'],
            chunk_index=0,
            embedding=embedding,
            category=faq['category'],
            keywords=faq['keywords'],
            entities=[]
        )
        documents_team_1.append(doc)
        print(f"   ✓ Embedded {faq['id']}: {faq['question'][:40]}...")

    # ===== Step 3: Store in ChromaDB (Team 1) =====
    print("\n3. Storing documents in ChromaDB (Team 1)...")

    count = vector_store.add_documents(
        team_id="team-1",
        documents=documents_team_1
    )
    print(f"   ✓ Stored {count} documents for team-1")

    # ===== Step 4: Create different docs for Team 2 =====
    print("\n4. Storing different documents for Team 2...")

    faqs_team_2 = [
        {
            "id": "api-001",
            "question": "What is the GET /users endpoint?",
            "answer": "Retrieves a list of users. Authentication required. Returns paginated results.",
            "category": "api",
            "keywords": ["api", "get", "users", "endpoint"]
        },
        {
            "id": "api-002",
            "question": "How do I authenticate with the API?",
            "answer": "Use Bearer token authentication. Include Authorization: Bearer {token} in request headers.",
            "category": "api",
            "keywords": ["api", "authentication", "bearer", "token"]
        }
    ]

    documents_team_2 = []
    for faq in faqs_team_2:
        full_text = f"{faq['question']} {faq['answer']}"
        embedding = embedding_service.embed_text(full_text)

        doc = Document(
            id=f"{faq['id']}-chunk-0",
            content=faq['answer'],
            faq_id=faq['id'],
            chunk_index=0,
            embedding=embedding,
            category=faq['category'],
            keywords=faq['keywords'],
            entities=[]
        )
        documents_team_2.append(doc)
        print(f"   ✓ Embedded {faq['id']}: {faq['question'][:40]}...")

    count = vector_store.add_documents(
        team_id="team-2",
        documents=documents_team_2
    )
    print(f"   ✓ Stored {count} documents for team-2")

    # ===== Step 5: Search Team 1 =====
    print("\n5. Searching Team 1 for 'How do I reset password?'...")

    query_text = "How do I reset password?"
    query_vector = embedding_service.embed_text(query_text)

    results = vector_store.search(
        team_id="team-1",
        query_vector=query_vector,
        top_k=3
    )

    print(f"   Found {len(results)} results:")
    for doc_id, score, metadata in results:
        print(f"   - {doc_id}: score={score:.3f}, category={metadata.get('category')}")

    # ===== Step 6: Search Team 2 (different results) =====
    print("\n6. Searching Team 2 with same query 'How do I reset password?'...")

    results_team_2 = vector_store.search(
        team_id="team-2",
        query_vector=query_vector,
        top_k=3
    )

    print(f"   Found {len(results_team_2)} results:")
    for doc_id, score, metadata in results_team_2:
        print(f"   - {doc_id}: score={score:.3f}, category={metadata.get('category')}")

    # ===== Step 7: Get statistics =====
    print("\n7. Getting collection statistics...")

    stats_team_1 = vector_store.get_stats("team-1")
    stats_team_2 = vector_store.get_stats("team-2")

    print(f"   Team 1: {stats_team_1['document_count']} documents")
    print(f"   Team 2: {stats_team_2['document_count']} documents")
    print(f"   Vector dimension: {stats_team_1['vector_dimension']}")

    # ===== Step 8: Health check =====
    print("\n8. Running health checks...")

    embedding_health = embedding_service.health_check()
    vector_store_health = vector_store.health_check()

    print(f"   Embedding service: {'✓ Healthy' if embedding_health else '✗ Unhealthy'}")
    print(f"   Vector store: {'✓ Healthy' if vector_store_health else '✗ Unhealthy'}")

    print("\n" + "=" * 70)
    print("✓ Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
