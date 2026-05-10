"""Parallel and optimized fetching utilities for drug scrapers."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def fetch_urls_parallel(
    fetch_fn,
    urls: list[str],
    concurrency: int = 8,
    batch_size: int = 50,
    retry_count: int = 2,
) -> list[tuple[int, Any]]:
    """
    Fetch multiple URLs in parallel with controlled concurrency.

    Args:
        fetch_fn: Async function to fetch a single URL (url -> result)
        urls: List of URLs to fetch
        concurrency: Max concurrent requests
        batch_size: Process URLs in batches to avoid memory issues
        retry_count: Number of retries per URL

    Returns:
        List of (index, result) tuples for successful fetches
    """
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    async def fetch_with_retry(idx: int, url: str) -> tuple[int, Any] | None:
        async with semaphore:
            for attempt in range(retry_count):
                try:
                    result = await fetch_fn(url)
                    if result is not None:
                        return (idx, result)
                except Exception as e:
                    if attempt == retry_count - 1:
                        logger.debug(f"Failed to fetch {url}: {e}")
                    await asyncio.sleep(0.5 * (attempt + 1))
            return None

    # Process in batches
    for batch_start in range(0, len(urls), batch_size):
        batch_end = min(batch_start + batch_size, len(urls))
        batch_urls = urls[batch_start:batch_end]
        batch_indices = list(range(batch_start, batch_end))

        tasks = [fetch_with_retry(i, u) for i, u in zip(batch_indices, batch_urls)]
        batch_results = await asyncio.gather(*tasks)

        for r in batch_results:
            if r is not None:
                results.append(r)

        # Small delay between batches
        if batch_end < len(urls):
            await asyncio.sleep(0.1)

    return results


async def fetch_all_with_bypass(
    urls: list[str],
    base_url: str = "",
    concurrency: int = 8,
    rate_limit: float = 0.5,
) -> list[tuple[int, str | None]]:
    """
    Fetch multiple URLs using the bypass system with parallel sessions.

    Uses curl_cffi impersonation sessions pooled for concurrent access.
    """
    from utils.bypass import ParallelBypassSession

    async with ParallelBypassSession(
        base_url,
        pool_size=min(concurrency, 4),
        rate_limit=rate_limit,
    ) as session:
        # Fetch in batches to avoid overwhelming
        semaphore = asyncio.Semaphore(concurrency)
        results = []

        async def fetch_one(idx: int, url: str) -> tuple[int, str | None]:
            async with semaphore:
                html = await session.get(url)
                return (idx, html)

        tasks = [fetch_one(i, u) for i, u in enumerate(urls)]
        results = await asyncio.gather(*tasks)

        return list(results)