# Woxsen University RAG Support System

A full-stack RAG (Retrieval-Augmented Generation) chatbot for student support,
using ChromaDB, LangChain, Claude API, and sentence-transformers.

## Project Structure

```
woxsen-rag/
├── backend/
│   ├── main.py              # FastAPI server (REST API)
│   ├── rag_engine.py        # Core RAG logic (ChromaDB + Claude)
│   ├── knowledge_base.py    # Direct answer rules (Layer 1)
│   └── ingest.py            # Document ingestion script
├── frontend/
│   └── chatbot_widget.html  # Drop-in widget for Woxsen panels
├── data/
│   └── sample_docs/         # Put university PDFs/docs here
├── scripts/
│   └── seed_knowledge.py    # Seeds initial knowledge base
├── requirements.txt
└── .env.example
```

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Ingest your university documents
```bash
python backend/ingest.py --docs-dir data/sample_docs/
```

### 4. Start the backend server
```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. Embed the widget in your HTML panels
Add to any Woxsen HTML panel (index.html, department_portal.html, etc.):
```html
<script src="http://localhost:8000/static/widget.js"></script>
```

## How It Works

```
Student Query
     │
     ▼
┌─────────────────────────────┐
│   Layer 1: Direct Answers   │  ← Instant, no API cost
│   (ID card, fee, hostel...) │    Returns structured steps
└────────────┬────────────────┘
             │ No match?
             ▼
┌─────────────────────────────┐
│   Layer 2: RAG Pipeline     │
│                             │
│  Query → Embedding          │
│       → ChromaDB Search     │  ← Find relevant docs
│       → Top-K Chunks        │
│       → Claude API          │  ← Generate grounded answer
│       → Cited Response      │
└─────────────────────────────┘
```

## API Endpoints

| Method | Endpoint         | Description                        |
|--------|------------------|------------------------------------|
| POST   | /chat            | Main chat endpoint                 |
| POST   | /ingest          | Upload & ingest a document         |
| GET    | /health          | Health check                       |
| GET    | /docs-list       | List ingested documents            |
| DELETE | /docs/{doc_id}   | Remove a document                  |

## Configuration (.env)

```
ANTHROPIC_API_KEY=sk-ant-...
CHROMA_PERSIST_DIR=./chroma_db
EMBED_MODEL=all-MiniLM-L6-v2
TOP_K_RESULTS=5
CLAUDE_MODEL=claude-sonnet-4-20250514
```
