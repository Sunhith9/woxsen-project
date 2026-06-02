# Woxsen University Platform

A full-stack university management system consisting of:

| Portal | File | Access |
|---|---|---|
| **Student Portal** | `index.html` | Students |
| **Admin Panel** | `Woxsen_Admin_Panel.html` | Registrar / Admin |
| **Department Portal** | `department_portal.html` | HODs / Faculty |
| **Landing Page** | `landing.html` | Public |
| **RAG Chatbot Backend** | `woxsen-rag/` | Internal API |

---

## 🚀 Running Locally (Development)

### 1 – Prerequisites

- Python 3.11+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for full stack)

### 2 – Quick start (Python only, no Docker)

```bash
# In the woxsen-rag directory
cd woxsen-rag
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Copy and fill in environment variables
copy .env.example .env        # then edit .env with real keys

# Start the server
uvicorn backend.main:app --reload --port 8000
```

The API will be at **http://localhost:8000**. Open any HTML portal in your browser or use VS Code Live Server.

---

## 🐳 Running the Full Stack (Docker Compose)

```bash
# From the project root
cp woxsen-rag/.env.example woxsen-rag/.env   # fill in real keys

# Start all services (API + Redis + Nginx + Prometheus + Grafana)
docker-compose up --build

# Or scale to 4 API replicas:
docker-compose up --build --scale api=4
```

| Service | URL |
|---|---|
| Student Portal | http://localhost/student |
| Admin Panel | http://localhost/admin |
| Department Portal | http://localhost/department |
| API (direct) | http://localhost:8000/docs |
| Grafana | http://localhost:3000 (user: `admin`) |
| Prometheus | http://localhost:9090 (internal) |

---

## 📦 Architecture

```
                 ┌─────────────────────┐
  Browser ──────▶│   NGINX (port 80)   │
                 │  + Static portals   │
                 └────────┬────────────┘
                          │ /api/* /chat /health
                          ▼
                 ┌─────────────────────┐
                 │  FastAPI  (×N)      │◀── Gunicorn + UvicornWorker
                 │  backend/main.py    │
                 └──┬──────────┬───────┘
                    │          │
              ┌─────▼──┐  ┌────▼────┐
              │ Supabase│  │  Redis  │  ← query cache + session
              │  (DB)   │  │        │
              └─────────┘  └─────────┘
                    │
              ┌─────▼──────────────────┐
              │  RAG Engine            │
              │  (Gemini REST API)     │
              │  + SentenceTransformers│
              └────────────────────────┘
```

---

## 📊 Monitoring

- **Prometheus** scrapes `/metrics` every 10 s
- **Grafana** dashboards at `http://localhost:3000`
- **Alerts** fire for: 5xx rate >2%, p95 latency >1s, API down, Redis memory >80%

---

## 🧪 Load Testing

```bash
# Install k6: https://k6.io/docs/getting-started/installation/

# Smoke test (100 VUs, 30 s)
k6 run --vus 100 --duration 30s load-test.js

# Full load test (up to 600 VUs – simulates 6 000 active users)
k6 run load-test.js

# Target a specific environment
k6 run -e BASE_URL=https://your-domain.com load-test.js
```

### SLO Targets

| Metric | Target |
|---|---|
| p95 request latency | < 2 s |
| p95 RAG query latency | < 3 s |
| Error rate | < 2% |

---

## 🔐 Security

- All API keys and secrets stored in `.env` (never committed)
- JWT-based session authentication (8-hour token expiry)
- Rate limiting: 30 req/s general, 5 req/min on `/api/login`
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`
- Non-root Docker user

---

## 📁 Project Structure

```
woxsen/
├── index.html                    # Student Portal
├── Woxsen_Admin_Panel.html       # Admin Panel
├── department_portal.html        # Department Portal
├── landing.html                  # Public Landing Page
├── docker-compose.yml            # Full stack orchestration
├── load-test.js                  # k6 load test
├── nginx/
│   └── nginx.conf                # Reverse proxy config
├── monitoring/
│   ├── prometheus.yml            # Metrics config
│   ├── alerts.yml                # Alert rules
│   └── grafana/provisioning/     # Auto-provisioned Grafana datasources
├── .github/workflows/ci.yml      # GitHub Actions CI/CD
└── woxsen-rag/
    ├── Dockerfile                # Multi-stage production image
    ├── requirements.txt
    ├── .env.example
    └── backend/
        ├── main.py               # FastAPI server
        ├── rag_engine.py         # Gemini-powered RAG pipeline
        ├── knowledge_base.py     # Layer 1 direct answers
        ├── redis_client.py       # Redis cache with in-memory fallback
        └── ingest.py             # Document ingestion
```

---

## 🔧 CI/CD (GitHub Actions)

1. **Test** – `pytest` on every PR
2. **Build** – Docker image pushed to GitHub Container Registry on merge to `main`
3. **Load Test** – k6 smoke test (100 VUs) validates the stack

Add these **GitHub Secrets**:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `GEMINI_API_KEY`
- `JWT_SECRET`
