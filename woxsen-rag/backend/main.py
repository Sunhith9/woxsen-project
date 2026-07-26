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



# ── Multi-Language Content Moderation Endpoint ──────────────────────────────────

class ModerationRequest(BaseModel):
    text: str

PROFANITY_PATTERNS = [
    # English Swear Words & Leetspeak
    r"\b(f[u*a@]c?k|f[u*a@]ck[i1a]ng?|f[u*a@]ck[e3]r|f[u*a@]cked|fck|f\*ck|f\*\*k)\b",
    r"\b(sh[i1!*]t|sh[i1!*]tt[i1y]ng?|sh[i1!*]tty|sh\*t)\b",
    r"\b(b[i1!*]tch|b[i1!*]tch[e3]s|b[i1!*]tchy|b\*tch)\b",
    r"\b(a[s$][s$]h[o0]l[e3]|a[s$][s$]|a\*\*hole|arsehole)\b",
    r"\b(b[a*]st[a*]rd|b[a*]st[a*]rds|b\*stard)\b",
    r"\b(d[i1!*]ck|d[i1!*]ckhead|d\*\*k)\b",
    r"\b(p[u*]ssy|c[u*]nt|c[u*]nts|c\*nt)\b",
    r"\b(m[o0]th[e3]rf[u*]ck[e3]r|m[o0]th[e3]rf[u*]ck[i1]ng|mfkr)\b",
    r"\b(c[o0]ck|c[o0]cksuck[e3]r)\b",
    r"\b(d[o0]uch[e3]|d[o0]uch[e3]b[a*]g)\b",
    r"\b(bullsh[i1!*]t)\b",
    r"\b(pr[i1]ck|tw[a*]t|w[a*]nk[e3]r|sl[u*]t|wh[o0]r[e3])\b",

    # Transliterated Indian Profanities & Slurs (Romanized)
    r"\b(chut[i1y]a|chut[i1y]e|chut|ch\*\*iya)\b",
    r"\b(bh[e3]nch[o0]d|b[e3]nch[o0]d|bc|b\*nchod)\b",
    r"\b(m[a*]d[a*]rch[o0]d|mc|m\*darchod)\b",
    r"\b(g[a*]and|gand|gandu)\b",
    r"\b(h[a*]r[a*]m[i1]|h[a*]r[a*]mz[a*]d[a*e3])\b",
    r"\b(k[a*]m[i1]n[a*e3])\b",
    r"\b(bh[o0]sd[i1]k[e3]|bh[o0]sd[i1]|bh[o0]sd[a*])\b",
    r"\b(s[a*]al[a*e3]|s[a*]le)\b",
    r"\b(kutt[a*e3]|kutt[i1])\b",
    r"\b(r[a*]nd[i1])\b",
    r"\b(d[e3]ng[u0]|d[e3]ng[a*]|d[e3]ng[e3])\b",
    r"\b(m[o0]dd[a*]|m[o0]dda)\b",
    r"\b(l[a*]nj[a*]|l[a*]nj[o0]dk[a*])\b",
    r"\b(p[u0]k[u0]|p[o00]k[u0])\b",
    r"\b(g[u0]dh[a*]|g[u0]da)\b",
    r"\b(p[u0]nd[a*i1]|pundai|othaa|koothi|thevidya)\b",

    # Native Indic Scripts (Hindi, Telugu, Tamil, Kannada, Malayalam, Bengali)
    r"(चूतिया|चूत|भैनचोद|बहनचोद|मादरचोद|गांड|गांडू|हरामी|हरामजादा|कमीना|भोसडीके|साला|साले|कुत्ता|कुत्ते|रंडी)",
    r"(డెంగు|దెంగు|మొడ్డ|లంజ|లంజకొడుకా|పూకు|పుకు|గుద్ద)",
    r"(புண்டை|ஒத்தா|கூதி|தேவடியா)",
    r"(ഹുച്ചാ|സുളെ|മയിര്|പൂറി)",

    # Insults directed at people or departments
    r"\b(idiot|idiots|idiotic|moron|morons|moronic)\b",
    r"\b(stupid|dumbass|dumb|retard|retarded)\b",
    r"\b(loser|scammer|fool|fools|foolish|jackass)\b",
    r"\b(corrupt bastard|useless fools|bloody|scum)\b",

    # Threats and violent language
    r"\b(kill|beat up|break your face|stab|shoot|punch|destroy you|harm you|physically attack)\b",
    r"\b(die motherfucker|gonna get you|threaten)\b",

    # Sexual profanity & harassment terms
    r"\b(suck my|blowjob|handjob|nudes|naked photos|pornography)\b"
]c?k|f[u*a@]ck[i1a]ng?|f[u*a@]ck[e3]r|f[u*a@]cked|fck|f\*ck|f\*\*k)\b",
    r"\b(sh[i1!*]t|sh[i1!*]tt[i1y]ng?|sh[i1!*]tty|sh\*t)\b",
    r"\b(b[i1!*]tch|b[i1!*]tch[e3]s|b[i1!*]tchy|b\*tch)\b",
    r"\b(a[s$][s$]h[o0]l[e3]|a[s$][s$]|a\*\*hole|arsehole)\b",
    r"\b(b[a*]st[a*]rd|b[a*]st[a*]rds|b\*stard)\b",
    r"\b(d[i1!*]ck|d[i1!*]ckhead|d\*\*k)\b",
    r"\b(p[u*]ssy|c[u*]nt|c[u*]nts|c\*nt)\b",
    r"\b(m[o0]th[e3]rf[u*]ck[e3]r|m[o0]th[e3]rf[u*]ck[i1]ng|mfkr)\b",
    r"\b(c[o0]ck|c[o0]cksuck[e3]r)\b",
    r"\b(d[o0]uch[e3]|d[o0]uch[e3]b[a*]g)\b",
    r"\b(bullsh[i1!*]t)\b",
    r"\b(pr[i1]ck|tw[a*]t|w[a*]nk[e3]r|sl[u*]t|wh[o0]r[e3])\b",

    # Hindi / North Indian Profanities & Slurs (Romanized & Devanagari)
    r"\b(chut[i1y]a|chut[i1y]e|chut|ch\*\*iya|चूतिया|चूत)\b",
    r"\b(bh[e3]nch[o0]d|b[e3]nch[o0]d|bc|b\*nchod|भैनचोद|बहनचोद)\b",
    r"\b(m[a*]d[a*]rch[o0]d|mc|m\*darchod|मादरचोद)\b",
    r"\b(g[a*]and|gand|gandu|गांड|गांडू)\b",
    r"\b(h[a*]r[a*]m[i1]|h[a*]r[a*]mz[a*]d[a*e3]|हरामी|हरामजादा)\b",
    r"\b(k[a*]m[i1]n[a*e3]|कमीना)\b",
    r"\b(bh[o0]sd[i1]k[e3]|bh[o0]sd[i1]|bh[o0]sd[a*]|भोसडीके)\b",
    r"\b(s[a*]al[a*e3]|s[a*]le|साला|साले)\b",
    r"\b(kutt[a*e3]|kutt[i1]|कुत्ता|कुत्ते)\b",
    r"\b(r[a*]nd[i1]|रंडी)\b",

    # Telugu Profanities & Slurs (Romanized & Telugu script)
    r"\b(d[e3]ng[u0]|d[e3]ng[a*]|d[e3]ng[e3]|డెంగు|దెంగు)\b",
    r"\b(m[o0]dd[a*]|m[o0]dda|మొడ్డ)\b",
    r"\b(l[a*]nj[a*]|l[a*]nj[o0]dk[a*]|లంజ|లంజకొడుకా)\b",
    r"\b(p[u0]k[u0]|p[o00]k[u0]|పూకు|పుకు)\b",
    r"\b(g[u0]dh[a*]|g[u0]da|గుద్ద)\b",
    r"\b(b[o0]l[i1]li|m[a*]d[a*]ch[o0]d)\b",

    # Tamil Profanities & Slurs (Romanized & Tamil script)
    r"\b(p[u0]nd[a*i1]|pundai|புண்டை)\b",
    r"\b(o[t*]ha|othaa|ஒத்தா)\b",
    r"\b(kooth[i1]|koothi|கூதி)\b",
    r"\b(thevid[i1]y[a*]|தேவடியா)\b",

    # Kannada Profanities & Slurs
    r"\b(h[u0]ch[a*]|huchnayi|s[u0]le|sulemaga)\b",

    # Malayalam Profanities & Slurs
    r"\b(m[a*]y[i1]r|myre|p[u0]ri|pandi)\b",

    # Marathi / Gujarati / Bengali Profanities
    r"\b(zavadya|gandya|bhadwa|bhadwe|khanki|chod)\b",

    # Insults directed at people or departments (Multi-language)
    r"\b(idiot|idiots|idiotic|moron|morons|moronic)\b",
    r"\b(stupid|dumbass|dumb|retard|retarded)\b",
    r"\b(loser|scammer|fool|fools|foolish|jackass)\b",
    r"\b(corrupt bastard|useless fools|bloody|scum)\b",

    # Threats and violent language
    r"\b(kill|beat up|break your face|stab|shoot|punch|destroy you|harm you|physically attack)\b",
    r"\b(die motherfucker|gonna get you|threaten)\b",

    # Sexual profanity & harassment terms
    r"\b(suck my|blowjob|handjob|nudes|naked photos|pornography)\b"
]

