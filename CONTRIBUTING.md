# 🎯 Contributing to Medicine Data Scraper

## 🙏 Acknowledgment

**This project was initiated and is maintained by:**
- **Akibuzzaman Akib** (@akibuzzaman7) — Lead Developer

We welcome contributions from everyone! Please note that all contributors will be properly credited.

## 🚀 Getting Started

### Setup Your Development Environment

```bash
# Clone the repository
git clone https://github.com/AKIB473/medicine-data-scraper.git
cd medicine-data-scraper

# Add upstream remote
git remote add upstream https://github.com/AKIB473/medicine-data-scraper.git

# Install dependencies
pip install -e .
pip install playwright
playwright install chromium --with-deps
```

## 📋 Contribution Types

### 1. Add a New Scraper (Most Needed!)

#### Step 1: Create Scraper Skeleton

```python
# scrapers/[category]/new_source.py
from __future__ import annotations

import logging
from typing import AsyncIterator

from models.drug import Drug, Manufacturer, DrugPrice
from scrapers.base import BaseScrapingScraper

logger = logging.getLogger(__name__)

class NewSourceScraper(BaseScrapingScraper):
    name = "new_source"
    base_url = "https://example.com"
    rate_limit = 1.0
    use_stealth = True

    async def scrape_all(self) -> AsyncIterator[Drug]:
        # Your scraping logic
        yield drug
```

#### Step 2: Register Your Scraper

```python
# scrapers/__init__.py
BANGLADESH_SCRAPERS = [
    ...
    "new_source",
]

# Or for international
INTERNATIONAL_SCRAPERS = [
    ...
    "new_source",
]
```

#### Step 3: Test It

```bash
python main.py test-source new_source
```

### 2. Improve Data Quality

- Improve field extraction
- Add normalization rules
- Fix parsing for specific sources

### 3. Enhance Pipeline

- Add new export formats (CSV, Parquet)
- Improve search (add FTS5)
- Add data validation rules

### 4. Fix Bugs

1. Reproduce the bug
2. Write a test (if possible)
3. Fix the code
4. Verify the fix

### 5. Documentation

- Improve README
- Add docstrings
- Write tutorials

## 🛠 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/add-xyz-scraper
```

### 2. Make Changes

```bash
# Edit files
vim scrapers/category/my_scraper.py

# Test as you go
python main.py test-source my_scraper
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat: add XYZ scraper for ABC drugs

- Implemented XYZ API scraper
- Handles pagination
- Extracts 15 fields
- Test: 100+ drugs collected"
```

### 4. Push and PR

```bash
git push origin feature/add-xyz-scraper
```

Then open a Pull Request on GitHub.

## ✅ PR Requirements

### Must-Have

- [ ] Code follows existing style (Black format)
- [ ] Scrapers use bypass stack (`fetch_bypass` or `fetch_page`)
- [ ] No hardcoded secrets or API keys
- [ ] Handles `None`/empty gracefully (no crashes)
- [ ] Yield `Drug` objects (not raw dicts)
- [ ] Tested locally (sample run works)

### Nice-to-Have

- [ ] Docstrings for public functions
- [ ] Type hints
- [ ] Error handling with logging
- [ ] Rate limiting respect
- [ ] Comments for complex logic

## 📦 Code Style

```bash
# Format code
black .

# Type check (optional)
mypy .
```

## 🧪 Testing

```bash
# Test single scraper
python main.py test-source your_source

# Test all scrapers (quick sample)
python main.py test-all
```

## 🔒 Security

- **Never commit secrets** (API keys, tokens, passwords)
- Use environment variables for sensitive data
- Don't scrape aggressively (respect `rate_limit`)

## 🙏 Thank You!

We appreciate all contributions, from bug reports to new scrapers!

---

**Need Help?**
- Open an Issue: [Report Bug](https://github.com/AKIB473/medicine-data-scraper/issues/new?template=bug.md)
- Ask Question: [Discussion](https://github.com/AKIB473/medicine-data-scraper/discussions)
- Contact: @akibuzzaman7 (GitHub)
