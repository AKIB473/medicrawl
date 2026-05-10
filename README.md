# 🚀 Medicrawl

<div align="center">

<!-- Medicrawl logo: parallel scraping with checkpoint, cache, circuit breaker -->
<svg width="720" height="240" viewBox="0 0 720 240" xmlns="http://www.w3.org/2000/svg" aria-label="Medicrawl: Parallel scraping with checkpoint, cache, and circuit breaker">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117"><animate attributeName="stop-color" values="#0d1117;#161b22;#0d1117" dur="8s" repeatCount="indefinite"/></stop>
      <stop offset="100%" stop-color="#161b22"><animate attributeName="stop-color" values="#161b22;#0d1117;#161b22" dur="8s" repeatCount="indefinite"/></stop>
    </linearGradient>
    <linearGradient id="nodeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#58a6ff"><animate attributeName="stop-color" values="#58a6ff;#8a63d2;#58a6ff" dur="4s" repeatCount="indefinite"/></stop>
      <stop offset="100%" stop-color="#8a63d2"><animate attributeName="stop-color" values="#8a63d2;#58a6ff;#8a63d2" dur="4s" repeatCount="indefinite"/></stop>
    </linearGradient>
    <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#2ea043"/><stop offset="50%" stop-color="#3fb950"/><stop offset="100%" stop-color="#2ea043"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="particleGlow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="100%" height="100%" fill="url(#bgGrad)"/>
  <g fill="#58a6ff" opacity="0.15" filter="url(#particleGlow)">
    <circle r="2"><animateMotion path="M0 0 Q360 120 720 0" dur="20s" repeatCount="indefinite"/></circle>
    <circle r="1.5"><animateMotion path="M720 240 Q360 120 0 240" dur="25s" repeatCount="indefinite"/></circle>
    <circle r="1"><animateMotion path="M0 120 Q720 120 0 120" dur="18s" repeatCount="indefinite"/></circle>
  </g>
  <g id="nodes">
    <circle cx="160" cy="120" r="32" fill="url(#nodeGrad)" filter="url(#glow)"><animate attributeName="r" values="32;40;32" dur="2.5s" repeatCount="indefinite"/></circle>
    <circle cx="160" cy="120" r="32" fill="none" stroke="#58a6ff" stroke-width="2" opacity="0.6"><animate attributeName="r" values="32;52;32" dur="2.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.6;0;0.6" dur="2.5s" repeatCount="indefinite"/></circle>
    <circle r="4" fill="#fff"><animateMotion path="M160 88 A40 40 0 1 1 160 152" dur="3s" repeatCount="indefinite"/></circle>
    <circle cx="360" cy="120" r="32" fill="url(#nodeGrad)" filter="url(#glow)"><animate attributeName="r" values="32;40;32" dur="2.5s" begin="0.83s" repeatCount="indefinite"/></circle>
    <circle cx="360" cy="120" r="32" fill="none" stroke="#58a6ff" stroke-width="2" opacity="0.6"><animate attributeName="r" values="32;52;32" dur="2.5s" begin="0.83s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.6;0;0.6" dur="2.5s" begin="0.83s" repeatCount="indefinite"/></circle>
    <circle r="4" fill="#fff"><animateMotion path="M360 88 A40 40 0 1 1 360 152" dur="3s" begin="1s" repeatCount="indefinite"/></circle>
    <circle cx="560" cy="120" r="32" fill="url(#nodeGrad)" filter="url(#glow)"><animate attributeName="r" values="32;40;32" dur="2.5s" begin="1.66s" repeatCount="indefinite"/></circle>
    <circle cx="560" cy="120" r="32" fill="none" stroke="#58a6ff" stroke-width="2" opacity="0.6"><animate attributeName="r" values="32;52;32" dur="2.5s" begin="1.66s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.6;0;0.6" dur="2.5s" begin="1.66s" repeatCount="indefinite"/></circle>
    <circle r="4" fill="#fff"><animateMotion path="M560 88 A40 40 0 1 1 560 152" dur="3s" begin="2s" repeatCount="indefinite"/></circle>
  </g>
  <g id="packets">
    <circle r="5" fill="#2ea043" filter="url(#particleGlow)"><animateMotion path="M188 120 L332 120" dur="2s" repeatCount="indefinite" begin="0.2s"/></circle>
    <circle r="5" fill="#2ea043" filter="url(#particleGlow)"><animateMotion path="M332 120 L188 120" dur="2s" repeatCount="indefinite" begin="1.2s"/></circle>
    <circle r="5" fill="#2ea043" filter="url(#particleGlow)"><animateMotion path="M388 120 L532 120" dur="2s" repeatCount="indefinite" begin="0.7s"/></circle>
    <circle r="5" fill="#2ea043" filter="url(#particleGlow)"><animateMotion path="M532 120 L388 120" dur="2s" repeatCount="indefinite" begin="1.7s"/></circle>
  </g>
  <g id="links" stroke="url(#lineGrad)" stroke-width="6" stroke-linecap="round" opacity="0.8">
    <line x1="188" y1="120" x2="332" y2="120"><animate attributeName="stroke-dasharray" values="0 144;144 0" dur="3s" repeatCount="indefinite"/></line>
    <line x1="388" y1="120" x2="532" y2="120"><animate attributeName="stroke-dasharray" values="0 144;144 0" dur="3s" begin="1.5s" repeatCount="indefinite"/></line>
  </g>
  <text x="360" y="185" text-anchor="middle" fill="#c9d1d9" font-family="'Segoe UI', 'Helvetica', 'Arial', sans-serif" font-size="20" font-weight="700">
    <tspan>⚡ Parallel • 💾 Checkpoint • 📡 Cache</tspan><animate attributeName="fill" values="#c9d1d9;#58a6ff;#2ea043;#c9d1d9" dur="6s" repeatCount="indefinite"/>
  </text>
  <text x="360" y="210" text-anchor="middle" fill="#8b949e" font-family="'Segoe UI', 'Helvetica', 'Arial', sans-serif" font-size="12">
    <tspan>27 Sources • Resumable • Zero Waste</tspan><animateTransform attributeName="transform" type="translate" values="0,0;0,-3;0,0" dur="3s" repeatCount="indefinite" additive="sum"/>
  </text>
