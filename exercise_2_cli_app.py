"""
EXERCISE 2: Build a CLI Support Bot

A real interactive CLI application that:
1. Loads FAQs from JSON file
2. Allows users to ask questions
3. Returns relevant answers with confidence scores
4. Shows multi-team support

Run: python exercise_2_cli_app.py
"""

import json
from pathlib import Path
from src.sdk.client import RAGClient

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_result(result, index):
    """Print a single search result."""
    score_percent = result.relevance_score * 100
    score_bar = "[" + "=" * int(score_percent / 5) + " " * (20 - int(score_percent / 5)) + "]"

    print(f"  {index}. {result.content[:75]}...")
    print(f"     Confidence: {score_bar} {score_percent:.0f}%")
    print(f"     Type: {result.content_type}, Category: {result.category}")
    print()

def load_sample_faqs(team_id, client):
    """Load and ingest sample FAQs for a team."""
    sample_content = [
        {
            "id": "auth-001",
            "title": "How do I reset my password?",
            "body": "To reset your password: 1) Click 'Forgot Password' on login page. "
                   "2) Enter your email. 3) Check your inbox for reset link. "
                   "4) Click link and create new password. Password must be 8+ characters with numbers and symbols.",
            "content_type": "faq",
            "category": "authentication",
            "keywords": ["password", "reset", "forgot", "login"]
        },
        {
            "id": "auth-002",
            "title": "How do I enable two-factor authentication?",
            "body": "Enable 2FA: 1) Go to Settings > Security. 2) Click 'Enable 2FA'. "
                   "3) Choose method (SMS or authenticator app). 4) Scan QR code with authenticator. "
                   "5) Enter verification code. You'll receive codes on your phone for login.",
            "content_type": "faq",
            "category": "security",
            "keywords": ["2fa", "security", "authentication", "two-factor"]
        },
        {
            "id": "billing-001",
            "title": "How do I update my billing information?",
            "body": "Update billing: 1) Go to Settings > Billing. 2) Click 'Payment Method'. "
                   "3) Add new card or update existing. 4) We accept all major credit cards. "
                   "5) Changes take effect immediately for next billing cycle.",
            "content_type": "faq",
            "category": "billing",
            "keywords": ["billing", "payment", "card", "update", "invoice"]
        },
        {
            "id": "billing-002",
            "title": "What payment methods do you accept?",
            "body": "We accept: Visa, MasterCard, American Express, PayPal, and bank transfers "
                   "(enterprise only). All transactions encrypted with SSL. Invoices sent monthly. "
                   "Annual plans available with 20% discount. Money-back guarantee within 30 days.",
            "content_type": "faq",
            "category": "billing",
            "keywords": ["payment", "method", "card", "credit", "invoice"]
        },
        {
            "id": "data-001",
            "title": "How do I export my data?",
            "body": "Export data: 1) Go to Settings > Data Management. 2) Click 'Export Data'. "
                   "3) Choose format (JSON or CSV). 4) Select date range. 5) Click Export. "
                   "File downloads immediately. Large exports may take minutes.",
            "content_type": "faq",
            "category": "data",
            "keywords": ["export", "data", "download", "csv", "json"]
        },
        {
            "id": "account-001",
            "title": "How do I delete my account?",
            "body": "Delete account: 1) Go to Settings > Account > Danger Zone. "
                   "2) Click 'Delete Account'. 3) Enter password to confirm. "
                   "4) All data deleted within 30 days. Cannot be recovered. "
                   "Contact support within 30 days to cancel deletion.",
            "content_type": "faq",
            "category": "account",
            "keywords": ["delete", "account", "remove", "close"]
        },
        {
            "id": "support-001",
            "title": "How do I contact support?",
            "body": "Get support: Email support@company.com, Response time 24 hours. "
                   "Chat: Available Mon-Fri 9am-5pm EST. Phone: +1-800-SUPPORT. "
                   "Include order/account number. Premium users get priority support.",
            "content_type": "faq",
            "category": "support",
            "keywords": ["support", "help", "contact", "email", "chat"]
        }
    ]

    print(f"Ingesting {len(sample_content)} FAQs for team '{team_id}'...")
    result = client.ingest_content(
        team_id=team_id,
        content=sample_content,
        content_type="faq"
    )
    print(f"[OK] Ingested {result['total_chunks']} chunks\n")

def interactive_mode(client, team_id):
    """Run interactive CLI bot."""
    print_header(f"Support Bot - Team: {team_id}")
    print("Type 'quit' to exit, 'clear' to clear, 'stats' for team stats\n")

    conversation_count = 0

    while True:
        try:
            user_input = input("You: ").strip()
        except KeyboardInterrupt:
            print("\n[Goodbye!]")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("[Goodbye!]")
            break

        if user_input.lower() == "clear":
            print("\n" * 3)
            continue

        if user_input.lower() == "stats":
            stats = client.get_stats(team_id)
            print(f"\nTeam Statistics:")
            print(f"  - Total chunks: {stats['document_count']}")
            print(f"  - Vector dimension: {stats['vector_dimension']}")
            print(f"  - Collection: {stats['collection_name']}\n")
            continue

        # Search for answer
        try:
            results = client.retrieve(
                query=user_input,
                team_id=team_id,
                top_k=3
            )

            conversation_count += 1

            if results.results:
                print(f"\nBot (found {len(results.results)} results in {results.execution_time_ms:.0f}ms):\n")

                for idx, result in enumerate(results.results, 1):
                    print_result(result, idx)

                if results.results[0].relevance_score < 0.3:
                    print("  [Note: Low confidence. For more help, contact support@company.com]\n")
            else:
                print("\nBot: Sorry, I couldn't find relevant information. Contact support.\n")

        except Exception as e:
            print(f"\nBot: Error processing query: {e}\n")

def main():
    """Main entry point."""
    print_header("EXERCISE 2: CLI Support Bot")

    # Create client
    client = RAGClient()
    print("[OK] RAG client initialized\n")

    # Demo: Load FAQs for two teams
    print("[DEMO] Loading sample FAQs...")
    load_sample_faqs("support-team", client)
    load_sample_faqs("sales-team", client)

    # Show menu
    print("\nChoose a team:")
    print("  1. Support Team (general support FAQs)")
    print("  2. Sales Team (sales FAQs)")
    print("  3. Exit")

    while True:
        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            interactive_mode(client, "support-team")
            break
        elif choice == "2":
            interactive_mode(client, "sales-team")
            break
        elif choice == "3":
            print("[Goodbye!]")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
