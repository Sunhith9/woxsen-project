"""
models.py
=========
Shared Pydantic request/response models for the Woxsen RAG backend.
"""

from typing import Optional
from pydantic import BaseModel


class RagQuery(BaseModel):
    query: str
    context: Optional[str] = None
    conversation_id: Optional[str] = None