</svg>

</div>

## 🌟 Overview

**Medicrawl** is a production‑grade pipeline that scrapes medicine data from 27 global sources in parallel, with zero data loss, intelligent caching, circuit breakers, and full observability.

It avoids repeated work by checkpointing every URL and caching HTTP responses. Each scraper runs with configurable concurrency, making full runs fast and resumable.

---

## ⚡ Quick Start

```bash
# Install (requires Python 3.11+)
pip install -e .
pip install curl_cffi cloudscraper beautifulsoup4 orjson

# Run all sources with full concurrency and cache
python main_advanced.py scrape --all --concurrency 0

# Run a single category (Bangladesh sources)
python main_advanced.py scrape --bd

# Resume an interrupted run (skips completed URLs automatically)
python main_advanced.py resume

# View metrics from the last run
cat data/metrics.json | python -m json.tool | less
```

---

## 🏆 Key Features

| Feature | Sequential (old) | Medicrawl (now) |
|---------|-----------------|-----------------|
| **Concurrency** | 1 URL at a time | 5‑20 URLs concurrently per source (configurable) |
| **Resume** | Re-scrape everything | Skip completed URLs via checkpoint |
| **Duplicate Requests** | Every run re‑fetches | SQLite HTTP cache (TTL‑based) |
| **Rate‑limit handling** | Crude sleep loops | Adaptive per-domain limiter |
| **Observability** | Minimal logging | Prometheus‑style metrics |
| **Circuit breaker** | None | Auto‑pause failing domains (5 min) |

---

## 📊 Performance Gains (local run)

| Metric | Sequential | Medicrawl (parallel per source) | Δ |
|--------|------------|-------------------------------|---|
| Wall‑time (all sources) | 6+ hrs | **~25 min** (with sharding) — single-process **~2 hrs** | 6–15× faster |
| Re‑run waste | 100% re‑scrape | **~80% cache hit, 0% duplicate URLs** | Near‑instant resume |
| Requests / sec | ~10 | **~80** (distributed across domains) | 8× throughput |

*Note: The 25–30 minute total runtime required GitHub Actions sharding (removed). Single-process full run takes longer (~2 hrs) but still benefits from per-source concurrency and checkpointing.*

---

### 🛠️ Pipeline Architecture

<div align="center">

<!-- Animated data flow through pipeline stages -->
<svg width="720" height="160" viewBox="0 0 720 160" xmlns="http://www.w3.org/2000/svg" aria-label="Pipeline: Sources → Parallel Scrapers → Checkpoint/Cache → Database">
  <defs>
    <linearGradient id="stageGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#58a6ff"/><stop offset="100%" stop-color="#1f6feb"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect x="40" y="50" width="140" height="60" rx="10" fill="url(#stageGrad)" filter="url(#glow)"><animate attributeName="y" values="50;45;50" dur="2s" repeatCount="indefinite"/></rect>
  <text x="110" y="85" text-anchor="middle" fill="white" font-family="sans-serif" font-size="14" font-weight="600">27 Sources</text>
  <rect x="220" y="50" width="140" height="60" rx="10" fill="url(#stageGrad)" filter="url(#glow)"><animate attributeName="y" values="50;45;50" dur="2s" begin="0.5s" repeatCount="indefinite"/></rect>
  <text x="290" y="75" text-anchor="middle" fill="white" font-family="sans-serif" font-size="13" font-weight="600">Parallel<br/>Scrapers</text>
  <rect x="400" y="50" width="140" height="60" rx="10" fill="url(#stageGrad)" filter="url(#glow)"><animate attributeName="y" values="50;45;50" dur="2s" begin="1s" repeatCount="indefinite"/></rect>
  <text x="470" y="75" text-anchor="middle" fill="white" font-family="sans-serif" font-size="13" font-weight="600">Checkpoint</text>
  <text x="470" y="95" text-anchor="middle" fill="white" font-family="sans-serif" font-size="13" font-weight="600">+ Cache</text>
  <rect x="560" y="50" width="120" height="60" rx="10" fill="url(#stageGrad)" filter="url(#glow)"><animate attributeName="y" values="50;45;50" dur="2s" begin="1.5s" repeatCount="indefinite"/></rect>
  <text x="620" y="85" text-anchor="middle" fill="white" font-family="sans-serif" font-size="13" font-weight="600">Merged<br/>DB</text>
  <g fill="none" stroke="#2ea043" stroke-width="3" stroke-linecap="round">
    <line x1="180" y1="80" x2="210" y2="80"><animate attributeName="stroke-dasharray" values="0 20;20 0" dur="1.5s" repeatCount="indefinite" begin="0.2s"/></line>
    <line x1="360" y1="80" x2="390" y2="80"><animate attributeName="stroke-dasharray" values="0 20;20 0" dur="1.5s" repeatCount="indefinite" begin="0.7s"/></line>
    <line x1="540" y1="80" x2="550" y2="80"><animate attributeName="stroke-dasharray" values="0 20;20 0" dur="1.5s" repeatCount="indefinite" begin="1.2s"/></line>
  </g>
