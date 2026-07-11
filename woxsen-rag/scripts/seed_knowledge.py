"""
seed_knowledge.py
=================
Quick-start script: seeds the vector DB from both:
  1. The direct knowledge base rules (converted to documents)
  2. Any .txt/.pdf files in data/sample_docs/

Run:
    python scripts/seed_knowledge.py
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Add root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag_engine import RAGEngine
from backend.ingest import seed_knowledge_base, load_file

def main():
    logger.info("🚀 Starting Woxsen RAG Knowledge Base Seeding")
    engine = RAGEngine()

    # Step 1: Seed from direct KB rules
    logger.info("\n📌 Step 1: Seeding from Direct Knowledge Base rules...")
    count = seed_knowledge_base(engine)
    logger.info(f"   Added {count} chunks from KB rules")

    # Step 2: Ingest sample documents
    docs_dir = Path(__file__).parent.parent / "data" / "sample_docs"
    if docs_dir.exists():
        logger.info(f"\n📄 Step 2: Ingesting documents from {docs_dir}...")
        all_docs = []
        for ext in [".txt", ".md", ".pdf", ".docx"]:
            for f in docs_dir.glob(f"*{ext}"):
                all_docs.extend(load_file(f))

        if all_docs:
            count2 = engine.ingest_documents(all_docs)
            logger.info(f"   Added {count2} chunks from {len(all_docs)} document pages")
        else:
            logger.info("   No additional documents found")

    # Final stats
    stats = engine.get_stats()
    logger.info(f"\n✅ Seeding Complete!")
    logger.info(f"   Total chunks in ChromaDB: {stats['total_chunks']}")
    sources = [s.get("source", s.get("id", str(s))) if isinstance(s, dict) else str(s) for s in stats.get("sources", [])]
    logger.info(f"   Sources: {', '.join(sources) or 'none'}")
    logger.info(f"\n▶ Now start the server: uvicorn backend.main:app --reload --port 8000")

if __name__ == "__main__":
    main()
