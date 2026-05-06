# Advanced Medicrawl - Optimized for Speed & Reliability

## Key Enhancements

### 1. **Ultra-Parallel Architecture**
- Concurrent URL fetching **within each scraper** (not just across scrapers)
- Adaptive concurrency based on source response times
- Connection pooling with `httpx.AsyncClient` limits

### 2. **Smart Timeouts & Fail-Fast**
- **Per-scraper timeout**: 15-30 minutes max per source
- **Per-request timeout**: 10-30 seconds
- **Job-level timeout**: 60 minutes (reduced from 360)
- Fast failure on rate limits / blocks

### 3. **Intelligent Retry & Circuit Breaker**
- Exponential backoff with jitter
- Circuit breaker pattern: stop hammering failing sources
- Retry only transient errors (5xx, timeouts, connection errors)
- Skip permanently failing sources

### 4. **Checkpoint/Resume System**
- Save progress every N records
- Resume from last checkpoint if interrupted
- SQLite-based progress tracking
- No re-scraping of already completed items

### 5. **Rate Limit Intelligence**
- Per-domain rate limit tracking
- Dynamic throttling based on response codes
- Retry-After header respect
- Burst allowance with smoothing

### 6. **Caching Layer**
- HTTP response caching (1-hour TTL)
- Avoid re-fetching same URLs
- Cache invalidation on ETag/Last-Modified changes

### 7. **Better Sharding Strategy**
- 30+ shards instead of 14
- Source-based + alphabetical sharding
- Smaller batches = faster completion

### 8. **Metrics & Observability**
- Prometheus-style metrics
- Progress bars with ETA
- Detailed error categorization
- Performance profiling per source

---

## Modified Files Overview

### Core Changes:
- `main.py` - Enhanced CLI with resume, timeout, metrics
- `scrapers/base.py` - Supercharged base scraper with all features
- `scrapers/*/*.py` - Updated to use new async patterns
- `.github/workflows/crawler.yml` - Optimized matrix, shorter timeouts
- `pyproject.toml` - Added new dependencies
- `utils/checkpoint.py` - NEW: checkpoint manager
- `utils/metrics.py` - NEW: metrics collection
- `utils/cache.py` - NEW: HTTP caching layer
- `config/default.yaml` - NEW: centralized configuration
