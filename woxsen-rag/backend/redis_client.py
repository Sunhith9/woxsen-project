"""
redis_client.py
===============
Optional Redis-backed cache with transparent in-memory fallback.
If REDIS_URL is not set or Redis is unreachable the cache silently
falls back to a plain dict so the application keeps working.
"""

import os
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    import redis  # type: ignore
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False


class RedisCache:
    """
    Thin wrapper around Redis with an in-memory fallback.

    Usage::

        cache = RedisCache()
        cache.set("key", {"answer": "..."}, ttl=3600)
        value = cache.get("key")   # returns dict or None
    """

    def __init__(self, ttl: int = 3600) -> None:
        self.default_ttl = ttl
        self._client: Optional[Any] = None
        self._memory: dict = {}   # fallback

        redis_url = os.getenv("REDIS_URL", "")
        if _REDIS_AVAILABLE and redis_url:
            try:
                self._client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
                self._client.ping()
                logger.info(f"Redis cache connected: {redis_url}")
            except Exception as exc:
                logger.warning(f"Redis unavailable ({exc}); using in-memory fallback.")
                self._client = None
        else:
            logger.info("REDIS_URL not set or redis package missing; using in-memory cache.")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[dict]:
        """Return cached value for *key* or ``None`` if missing/expired."""
        if self._client:
            try:
                raw = self._client.get(key)
                if raw:
                    return json.loads(raw)
            except Exception as exc:
                logger.warning(f"Redis GET error: {exc}")
        return self._memory.get(key)

    def set(self, key: str, value: dict, ttl: Optional[int] = None) -> None:
        """Store *value* under *key* with an optional TTL (seconds)."""
        ttl = ttl if ttl is not None else self.default_ttl
        if self._client:
            try:
                self._client.setex(key, ttl, json.dumps(value))
                return
            except Exception as exc:
                logger.warning(f"Redis SET error: {exc}")
        self._memory[key] = value

    def delete(self, key: str) -> None:
        """Remove *key* from the cache."""
        if self._client:
            try:
                self._client.delete(key)
                return
            except Exception as exc:
                logger.warning(f"Redis DELETE error: {exc}")
        self._memory.pop(key, None)

    def flush(self) -> None:
        """Clear all cached values (use with care)."""
        if self._client:
            try:
                self._client.flushdb()
                return
            except Exception as exc:
                logger.warning(f"Redis FLUSH error: {exc}")
        self._memory.clear()

    def ping(self) -> bool:
        """Return True if the underlying Redis connection is healthy."""
        if self._client:
            try:
                return bool(self._client.ping())
            except Exception:
                return False
        return False  # in-memory fallback – no remote health check
