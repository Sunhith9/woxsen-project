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
    WS   /ws                Real-time WebSocket (status updates & new grievance alerts)
    POST /api/v1/notify     Internal: broadcast a status change event

Run:
    uvicorn backend.main:app --reload --port 8000
"""

import os
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, List

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, WebSocket, WebSocketDisconnect
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

# Simple in-memory cache for the current session
query_cache = {}


# ── WebSocket Connection Manager ───────────────────────────────────────────────

class ConnectionManager:
    """
    Manages WebSocket connections.
    Each client connects with a role query param:
      - ws://localhost:8000/ws?student_id=XYZ  → student channel
      - ws://localhost:8000/ws?role=admin       → admin channel
    """

    def __init__(self):
        # student_id → list of WebSocket connections (same student may have multiple tabs)
        self.students: Dict[str, List[WebSocket]] = {}
        # admin connections
        self.admins: List[WebSocket] = []

    async def connect_student(self, ws: WebSocket, student_id: str):
        await ws.accept()
        self.students.setdefault(student_id, []).append(ws)
        logger.info(f"WS: student {student_id} connected ({len(self.students[student_id])} tabs)")

    async def connect_admin(self, ws: WebSocket):
        await ws.accept()
        self.admins.append(ws)
        logger.info(f"WS: admin connected ({len(self.admins)} admins online)")

    def disconnect(self, ws: WebSocket):
        # Remove from students
        for sid, conns in list(self.students.items()):
            if ws in conns:
                conns.remove(ws)
                if not conns:
                    del self.students[sid]
                logger.info(f"WS: student {sid} disconnected")
                return
        # Remove from admins
        if ws in self.admins:
            self.admins.remove(ws)
            logger.info("WS: admin disconnected")

    async def notify_student(self, student_id: str, payload: dict):
        """Send a JSON message to all tabs of a specific student."""
        conns = self.students.get(student_id, [])
        dead = []
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def notify_admins(self, payload: dict):
        """Broadcast a JSON message to all connected admins."""
        dead = []
        for ws in self.admins:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def broadcast_all(self, payload: dict):
        """Broadcast to every connected client (students + admins)."""
        for conns in self.students.values():
            for ws in conns:
                try:
                    await ws.send_json(payload)
                except Exception:
                    pass
        for ws in self.admins:
            try:
                await ws.send_json(payload)
            except Exception:
                pass


ws_manager = ConnectionManager()


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Woxsen University Support API",
    description="RAG-powered student support chatbot backend with real-time WebSocket updates",
    version="2.0.0"
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


# ── Request / Response models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: Optional[str] = None
    question: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    type: str           # "direct" | "rag" | "error"
    answer: Optional[str] = None
    title: Optional[str] = None
    steps: Optional[list] = None
    contact: Optional[str] = None
    fee: Optional[str] = None
    note: Optional[str] = None
    sources: Optional[list[str]] = None


class NotifyPayload(BaseModel):
    """Sent by frontend proxy calls to trigger real-time WS broadcast."""
    event: str                          # "status_change" | "new_grievance"
    student_id: Optional[str] = None    # target student (for status_change)
    grievance_id: Optional[str] = None
    status: Optional[str] = None
    student_name: Optional[str] = None  # for new_grievance alerts to admin
    category: Optional[str] = None


# ── WebSocket Endpoint ─────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, student_id: str = None, role: str = None):
    """
    Real-time WebSocket endpoint.

    Connect as student:  ws://localhost:8000/ws?student_id=USER123
    Connect as admin:    ws://localhost:8000/ws?role=admin
    """
    if student_id:
        await ws_manager.connect_student(ws, student_id)
        try:
            # Send a welcome ping so the client knows it's connected
            await ws.send_json({"event": "connected", "student_id": student_id})
            while True:
                # Keep the connection alive; client can send pings
                data = await ws.receive_text()
                if data == "ping":
                    await ws.send_text("pong")
        except WebSocketDisconnect:
            ws_manager.disconnect(ws)

    elif role == "admin":
        await ws_manager.connect_admin(ws)
        try:
            await ws.send_json({"event": "connected", "role": "admin"})
            while True:
                data = await ws.receive_text()
                if data == "ping":
                    await ws.send_text("pong")
        except WebSocketDisconnect:
            ws_manager.disconnect(ws)

    else:
        await ws.close(code=4001, reason="Missing student_id or role=admin param")


# ── Notify endpoint (called by frontend after Supabase mutations) ──────────────

@app.post("/api/v1/notify")
async def notify(payload: NotifyPayload):
    """
    The frontend calls this after updating a grievance in Supabase.
    We broadcast the event to relevant WebSocket clients.
    """
    if payload.event == "status_change" and payload.student_id:
        await ws_manager.notify_student(payload.student_id, {
            "event": "status_change",
            "grievance_id": payload.grievance_id,
            "status": payload.status,
            "category": payload.category,
        })
        # Also notify admins so their dashboard updates
        await ws_manager.notify_admins({
            "event": "status_change",
            "grievance_id": payload.grievance_id,
            "status": payload.status,
        })

    elif payload.event == "new_grievance":
        await ws_manager.notify_admins({
            "event": "new_grievance",
            "grievance_id": payload.grievance_id,
            "student_name": payload.student_name,
            "category": payload.category,
        })

    return {"ok": True}


# ── Health / Stats ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Woxsen Support API",
        "ws_students": sum(len(v) for v in ws_manager.students.values()),
        "ws_admins": len(ws_manager.admins),
    }


@app.get("/stats")
def stats():
    """Returns vector DB statistics — useful for admin dashboard."""
    return rag_engine.get_stats()


@app.get("/docs-list")
def docs_list():
    """List all ingested document sources."""
    s = rag_engine.get_stats()
    return {"sources": s["sources"], "total_chunks": s["total_chunks"]}


# ── Chat ───────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Flow:
        1. Try Layer 1 (direct keyword match) → instant answer
        2. If no match → Layer 2 RAG pipeline (Gemini)
    """
    msg = request.message or request.question
    if not msg or not msg.strip():
        raise HTTPException(status_code=400, detail="Message or question cannot be empty")

    query = msg.strip()
    logger.info(f"Chat query: {query[:80]}")

    # Layer 1
    direct_match = find_direct_answer(query)
    if direct_match:
        logger.info(f"Layer 1 match: {query[:80]}")
        ans = direct_answer_to_dict(direct_match)
        query_cache[query] = ans
        return ChatResponse(**ans)

    # Layer 2 — RAG
    logger.info("Invoking RAG pipeline")
    result = await rag_engine.query(query, conversation_id=request.conversation_id)

    return ChatResponse(
        type=result["type"],
        answer=result["answer"],
        sources=result.get("sources", [])
    )


