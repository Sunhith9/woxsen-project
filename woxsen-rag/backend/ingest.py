"""
ingest.py
=========
Ingest university documents (PDFs, DOCX, TXT) into ChromaDB.

Usage:
    # Ingest all documents in a folder
    python backend/ingest.py --docs-dir data/sample_docs/

    # Ingest a single file
    python backend/ingest.py --file data/student_handbook.pdf

    # Also seeds direct knowledge base content as documents
    python backend/ingest.py --seed-kb
"""

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.documents import Document
from backend.rag_engine import RAGEngine


def load_pdf(file_path: Path) -> list[Document]:
    from langchain_community.document_loaders import PyPDFLoader
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = file_path.name
        doc.metadata["file_type"] = "pdf"
    return docs


def load_docx(file_path: Path) -> list[Document]:
    from langchain_community.document_loaders import Docx2txtLoader
    loader = Docx2txtLoader(str(file_path))
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = file_path.name
        doc.metadata["file_type"] = "docx"
    return docs


def load_txt(file_path: Path) -> list[Document]:
    from langchain_community.document_loaders import TextLoader
    loader = TextLoader(str(file_path), encoding="utf-8")
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = file_path.name
        doc.metadata["file_type"] = "txt"
    return docs


LOADERS = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".doc": load_docx,
    ".txt": load_txt,
    ".md": load_txt,
}


def load_file(file_path: Path) -> list[Document]:
    ext = file_path.suffix.lower()
    loader_fn = LOADERS.get(ext)
    if not loader_fn:
        logger.warning(f"Unsupported file type: {ext} — skipping {file_path.name}")
        return []
    try:
        docs = loader_fn(file_path)
        logger.info(f"Loaded {len(docs)} pages from {file_path.name}")
        return docs
    except Exception as e:
        logger.error(f"Failed to load {file_path.name}: {e}")
        return []


def seed_knowledge_base(engine: RAGEngine) -> int:
    """
    Convert the direct knowledge base rules into RAG documents.
    This ensures even RAG queries can find common issue info.
    """
    from backend.knowledge_base import KNOWLEDGE_BASE

    docs = []
    for item in KNOWLEDGE_BASE:
        steps_text = "\n".join(
            f"Step {i+1}: Go to {s.place}. {s.detail}"
            + (f" Timing: {s.timing}" if s.timing else "")
            for i, s in enumerate(item.steps)
        )
        content = f"""
Issue: {item.title}

Process:
{steps_text}

Contact: {item.contact}
{f"Fee: {item.fee}" if item.fee else ""}
{f"Note: {item.note}" if item.note else ""}
        """.strip()

        docs.append(Document(
            page_content=content,
            metadata={"source": "Woxsen_Support_KB", "issue_id": item.id}
        ))

    count = engine.ingest_documents(docs)
    logger.info(f"Seeded {count} KB chunks from {len(docs)} issues")
    return count


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into Woxsen RAG system")
    parser.add_argument("--docs-dir", type=str, help="Directory containing documents to ingest")
    parser.add_argument("--file", type=str, help="Single file to ingest")
    parser.add_argument("--seed-kb", action="store_true", help="Seed from direct knowledge base")
    args = parser.parse_args()

    engine = RAGEngine()
    total_chunks = 0

    if args.seed_kb:
        logger.info("Seeding from direct knowledge base...")
        total_chunks += seed_knowledge_base(engine)

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            sys.exit(1)
        docs = load_file(file_path)
        total_chunks += engine.ingest_documents(docs)

    if args.docs_dir:
        docs_dir = Path(args.docs_dir)
        if not docs_dir.exists():
            logger.error(f"Directory not found: {docs_dir}")
            sys.exit(1)

        all_docs = []
        for ext in LOADERS:
            for file_path in docs_dir.glob(f"**/*{ext}"):
                all_docs.extend(load_file(file_path))

        if all_docs:
            total_chunks += engine.ingest_documents(all_docs)
        else:
            logger.warning("No supported documents found in directory")

    if total_chunks > 0:
        stats = engine.get_stats()
        logger.info(f"✅ Ingestion complete!")
        logger.info(f"   Total chunks in DB: {stats['total_chunks']}")
        logger.info(f"   Sources: {', '.join(stats['sources'])}")
    else:
        logger.warning("No chunks were ingested. Check your file paths and formats.")


if __name__ == "__main__":
    main()
