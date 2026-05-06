"""Metrics collection for monitoring scraper performance."""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ScrapeMetrics:
    """Metrics for a single scraper run."""
    scraper_name: str
    start_time: float
    end_time: Optional[float] = None
    urls_attempted: int = 0
    urls_succeeded: int = 0
    urls_failed: int = 0
    drugs_saved: int = 0
    total_bytes: int = 0
    errors_by_type: dict = field(default_factory=lambda: defaultdict(int))
    retries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    rate_limited: int = 0  # times we hit rate limit and waited

    @property
    def duration(self) -> float:
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def success_rate(self) -> float:
        if self.urls_attempted == 0:
            return 0.0
        return (self.urls_succeeded / self.urls_attempted) * 100

    @property
    def drugs_per_second(self) -> float:
        dur = self.duration
        if dur == 0:
            return 0.0
        return self.drugs_saved / dur

    def to_summary(self) -> dict:
        """Get summary dict for reporting."""
        return {
            "scraper": self.scraper_name,
            "duration_seconds": round(self.duration, 2),
            "urls_attempted": self.urls_attempted,
            "urls_succeeded": self.urls_succeeded,
            "urls_failed": self.urls_failed,
            "success_rate_pct": round(self.success_rate, 2),
            "drugs_saved": self.drugs_saved,
            "drugs_per_second": round(self.drugs_per_second, 2),
            "retries": self.retries,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "rate_limited": self.rate_limited,
            "errors": dict(self.errors_by_type),
        }


class MetricsCollector:
    """Collects and persists metrics across all scrapers."""

    def __init__(self, metrics_file: Path):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self._metrics: dict[str, ScrapeMetrics] = {}
        self._start_time = time.time()

    def start_scraper(self, name: str) -> ScrapeMetrics:
        """Begin tracking a scraper."""
        metrics = ScrapeMetrics(scraper_name=name, start_time=time.time())
        self._metrics[name] = metrics
        logger.info(f"Started metrics for {name}")
        return metrics

    def get_metrics(self, name: str) -> Optional[ScrapeMetrics]:
        """Get metrics for a scraper."""
        return self._metrics.get(name)

    def finish_scraper(self, name: str):
        """Mark scraper as completed."""
        if name in self._metrics:
            self._metrics[name].end_time = time.time()
            self.save()

    def record_url(self, name: str, success: bool, error_type: Optional[str] = None):
        """Record URL fetch attempt."""
        if name not in self._metrics:
            self.start_scraper(name)
        m = self._metrics[name]
        m.urls_attempted += 1
        if success:
            m.urls_succeeded += 1
        else:
            m.urls_failed += 1
            if error_type:
                m.errors_by_type[error_type] += 1

    def record_drug(self, name: str, bytes_saved: int = 0):
        """Record a drug saved."""
        if name not in self._metrics:
            self.start_scraper(name)
        self._metrics[name].drugs_saved += 1
        self._metrics[name].total_bytes += bytes_saved

    def record_retry(self, name: str):
        """Record a retry attempt."""
        if name in self._metrics:
            self._metrics[name].retries += 1

    def record_cache(self, name: str, hit: bool):
        """Record cache hit/miss."""
        if name in self._metrics:
            if hit:
                self._metrics[name].cache_hits += 1
            else:
                self._metrics[name].cache_misses += 1

    def record_rate_limit(self, name: str):
        """Record hitting a rate limit."""
        if name in self._metrics:
            self._metrics[name].rate_limited += 1

    def save(self):
        """Persist metrics to disk."""
        summary = {
            "run_started_at": self._start_time,
            "total_duration_seconds": round(time.time() - self._start_time, 2),
            "scrapers": [m.to_summary() for m in self._metrics.values()],
            "total_drugs": sum(m.drugs_saved for m in self._metrics.values()),
            "total_errors": sum(m.urls_failed for m in self._metrics.values()),
        }

        # Atomic write via temp file
        tmp = self.metrics_file.with_suffix('.tmp')
        tmp.write_text(json.dumps(summary, indent=2))
        tmp.replace(self.metrics_file)
        logger.debug(f"Metrics saved to {self.metrics_file}")

    def load_previous(self) -> Optional[dict]:
        """Load previous metrics if available."""
        if self.metrics_file.exists():
            return json.loads(self.metrics_file.read_text())
        return None

    def get_summary(self) -> dict:
        """Get overall summary."""
        total_drugs = sum(m.drugs_saved for m in self._metrics.values())
        total_time = time.time() - self._start_time
        active_scrapers = len(self._metrics)
        completed = sum(1 for m in self._metrics.values() if m.end_time is not None)

        return {
            "total_drugs": total_drugs,
            "elapsed_seconds": round(total_time, 2),
            "active_scrapers": active_scrapers,
            "completed_scrapers": completed,
            "drugs_per_second": round(total_drugs / total_time, 2) if total_time > 0 else 0,
        }