@app.post("/api/rag/query", response_model=ChatResponse)
async def api_rag_query(request: RagQuery):
    """RAG query endpoint with backend caching."""
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query_str = request.query.strip().lower()
    session_id = request.conversation_id or "default"
    cache_key = f"{session_id}_{query_str}"

    if cache_key in query_cache:
        logger.info(f"Cache hit: {query_str[:80]}")
        return ChatResponse(**query_cache[cache_key])

    direct_match = find_direct_answer(query_str)
    if direct_match:
        ans = direct_answer_to_dict(direct_match)
        query_cache[cache_key] = ans
        return ChatResponse(**ans)

    full_query = f"Context: {request.context}\nQuestion: {query_str}" if request.context else query_str
    result = await rag_engine.query(full_query, conversation_id=request.conversation_id)

    ans = {"type": result["type"], "answer": result["answer"], "sources": result.get("sources", [])}
    query_cache[cache_key] = ans
    return ChatResponse(**ans)


# ── Document Ingestion ─────────────────────────────────────────────────────────

@app.post("/ingest")
async def ingest_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload and ingest a document (PDF, DOCX, TXT) into ChromaDB."""
    ALLOWED_TYPES = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "text/plain": ".txt",
        "text/markdown": ".md",
    }
    ext = ALLOWED_TYPES.get(file.content_type)
    if not ext:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".pdf", ".docx", ".txt", ".md"}:
            raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: PDF, DOCX, TXT, MD")
        ext = suffix

    content = await file.read()
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp.write(content)
    tmp.close()

    def do_ingest(tmp_path: str, original_name: str):
        try:
            from backend.ingest import load_file
            docs = load_file(Path(tmp_path))
            for doc in docs:
                doc.metadata["source"] = original_name
            count = rag_engine.ingest_documents(docs)
            logger.info(f"Ingest complete: {count} chunks from {original_name}")
        finally:
            os.unlink(tmp_path)

    background_tasks.add_task(do_ingest, tmp.name, file.filename or "uploaded_doc")
    return {"status": "ingesting", "filename": file.filename, "message": "Document is being processed."}


@app.delete("/docs/{source_name}")
def delete_source(source_name: str):
    deleted = rag_engine.delete_source(source_name)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Source '{source_name}' not found")
    return {"deleted_chunks": deleted, "source": source_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8000")), reload=True)