@app.post("/api/v1/moderate")
def moderate_text_endpoint(payload: ModerationRequest):
    """
    Multi-language content moderation filter for grievance submission text.
    Uses AI LLM (Gemini) if available, with robust multi-language pattern matching fallback.
    Returns {"allowed": bool, "message": str}
    """
    clean_text = (payload.text or "").strip()
    block_msg = "Your grievance could not be submitted because it contains language that is not appropriate for this platform. Please remove any offensive, abusive, or unprofessional words and resubmit your complaint using respectful language."

    if not clean_text:
        return {"allowed": True, "message": ""}

    # 1. Try Gemini AI LLM Moderation for 100% multilingual & context accuracy
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            sys_prompt = (
                "You are a strict content moderation filter for a university grievance submission portal.\n"
                "Task: Review the grievance text submitted in ANY language (English, Hindi, Telugu, Tamil, Kannada, Marathi, Bengali, Spanish, French, etc., in native or transliterated script).\n"
                "Check for: profanity, swear words, slurs, abusive language, personal insults directed at a person or department, threats of violence, or sexual content.\n"
                "RULES:\n"
                "- Flag ONLY actual offensive/unprofessional language (swear words, insults, slurs, threats).\n"
                "- Do NOT flag strong but respectful expressions of frustration or dissatisfaction (e.g. 'this is unacceptable', 'I am extremely disappointed', 'this service is terrible') — these are valid and MUST be allowed.\n"
                "- Output ONLY valid JSON: {\"allowed\": true, \"message\": \"\"} or {\"allowed\": false, \"message\": \"Your grievance could not be submitted because it contains language that is not appropriate for this platform. Please remove any offensive, abusive, or unprofessional words and resubmit your complaint using respectful language.\"}\n"
                "No extra text."
            )
            req_body = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{sys_prompt}\n\nGRIEVANCE TEXT TO REVIEW:\n\"{clean_text}\""}]}
                ],
                "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"}
            }
            res = requests.post(url, json=req_body, timeout=5)
            if res.status_code == 200:
                res_data = res.json()
                res_text = res_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                parsed = json.loads(res_text)
                if isinstance(parsed, dict) and "allowed" in parsed:
                    return {
                        "allowed": bool(parsed.get("allowed")),
                        "message": block_msg if not parsed.get("allowed") else ""
                    }
        except Exception as e:
            logger.warning(f"Gemini moderation fallback to regex: {e}")

    # 2. Comprehensive Multi-Language Pattern Matching Fallback
    lower_text = clean_text.lower()
    for pat in PROFANITY_PATTERNS:
        if re.search(pat, lower_text, re.IGNORECASE):
            return {
                "allowed": False,
                "message": block_msg
            }

    return {
        "allowed": True,
        "message": ""
    }