</svg>

</div>

---

## 🔧 How It Works

1. **Source selection** — Choose all sources or a category (`--bd`, `--intl`, `--research`)
2. **Per-source parallelism** — Each scraper fetches 5–20 URLs concurrently (configurable via `--concurrency`)
3. **Checkpoint filtering** — Already‑completed URLs (by hash) are skipped automatically
4. **HTTP cache** — Responses cached to disk with TTL (default 1 hour); cache hits skip network
5. **Circuit breaker** — After 5 failures on a domain, further requests pause for 5 minutes
6. **Metrics collection** — Successes, failures, cache hits, durations recorded to `data/metrics.json`
7. **Resume support** — Rerun anytime; only new/changed URLs are processed
8. **Post‑process** — Normalize, deduplicate, merge into canonical drug records, build SQLite DB + merged JSON

---

## 📁 Repository Structure

```
medicrawl/
├── scrapers/
│   ├── base.py                 # Original base scraper (sequential)
│   ├── base_advanced.py        # Advanced base (checkpoint, cache, circuit, concurrency)
│   ├── bangladesh/             # 11 Bangladesh sources
│   ├── international/          # 14 international sources
│   └── research/               # 2 research sources
├── utils/
│   ├── checkpoint.py           # SQLite checkpoint manager (URL hash → completed)
│   ├── cache.py                # HTTP response cache with TTL + LRU eviction
│   ├── metrics.py              # Scrape metrics collector
│   ├── pipeline.py             # Post‑process: merge → DB → export
│   └── change_detector.py      # Detect data changes between runs
├── models/
│   └── drug.py                 # Pydantic models (Drug, Manufacturer, DrugPrice, ScrapeMeta)
├── config/
│   └── default.yaml            # Global and per‑source configuration
├── data/
│   ├── .checkpoints/           # SQLite DB: completed URL hashes + scraper state
│   ├── .cache/                 # SQLite DB: HTTP response cache
│   ├── medex/ drugs.json meta.json
│   ├── dims/ …
│   ├── metrics.json
│   ├── merged_drugs.json       # Final merged dataset
│   └── mediscrape.db           # SQLite database (queryable)
├── main.py                     # Legacy CLI (sequential, no advanced features)
├── main_advanced.py            # Modern CLI (resume, cache, concurrency)
├── scripts/
│   └── upgrade_scrapers.py     # Migrate old scrapers to advanced base
└── pyproject.toml
```

---

## ⚙️ Configuration

Create `config/default.yaml` (optional — sensible defaults exist):

```yaml
scrapers:
  default_concurrency: 10      # URLs in flight per scraper
  request_timeout: 30          # seconds per HTTP request
  scraper_timeout: 900         # max wall time per scraper (15 min)
  checkpoint_enabled: true
  checkpoint_interval: 100     # save checkpoint every N drugs
  cache_enabled: true
  cache_ttl_seconds: 3600      # 1 hour

sources:
  medex:
    concurrency: 8             # per‑source override
    timeout: 1200              # 20 min for large sources
  dims:
    concurrency: 4
```

---

## 🧪 Testing

```bash
# Fast sanity check (2 sources, low concurrency)
python main_advanced.py scrape medex dims --concurrency 2 --timeout 300

# Re‑run — should skip completed URLs
python main_advanced.py scrape medex dims --concurrency 2

# Check checkpoint DB
sqlite3 data/.checkpoints/state.db "SELECT scraper, status, urls_completed FROM checkpoints"

# Inspect metrics
python -c "import json; print(json.dumps(json.load(open('data/metrics.json')), indent=2))"
```

---

## 🤝 Contributing

We ❤️ PRs! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

All contributions, ideas, and credits belong to the maintainer (Akibuzzaman Akib).

---

## 📄 License

MIT — see [LICENSE](LICENSE)
