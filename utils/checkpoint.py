"""Checkpoint manager for resuming interrupted scrapes with URL-level tracking."""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import orjson

logger = logging.getLogger(__name__)


@dataclass
class CheckpointState:
    """State for a single scraper run."""
    scraper_name: str
    started_at: float
    last_update: float
    urls_total: int = 0
    urls_completed: int = 0
    drugs_saved: int = 0
    errors: int = 0
    last_url: Optional[str] = None
    eta_seconds: Optional[float] = None
    status: str = "running"  # running, completed, failed, cancelled

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CheckpointState":
        return cls(**data)


class CheckpointManager:
    """Manages saving/loading of scrape progress with URL-level deduplication."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.checkpoint_dir = self.data_dir / ".checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.checkpoint_dir / "state.db"
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                scraper TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS completed_urls (
                scraper TEXT NOT NULL,
                url_hash TEXT NOT NULL,
                completed_at REAL NOT NULL,
                PRIMARY KEY (scraper, url_hash)
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_urls_scraper ON completed_urls(scraper)")
        conn.commit()
        conn.close()

    def save(self, state: CheckpointState):
        """Save checkpoint state."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(
                "INSERT OR REPLACE INTO checkpoints (scraper, state_json, updated_at) VALUES (?, ?, ?)",
                (state.scraper_name, orjson.dumps(state.to_dict()).decode(), time.time())
            )
            conn.commit()
            logger.debug(f"Checkpoint saved: {state.scraper_name} ({state.urls_completed}/{state.urls_total})")
        finally:
            conn.close()

    def load(self, scraper_name: str) -> Optional[CheckpointState]:
        """Load checkpoint state for a scraper."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            row = conn.execute(
                "SELECT state_json FROM checkpoints WHERE scraper = ?",
                (scraper_name,)
            ).fetchone()
            if row:
                data = orjson.loads(row[0])
                return CheckpointState.from_dict(data)
        finally:
            conn.close()
        return None

    def exists(self, scraper_name: str) -> bool:
        """Check if checkpoint exists for scraper."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            count = conn.execute(
                "SELECT COUNT(*) FROM checkpoints WHERE scraper = ?",
                (scraper_name,)
            ).fetchone()[0]
            return count > 0
        finally:
            conn.close()

    def add_url(self, scraper_name: str, url: str):
        """Mark a URL as completed for a scraper."""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:32]
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(
                "INSERT OR IGNORE INTO completed_urls (scraper, url_hash, completed_at) VALUES (?, ?, ?)",
                (scraper_name, url_hash, time.time())
            )
            conn.commit()
        finally:
            conn.close()

    def get_completed_urls(self, scraper_name: str) -> set[str]:
        """Get set of URL hashes completed for scraper."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            rows = conn.execute(
                "SELECT url_hash FROM completed_urls WHERE scraper = ?"
            ).fetchall()
            return set(r[0] for r in rows)
        finally:
            conn.close()

    def is_url_completed(self, scraper_name: str, url: str) -> bool:
        """Check if a URL is already processed."""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:32]
        conn = sqlite3.connect(str(self.db_path))
        try:
            count = conn.execute(
                "SELECT COUNT(*) FROM completed_urls WHERE scraper = ? AND url_hash = ?",
                (scraper_name, url_hash)
            ).fetchone()[0]
            return count > 0
        finally:
            conn.close()

    def get_resumable_scrapers(self, all_scrapers: list[str]) -> list[str]:
        """Get list of scrapers with incomplete checkpoints."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            rows = conn.execute(
                "SELECT scraper, state_json FROM checkpoints WHERE scraper IN ({})".format(
                    ",".join("?" * len(all_scrapers))
                ),
                all_scrapers
            ).fetchall()

            resumable = []
            for scraper, state_json in rows:
                state = CheckpointState.from_dict(orjson.loads(state_json))
                if state.status == "running" and state.urls_completed < state.urls_total:
                    resumable.append(scraper)
            return resumable
        finally:
            conn.close()

    def delete(self, scraper_name: str):
        """Delete checkpoint for a scraper."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute("DELETE FROM checkpoints WHERE scraper = ?", (scraper_name,))
            conn.execute("DELETE FROM completed_urls WHERE scraper = ?", (scraper_name,))
            conn.commit()
        finally:
            conn.close()

    def list_all(self) -> list[tuple[str, CheckpointState, float]]:
        """List all checkpoints with their states."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            rows = conn.execute("SELECT scraper, state_json, updated_at FROM checkpoints").fetchall()
            result = []
            for scraper, state_json, updated in rows:
                state = CheckpointState.from_dict(orjson.loads(state_json))
                result.append((scraper, state, updated))
            return result
        finally:
            conn.close()

    def cleanup_old(self, retention_days: int = 7):
        """Remove checkpoints older than retention_days."""
        cutoff = time.time() - (retention_days * 86400)
        conn = sqlite3.connect(str(self.db_path))
        try:
            deleted = conn.execute(
                "DELETE FROM checkpoints WHERE updated_at < ?",
                (cutoff,)
            ).rowcount
            conn.commit()
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} old checkpoint(s)")
        finally:
            conn.close()