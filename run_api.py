"""
Start RAG Framework API server.

Usage:
    python run_api.py

Then visit:
    - API docs: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
    - API endpoint: http://localhost:8000/api/v1/...
"""

import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("RAG Framework API Server")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Starting server on http://localhost:8000")
    logger.info("")
    logger.info("API Documentation:")
    logger.info("  - Swagger UI:  http://localhost:8000/docs")
    logger.info("  - ReDoc:       http://localhost:8000/redoc")
    logger.info("")
    logger.info("Endpoints:")
    logger.info("  - POST   /api/v1/retrieve          - Main retrieval")
    logger.info("  - POST   /api/v1/retrieve-expanded - Multi-pass retrieval")
    logger.info("  - POST   /api/v1/ingest            - Ingest FAQs")
    logger.info("  - GET    /api/v1/health            - Health check")
    logger.info("  - GET    /api/v1/stats/{team_id}   - Team statistics")
    logger.info("")
    logger.info("Press Ctrl+C to stop the server")
    logger.info("=" * 70)

    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
