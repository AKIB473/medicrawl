"""Advanced base scraper with checkpointing, caching, circuit breaker, concurrency utilities."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator, Callable
from urllib.parse import urlparse

import orjson
import httpx

from scrapers.base import BaseScrapingScraper, BaseAPIScraper
from models.drug import Drug, ScrapeMeta

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Circuit Breaker
# --------------------------------------------------------------------------- #

class CircuitBreaker:
    """Per-domain circuit breaker to stop hammering failing hosts."""

    def __init__(self, failure_threshold: int = 5, timeout: float = 300.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures: dict[str, int] = {}
        self.last_failure_time: dict[str, float] = {}
        self.states: dict[str, bool] = {}  # True = closed (OK), False = open (blocked)

    def record_failure(self, domain: str):
        self.failures[domain] = self.failures.get(domain, 0) + 1
        self.last_failure_time[domain] = time.time()
        if self.failures[domain] >= self.failure_threshold:
            self.states[domain] = False
            logger.warning(f"Circuit breaker OPEN for {domain} (failures: {self.failures[domain]})")

    def record_success(self, domain: str):
        self.failures[domain] = 0
        self.states[domain] = True

    def is_open(self, domain: str) -> bool:
        if domain not in self.states:
            return False
        if self.states[domain]:
            return False
        last_fail = self.last_failure_time.get(domain, 0)
        if time.time() - last_fail > self.timeout:
            logger.info(f"Circuit breaker half-open for {domain}, allowing test request")
            return False
        return True


def _get_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or ""


# --------------------------------------------------------------------------- #
# Advanced Scraper Mixin
# --------------------------------------------------------------------------- #

class AdvancedScraperMixin:
    """
    Mixin providing advanced features:
    - HTTP caching (via HTTPCache)
    - Circuit breaker
    - Checkpoint filtering
    - Concurrent iteration helper
    - Metrics collection
    - Overridden fetch/api methods with caching/circuit
    - Enhanced run() with per-URL checkpoint updates
    """

    # To be injected by main_advanced
    checkpoint_manager = None
    cache = None
    metrics = None

    # Tunables (may be overridden by per-source config)
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    scraper_timeout: int = 900
    checkpoint_interval: int = 100
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 300.0

    def __init__(self, *args, **kwargs):
        # Extract advanced params before forwarding to super
        self.checkpoint_manager = kwargs.pop("checkpoint_manager", None)
        self.cache = kwargs.pop("cache", None)
        self.metrics = kwargs.pop("metrics", None)
        self._apply_source_config()
        super().__init__(*args, **kwargs)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.circuit_breaker_threshold,
            timeout=self.circuit_breaker_timeout,
        )
        self._last_request_times: dict[str, float] = {}

    def _apply_source_config(self):
        """Pull per-source overrides from global CONFIG if available."""
        try:
            from main_advanced import CONFIG  # late import to avoid circular
            source_cfg = CONFIG.get("sources", {}).get(self.name, {})
            default_cfg = CONFIG.get("scrapers", {})
            self.max_concurrent_requests = source_cfg.get("concurrency", default_cfg.get("default_concurrency", 10))
            self.scraper_timeout = source_cfg.get("timeout", default_cfg.get("scraper_timeout", 900))
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # Helper: checkpoint URL filtering
    # ------------------------------------------------------------------ #

    def filter_checkpoint(self, urls: list) -> list:
        """Exclude URLs already completed according to checkpoint manager."""
        if not self.checkpoint_manager:
            return urls
        completed = self.checkpoint_manager.get_completed_urls(self.name)
        total_before = len(urls)
        filtered = [u for u in urls if u not in completed]
        if total_before > len(filtered):
            logger.info(f"{self.name}: filtered {total_before - len(filtered)} already-done URLs ({len(filtered)} remaining)")
        return filtered

    # ------------------------------------------------------------------ #
    # Concurrent processing helper
    # ------------------------------------------------------------------ #

    async def concurrent_iter(self, items: list, processor: Callable) -> AsyncIterator:
        """Process items concurrently with bounded semaphore; yields processed results."""
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)

        async def wrapper(item):
            async with semaphore:
                return await processor(item)

        tasks = [asyncio.create_task(wrapper(item)) for item in items]
        for fut in asyncio.as_completed(tasks):
            try:
                result = await fut
                if result is not None:
                    yield result
            except Exception as e:
                logger.warning(f"concurrent_iter error: {e}")
                if self.metrics:
                    self.metrics.record_url(self.name, False, type(e).__name__)
        # Ensure all tasks done to avoid warnings
        await asyncio.gather(*tasks, return_exceptions=True)

    # ------------------------------------------------------------------ #
    # Overridden fetch/page methods with caching & circuit breaker
    # ------------------------------------------------------------------ #

    async def fetch_page(self, url: str, **kwargs):
        domain = _get_domain(url) or _get_domain(self.base_url)
        if self.circuit_breaker.is_open(domain):
            logger.warning(f"Circuit breaker OPEN for {domain}, skipping {url}")
            if self.metrics:
                self.metrics.record_url(self.name, False, "circuit_open")
            raise Exception(f"Circuit breaker open for {domain}")

        if self.cache:
            cached = self.cache.get(url)
            if cached:
                status, headers, body = cached
                if self.metrics:
                    self.metrics.record_cache(self.name, True)
                return _CachedHTMLPage(body.decode("utf-8", errors="replace"), url)

        try:
            resp = await super().fetch_page(url, **kwargs)
            if self.cache:
                try:
                    body = resp.text if hasattr(resp, "text") else str(resp)
                    body_bytes = body.encode("utf-8")
                    self.cache.set(url, getattr(resp, "status", 200), dict(getattr(resp, "headers", {})), body_bytes)
                except Exception as e:
                    logger.debug(f"Cache set failed: {e}")
            if self.metrics:
                self.metrics.record_url(self.name, True)
            self.circuit_breaker.record_success(domain)
            return resp
        except Exception as e:
            self.circuit_breaker.record_failure(domain)
            if self.metrics:
                self.metrics.record_url(self.name, False, type(e).__name__)
            raise

    async def api_get(self, url: str, params: dict | None = None) -> dict:
        from urllib.parse import urlencode
        full_url = f"{url}?{urlencode(params)}" if params else url

        domain = _get_domain(full_url) or _get_domain(self.base_url)
        if self.circuit_breaker.is_open(domain):
            logger.warning(f"Circuit breaker OPEN for {domain}")
            if self.metrics:
                self.metrics.record_url(self.name, False, "circuit_open")
            raise Exception(f"Circuit breaker open for {domain}")

        if self.cache:
            cached = self.cache.get(full_url)
            if cached:
                status, headers, body = cached
                if self.metrics:
                    self.metrics.record_cache(self.name, True)
                import json
                return json.loads(body)

        try:
            result = await super().api_get(url, params)
            if self.cache:
                body_bytes = orjson.dumps(result)
                self.cache.set(full_url, 200, {}, body_bytes)
            if self.metrics:
                self.metrics.record_url(self.name, True)
            self.circuit_breaker.record_success(domain)
            return result
        except Exception as e:
            self.circuit_breaker.record_failure(domain)
            if self.metrics:
                self.metrics.record_url(self.name, False, type(e).__name__)
            raise

    # ------------------------------------------------------------------ #
    # Overridden run with checkpoint tracking and cleanup
    # ------------------------------------------------------------------ #

    async def run(self) -> ScrapeMeta:
        """Run scraper with checkpoint tracking of completed URLs and proper cleanup."""
        start = time.time()
        meta = ScrapeMeta(source=self.name)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        drugs: list[Drug] = []
        try:
            async for drug in self.scrape_all():
                if drug:
                    drugs.append(drug)
                    meta.total_drugs += 1
                    if self.checkpoint_manager:
                        self.checkpoint_manager.add_url(self.name, drug.source_url)
        except Exception as e:
            logger.error(f"[{self.name}] Error during scraping: {e}")
            meta.errors += 1
        finally:
            try:
                await self._cleanup_resources()
            except Exception as e:
                logger.debug(f"Cleanup error: {e}")

        meta.duration_seconds = time.time() - start

        output_file = self.data_dir / "drugs.json"
        old_checksum = self._file_checksum(output_file)
        if meta.errors > 0 and not drugs:
            meta.checksum = old_checksum
            if old_checksum:
                logger.warning(f"[{self.name}] Scrape failed with no data; preserving existing drugs.json")
        else:
            data = [orjson.loads(d.to_json_bytes()) for d in drugs]
            output_file.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))
            new_checksum = self._file_checksum(output_file)
            meta.checksum = new_checksum
            if old_checksum and old_checksum != new_checksum:
                logger.info(f"[{self.name}] Data changed! Old: {old_checksum[:8]}, New: {new_checksum[:8]}")

        meta_file = self.data_dir / "meta.json"
        meta_file.write_bytes(orjson.dumps(meta.model_dump(mode="json"), option=orjson.OPT_INDENT_2))
        logger.info(f"[{self.name}] Done: {meta.total_drugs} drugs in {meta.duration_seconds:.1f}s")
        return meta

    @staticmethod
    def _file_checksum(path: Path) -> str | None:
        if not path.exists():
            return None
        return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------- #
# Cached HTML wrapper (for fetch_page cache hits)
# --------------------------------------------------------------------------- #

class _CachedHTMLPage:
    def __init__(self, html: str, url: str = ""):
        self._html = html
        self.url = url

    @property
    def text(self) -> str:
        return self._html

    def css(self, selector: str):
        from lxml import html as lxml_html
        from lxml.cssselect import CSSSelector
        root = lxml_html.fromstring(self._html)
        sel = CSSSelector(selector)
        return [_Elem(e) for e in sel(root)]

    def css_first(self, selector: str):
        results = self.css(selector)
        return results[0] if results else None


class _Elem:
    def __init__(self, elem):
        self._elem = elem

    @property
    def text(self) -> str:
        from lxml import etree
        return (etree.tostring(self._elem, method="text", encoding="unicode") or "").strip()

    @property
    def tag(self) -> str:
        t = self._elem.tag
        return t if isinstance(t, str) else ""

    @property
    def attrib(self) -> dict:
        return dict(self._elem.attrib)

    @property
    def parent(self):
        p = self._elem.getparent()
        return _Elem(p) if p is not None else None

    def css(self, selector: str):
        try:
            from lxml.cssselect import CSSSelector
            sel = CSSSelector(selector)
            return [_Elem(e) for e in sel(self._elem)]
        except Exception:
            return []

    def css_first(self, selector: str):
        results = self.css(selector)
        return results[0] if results else None


# --------------------------------------------------------------------------- #
# Concrete advanced base classes
# --------------------------------------------------------------------------- #

class BaseAdvancedScraper(AdvancedScraperMixin, BaseScrapingScraper):
    """Advanced scraper for HTML/Scraping sources."""
    pass


class BaseAdvancedAPIScraper(AdvancedScraperMixin, BaseAPIScraper):
    """Advanced scraper for API-based sources."""
    pass
