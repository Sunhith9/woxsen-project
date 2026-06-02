@echo off
echo Starting Woxsen RAG Backend Server...
cd /d "c:\class notes\SEM - IV\projects\woxsen\woxsen-rag"
python -m uvicorn backend.main:app --reload --port 8000
pause
