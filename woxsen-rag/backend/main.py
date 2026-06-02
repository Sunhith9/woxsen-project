"""
main.py
=======
FastAPI server for Woxsen RAG Support System.

Endpoints:
    POST /chat              Main chat (Layer 1 → Layer 2 fallback)
    POST /ingest            Upload & ingest a document
    GET  /health            Health check
    GET  /stats             Vector DB stats
    GET  /docs-list         List ingested sources
    DELETE /docs/{source}   Remove a source document

Run:
    uvicorn backend.main:app --reload --port 8000
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from backend.knowledge_base import find_direct_answer, direct_answer_to_dict
from backend.rag_engine import RAGEngine
from backend.models import RagQuery
import json

# Simple in-memory cache for the current session
query_cache = {}


app = FastAPI(
    title="Woxsen University Support API",
    description="RAG-powered student support chatbot backend",
    version="1.0.0"
)

# CORS — allow your HTML panels to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single shared RAG engine instance
rag_engine = RAGEngine()


# ── Request / Response models ──────────────────

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None   # For future multi-turn tracking


class ChatResponse(BaseModel):
    type: str           # "direct" | "rag" | "error"
    answer: Optional[str] = None
    title: Optional[str] = None
    steps: Optional[list] = None
    contact: Optional[str] = None
    fee: Optional[str] = None
    note: Optional[str] = None
    sources: Optional[list[str]] = None


# ── Routes ────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "Woxsen Support API"}


@app.get("/stats")
def stats():
    """Returns vector DB statistics — useful for admin dashboard."""
    return rag_engine.get_stats()


@app.get("/docs-list")
def docs_list():
    """List all ingested document sources."""
    s = rag_engine.get_stats()
    return {"sources": s["sources"], "total_chunks": s["total_chunks"]}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    
    Flow:
        1. Try Layer 1 (direct keyword match) → instant answer
        2. If no match → Layer 2 RAG pipeline (ChromaDB + Claude)
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    query = request.message.strip()
    logger.info(f"Chat query: {query[:80]}")

    # Try Layer 1 (direct keyword match) -> instant structured answer
    direct_match = find_direct_answer(query)
    if direct_match:
        logger.info(f"Layer 1 match for query: {query[:80]}")
        ans = direct_answer_to_dict(direct_match)
        query_cache[query] = ans
        return ChatResponse(**ans)

    # Pass all other queries directly to the RAG pipeline so Gemini can answer
    logger.info("Invoking RAG pipeline")
    result = await rag_engine.query(query, conversation_id=request.conversation_id)

    return ChatResponse(
        type=result["type"],
        answer=result["answer"],
        sources=result.get("sources", [])
    )


@app.post("/api/rag/query", response_model=ChatResponse)
async def api_rag_query(request: RagQuery):
    """
    RAG query endpoint with backend caching.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query_str = request.query.strip().lower()
    session_id = request.conversation_id or "default"
    cache_key = f"{session_id}_{query_str}"
    
    # Check cache first to answer instantly for future students
    if cache_key in query_cache:
        logger.info(f"Cache hit for query: {query_str[:80]}")
        return ChatResponse(**query_cache[cache_key])

    # Try Layer 1 (direct keyword match) -> instant structured answer
    direct_match = find_direct_answer(query_str)
    if direct_match:
        logger.info(f"Layer 1 match for query: {query_str[:80]}")
        ans = direct_answer_to_dict(direct_match)
        query_cache[cache_key] = ans
        return ChatResponse(**ans)

    # Pass all other queries directly to the RAG pipeline so Gemini can answer
    logger.info("Invoking RAG pipeline")
    if request.context:
        full_query = f"Context: {request.context}\nQuestion: {query_str}"
    else:
        full_query = query_str
        
    result = await rag_engine.query(full_query, conversation_id=request.conversation_id)
    
    ans = {
        "type": result["type"],
        "answer": result["answer"],
        "sources": result.get("sources", [])
    }
    
    # Save to memory cache
    query_cache[cache_key] = ans

    return ChatResponse(**ans)


@app.post("/ingest")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload and ingest a document (PDF, DOCX, TXT) into ChromaDB.
    Ingestion runs in the background.
    """
    ALLOWED_TYPES = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "text/plain": ".txt",
        "text/markdown": ".md",
    }

    ext = ALLOWED_TYPES.get(file.content_type)
    if not ext:
        # Try by filename
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".pdf", ".docx", ".txt", ".md"}:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: PDF, DOCX, TXT, MD"
            )
        ext = suffix

    # Save to temp file
    content = await file.read()
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp.write(content)
    tmp.close()

    def do_ingest(tmp_path: str, original_name: str):
        try:
            from backend.ingest import load_file
            from langchain_core.documents import Document

            docs = load_file(Path(tmp_path))
            for doc in docs:
                doc.metadata["source"] = original_name

            count = rag_engine.ingest_documents(docs)
            logger.info(f"Background ingest complete: {count} chunks from {original_name}")
        finally:
            os.unlink(tmp_path)

    background_tasks.add_task(do_ingest, tmp.name, file.filename or "uploaded_doc")

    return {
        "status": "ingesting",
        "filename": file.filename,
        "message": "Document is being processed and will be available shortly."
    }


@app.delete("/docs/{source_name}")
def delete_source(source_name: str):
    """Remove all chunks from a specific source document."""
    deleted = rag_engine.delete_source(source_name)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Source '{source_name}' not found")
    return {"deleted_chunks": deleted, "source": source_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )
