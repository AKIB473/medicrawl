"""Smart HTTP response cache with TTL and invalidation."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import sqlite3
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import orjson

logger = logging.getLogger(__name__)


class HTTPCache:
    """Disk-based HTTP response cache with TTL."""

    def __init__(self, cache_dir: Path, ttl_seconds: int = 3600, max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.db_path = self.cache_dir / "http_cache.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite cache database."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                url_hash TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                status INTEGER,
                headers TEXT,
                body BLOB,
                created_at REAL,
                etag TEXT,
                last_modified TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON responses(created_at)")
        conn.commit()
        conn.close()

    def _hash_url(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:32]

    def get(self, url: str, validate_etag: bool = False) -> Optional[tuple[int, dict, bytes]]:
        """Get cached response if still valid."""
        url_hash = self._hash_url(url)
        conn = sqlite3.connect(str(self.db_path))
        try:
            row = conn.execute(
                "SELECT status, headers, body, created_at, etag, last_modified FROM responses WHERE url_hash = ?",
                (url_hash,)
            ).fetchone()

            if not row:
                return None

            status, headers_json, body, created_at, etag, last_modified = row

            # Check TTL
            age = time.time() - created_at
            if age > self.ttl:
                # Delete expired entry
                conn.execute("DELETE FROM responses WHERE url_hash = ?", (url_hash,))
                conn.commit()
                return None

            headers = json.loads(headers_json)
            return status, headers, body
        finally:
            conn.close()

    def set(self, url: str, status: int, headers: dict, body: bytes,
            etag: Optional[str] = None, last_modified: Optional[str] = None):
        """Store response in cache."""
        url_hash = self._hash_url(url)
        headers_json = json.dumps(dict(headers))

        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("""
                INSERT OR REPLACE INTO responses
                (url_hash, url, status, headers, body, created_at, etag, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                url_hash, url, status, headers_json, body,
                time.time(), etag, last_modified
            ))
            conn.commit()

            # Enforce max size (LRU eviction)
            self._enforce_max_size(conn)
        finally:
            conn.close()

    def _enforce_max_size(self, conn):
        """Evict oldest entries if cache exceeds max size."""
        import os
        try:
            db_size = os.path.getsize(self.db_path)
            if db_size > self.max_size_bytes:
                # Delete oldest 20% of entries
                cutoff = time.time() - (self.ttl * 0.5)
                deleted = conn.execute(
                    "DELETE FROM responses WHERE created_at < ?",
                    (cutoff,)
                ).rowcount
                conn.commit()
                if deleted > 0:
                    logger.info(f"Cache size limit: evicted {deleted} old entries")
        except Exception as e:
            logger.warning(f"Cache size check failed: {e}")

    def invalidate(self, url: str):
        """Remove specific URL from cache."""
        url_hash = self._hash_url(url)
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("DELETE FROM responses WHERE url_hash = ?", (url_hash,))
            conn.commit()
        finally:
            conn.close()

    def clear(self):
        """Clear entire cache."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("DELETE FROM responses")
            conn.commit()
        finally:
            conn.close()

    def stats(self) -> dict:
        """Get cache statistics."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            count = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
            total_size = conn.execute("SELECT SUM(LENGTH(body)) FROM responses").fetchone()[0] or 0
            oldest = conn.execute("SELECT MIN(created_at) FROM responses").fetchone()[0]
            return {
                "entries": count,
                "size_bytes": total_size,
                "oldest_entry_age_seconds": time.time() - oldest if oldest else 0
            }
        finally:
            conn.close()

    @asynccontextmanager
    async def cached_request(self, session, url: str, method: str = "GET", **kwargs):
        """
        Context manager for cached HTTP requests.
        Usage: async with cache.cached_request(session, url) as resp:
        """
        cache_key = f"{method}:{url}:{json.dumps(kwargs, sort_keys=True)}"
        cached = self.get(cache_key)

        if cached:
            status, headers, body = cached
            logger.debug(f"Cache HIT: {url}")
            yield _CachedResponse(status, headers, body)
            return

        logger.debug(f"Cache MISS: {url}")
        resp = await session.request(method, url, **kwargs)
        body = await resp.aread()

        # Store in cache only for successful responses
        if 200 <= resp.status < 300:
            self.set(cache_key, resp.status, dict(resp.headers), body,
                     resp.headers.get("ETag"), resp.headers.get("Last-Modified"))

        yield resp


class _CachedResponse:
    """Mimics httpx.Response for cached content."""
    def __init__(self, status: int, headers: dict, body: bytes):
        self.status_code = status
        self.headers = headers
        self._body = body
        self._text: str | None = None
        self._json = None

    async def aread(self) -> bytes:
        return self._body

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = self._body.decode("utf-8", errors="replace")
        return self._text if self._text else ""

    def json(self):
        if self._json is None:
            import json
            self._json = json.loads(self._body)
        return self._json
