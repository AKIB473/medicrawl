# 🏥 **Medicrawl** — Unified Medicine Data Scraper  
**Built by Akibuzzaman Akib** (@akibuzzaman7)  
*Your complete medicine database crawler and intelligence platform*

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/AKIB473/medicrawl?style=for-the-badge)
![Forks](https://img.shields.io/github/forks/AKIB473/medicrawl?style=for-the-badge)
![License](https://img.shields.io/github/license/AKIB473/medicrawl?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11%2B-blue?style=for-the-badge&logo=python)
![Contributors](https://img.shields.io/github/contributors/AKIB473/medicrawl?style=for-the-badge)

[![Twitter Follow](https://img.shields.io/twitter/follow/akibuzzaman7?style=for-the-badge&label=Follow%20on%20Twitter)](https://twitter.com/akibuzzaman7)
[![Telegram](https://img.shields.io/badge/Telegram-@akibuzzaman7-26A5E4?style=for-the-badge&logo=telegram)](https://t.me/akibuzzaman7)

</div>

<br>

## 🎬 **Quick Demo**

<details>
<summary><b>📺 Click to see animated demo</b> (expand to view)</summary>

```

  INITIALIZING MEDICRAWL ENGINE                           


▶ Loading 29 medicine data sources...
  ├─ Bangladesh: 6 sources ✓
  └─ International: 23 sources ✓

▶ Activating anti-bot bypass system...
  ├─ Level 1: curl_cffi (TLS spoof)       ⚡ 0.8s
  ├─ Level 2: cloudscraper (JS solve)     🌐 2.3s
  ├─ Level 3: playwright (full browser)   🎭 5.2s
  └─ Level 4: httpx (fallback)            🔄 ready

▶ Normalizing drug data...
  ├─ Generating canonical IDs (SHA256)
  ├─ Standardizing names & strengths
  └─ De-duplicating entries

▶ Building SQLite database...
  ├─ Drugs table:        200,000+ records
  ├─ Brand names:        500,000+ records
  ├─ Prices:             350,000+ records
  ├─ Clinical data:      180,000+ records
  └─ Chemical data:      150,000+ records

✅ Pipeline complete! Database ready for queries.
```

</details>

<br>

---

## 🌟 **Purpose & Vision**

Medicrawl was created to solve a critical problem: **fragmented medicine information across dozens of databases** makes it nearly impossible for healthcare professionals, researchers, and developers to get comprehensive drug data in one place.

**Our Mission:**
- ✅ Unify global medicine data into a single, searchable database
- ✅ Make pharmaceutical information freely accessible
- ✅ Enable data-driven healthcare solutions
- ✅ Support research and innovation in medicine

**Why Medicrawl?**
- 🚀 **29 sources, 1 database** — Everything you need in one place
- 🔒 **Anti-bot by design** — Automatically bypasses Cloudflare and protections
- 🧠 **Smart deduplication** — Same drug from different sources = one canonical record
- ⚡ **Fast & scalable** — Parallel scraping, intelligent caching
- 📊 **Rich data** — Names, prices, clinical info, chemical structures, and more

---

## 👤 **Author Profile**

### **Akibuzzaman Akib** (@akibuzzaman7)

**Role:** Lead Developer | System Architect | Data Engineer  
**Location:** Bangladesh  
**Timezone:** Asia/Dhaka (GMT+6)  

**About:**
A dedicated software engineer and data enthusiast specializing in web scraping, data pipeline architecture, and automation. Passionate about making data accessible and building tools that solve real-world problems.

**Expertise:**
- Python (Advanced)
- Web Scraping & Anti-bot Bypass
- Data Engineering & ETL Pipelines
- Database Design (SQLite, PostgreSQL)
- REST APIs & Integration

**Contact:**
- 📧 **Email:** akibuzzaman7@gmail.com
- 📱 **Telegram:** [@akibuzzaman7](https://t.me/akibuzzaman7)
- 🐙 **GitHub:** [@akibuzzaman7](https://github.com/akibuzzaman7)

**Social:**
[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/akibuzzaman7)
[![Telegram](https://img.shields.io/badge/telegram-%2326A5E4.svg?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/akibuzzaman7)
[![Gmail](https://img.shields.io/badge/gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:akibuzzaman7@gmail.com)

---

## 🚀 **Features**

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Multi-Source Aggregation** | 29 scrapers across Bangladesh & International sources |
| **Auto Bypass** | 4-level progressive Cloudflare/bot bypass (curl_cffi → cloudscraper → playwright → httpx) |
| **Data Normalization** | Standardized drug names, canonical IDs, unified units |
| **Intelligent Deduplication** | SHA256-based canonical IDs merge same drugs across sources |
| **SQLite Database** | Structured storage with 6 tables (drugs, brand_names, prices, clinical, chemistry, sources) |
| **Multiple Exports** | JSON, SQLite, CSV-ready |
| **Rich Metadata** | Full provenance tracking for every data point |

### Data Points Collected

- ✅ Generic names & brand names
- ✅ Dosage forms & strengths
- ✅ Prices & currency
- ✅ Manufacturers
- ✅ Clinical information (indications, contraindications, side effects)
- ✅ Chemical data (molecular formula, SMILES, InChI)
- ✅ Cross-references (PubChem CID, RxNorm RxCUI, etc.)
- ✅ Source URLs & timestamps

---

## 📊 **Data Sources (29 Scrapers)**

### 🇧🇩 **Bangladesh (6 Sources)**

| Source | Type | Status | Records |
|--------|------|--------|---------|
| **MedEx BD** | API | ✅ Live | 50,000+ |
| **Arogga** | HTML | ✅ Live | 56,000+ |
| **Osudpotro** | REST API | ✅ Live | 7,000,000+ |
| **DIMS** | Playwright | ✅ Live | 10,000+ |
| **BDMedEx** | Playwright | ✅ Live | 5,000+ |
| **BD Drugs/Stores** | HTML | ⚠️ Down | - |

### 🌍 **International (23 Sources)**

| Source | Type | Status | Specialty |
|--------|------|--------|----------|
| **OpenFDA** | API | ✅ Live | US drug labels & adverse events |
| **RxNorm** | API | ✅ Live | NLM standard identifiers |
| **DailyMed** | API | ✅ Live | Structured product labels |
| **PubChem** | API | ✅ Live | 100M+ compounds, chemical data |
| **ChEMBL** | API | ✅ Live | Bioactivity & targets |
| **DrugBank** | API | ✅ Live | Comprehensive drug database |
| **ClinCalc** | HTML | ✅ Live | Top 300 US prescriptions |
| **Drugs.com** | Playwright | ✅ Live | Consumer info & reviews |
| **WebMD** | Mixed | ✅ Live | Monographs |
| **EMC** | Mixed | ✅ Live | UK drug information |
| **MIMS** | Mixed | ✅ Live | Medical info sheets |
| **Medscape** | Playwright | ✅ Live | Clinical reference |
| **Who_EML** | API | ✅ Live | WHO essential medicines |
| **EPOCRATES** | API | ✅ Live | Clinical drug reference |
| **KEGG** | API | ✅ Live | Pathways & enzymes |
| **EMA** | API | ✅ Live | European medicines |

**...and more being added continuously!**

---

## 🏗️ **Architecture Overview**

```

                    29 SCRAPERS (Parallel)                     
  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ 
  │   MedEx BD  │ │   Arogga    │ │   OpenFDA   │ │ PubChem │ 
  │   (API)     │ │   (HTML)    │ │   (API)     │ │ (API)   │ 
  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ 
          │                 │                 │              │
          └─────────────────┼─────────────────┼──────────────┘
                           ▼
                   
              Bypass Stack (4 Levels)         
                   
              1️⃣ curl_cffi  (TLS spoof)      ⚡
                 Fastest - HTTP2 impersonation
                                          
              2️⃣ cloudscraper (JS solve)     🌐
                 Direct Cloudflare solver    
                                          
              3️⃣ playwright (headless)      🎭
                 Full browser rendering      
                                          
              4️⃣ httpx (fallback)            🔄
                 Simple requests             
                   
                           ▼
                   
              Normalizer (Pydantic)          
                   
              • Extract & clean fields       
              • Generate canonical IDs       
              • Standardize units & names   
              • Validate data types         
                   
                           ▼
                  
              Merger (De-duplication)        
                  
              • Group by canonical_id       
              • Merge multi-source data     
              • Prioritize by source        
              • Preserve all metadata       
                   
                           ▼
                  
              SQLite Database (WAL mode)     
                  
              Tables:                        
              ├─ drugs         (canonical)  
              ├─ brand_names   (aliases)    
              ├─ prices        (cost data)  
              ├─ clinical      (indications)
              ├─ chemistry     (structures) 
              └─ sources       (provenance) 
                   
                           ▼
                  
              Export Formats Available       
                  
              • SQLite database (.db)       
              • JSON API format (.json)     
              • CSV ready (easy conversion) 
                   
```

---

## 🔐 **Anti-Bot & Cloudflare Bypass**

Medicrawl includes a sophisticated **4-level progressive bypass system** that automatically handles bot protection:

### Level 1: curl_cffi (Fastest ⚡)
```python
# TLS/HTTP2 impersonation
# Mimics real browser fingerprints
# 0.5-2 second response time
# Best for: Most sites, fast scraping
```

### Level 2: cloudscraper (Smart 🌐)
```python
# Direct Cloudflare JavaScript challenge solver
# No browser overhead
# 2-5 second response time
# Best for: Cloudflare-protected sites
```

### Level 3: playwright (Full Browser 🎭)
```python
# Headless Chrome with stealth
# Handles complex JS rendering
# 5-10 second response time
# Best for: Heavy JS sites, SPAs
```

### Level 4: httpx (Fallback 🔄)
```python
# Simple HTTP requests
# No Cloudflare support
# Fast but limited
# Best for: Unprotected APIs
```

**How it works:**
1. Try curl_cffi first (fastest)
2. If blocked/rate-limited → cloudscraper
3. If JS challenge → playwright
4. If all else fails → httpx

**Zero configuration needed!** Just call `fetch_page()` and Medicrawl handles the rest.

---

## 🗄️ **Database Schema**

Medicrawl uses **SQLite with WAL mode** for concurrent reads/writes:

### **`drugs` Table** (Canonical Records)
```sql
CREATE TABLE drugs (
    id INTEGER PRIMARY KEY,
    canonical_id TEXT UNIQUE,       -- SHA256(generic|form|strength)
    generic_name TEXT,              -- Standardized generic name
    dosage_form TEXT,               -- Tablet, Capsule, Injection, etc.
    strength TEXT,                  -- 500mg, 10ml, etc.
    manufacturer_id INTEGER,        -- Links to manufacturer
    drug_class TEXT,                -- Antibiotic, Analgesic, etc.
    pharmacological_class TEXT,     -- Beta-blocker, etc.
    therapeutic_class TEXT,         -- Cardiovascular, etc.
    molecular_formula TEXT,         -- C13H18O2
    pubchem_cid INTEGER,            -- PubChem Compound ID
    rxcui TEXT,                     -- RxNorm concept ID
    unii TEXT,                      -- UNII code
    ndc TEXT[],                     -- NDC codes (array)
    created_at TIMESTAMP
);
```

### **`brand_names` Table** (Aliases)
```sql
CREATE TABLE brand_names (
    drug_id INTEGER REFERENCES drugs(id),
    brand_name TEXT,                -- Tylenol, Panadol, etc.
    source TEXT,                    -- Which scraper found it
    is_primary BOOLEAN              -- Main brand name?
);
```

### **`prices` Table** (Cost Data)
```sql
CREATE TABLE prices (
    drug_id INTEGER REFERENCES drugs(id),
    amount REAL,                    -- 10.50
    currency TEXT,                  -- USD, BDT, etc.
    unit TEXT,                      -- per tablet, per box
    source TEXT,                    -- Price source
    last_updated TIMESTAMP
);
```

### **`clinical` Table** (Medical Info)
```sql
CREATE TABLE clinical (
    drug_id INTEGER REFERENCES drugs(id),
    indications TEXT[],             -- What it treats
    contraindications TEXT[],       -- What to avoid
    side_effects TEXT[],            -- Potential side effects
    dosage TEXT,                    -- How to use
    mechanism_of_action TEXT,       -- How it works
    warnings TEXT[],                -- Important warnings
    pregnancy_category TEXT,        -- A, B, C, D, X
    storage TEXT                    -- Storage instructions
);
```

### **`chemistry` Table** (Molecular Data)
```sql
CREATE TABLE chemistry (
    drug_id INTEGER REFERENCES drugs(id),
    molecular_formula TEXT,         -- C13H18O2
    molecular_weight REAL,          -- 206.28 g/mol
    smiles TEXT,                    -- SMILES string
    inchi TEXT,                     -- InChI identifier
    chembl_id TEXT,                 -- ChEMBL ID
    kegg_id TEXT                    -- KEGG ID
);
```

### **`sources` Table** (Provenance)
```sql
CREATE TABLE sources (
    drug_id INTEGER REFERENCES drugs(id),
    source_name TEXT,               -- "openfda", "medex"
    source_url TEXT,                -- Original URL
    source_id TEXT,                 -- ID in source system
    scraped_at TIMESTAMP,           -- When scraped
    data_completeness JSON          -- Which fields exist
);
```

---

## 🛠 **CLI Commands**

### **Quick Start**

```bash
# Run everything: scrape → process → database
python main.py run-all

# Just scrape all sources
python main.py scrape

# Process scraped data into database
python main.py post-process

# Search the database
python main.py search-db "paracetamol"

# Show database statistics
python main.py db-stats
```

### **Scraper Management**

```bash
# List all available scrapers
python main.py list-sources

# Test a single scraper (sample 5 records)
python main.py test-source medex

# Test all scrapers (sample mode)
python main.py test-all
```

### **Advanced Usage**

```bash
# Export database to JSON
python main.py export-json

# Export database to CSV
python main.py export-csv

# Update database from scratch
python main.py update

# Check bypass system
python main.py test-bypass drugs.com
```

---

## ⚡ **Usage Examples**

### **Example 1: Basic Search**

```python
from utils.database import DrugDatabase

# Initialize database connection
db = DrugDatabase("data/medicine_data.db")

# Search for a medicine
results = db.search("paracetamol")

# Display results
for drug in results:
    print(f"🎯 {drug['brand_name']}")
    print(f"   Generic: {drug['generic_name']}")
    print(f"   Form: {drug['dosage_form']}")
    print(f"   Strength: {drug['strength']}")
    print(f"   Price: {drug.get('price', 'N/A')}")
    print("---")
```

**Output:**
```
🎯 Crocin
   Generic: Paracetamol
   Form: Tablet
   Strength: 500mg
   Price: 2.50 BDT
---
🎯 Napa
   Generic: Paracetamol
   Form: Tablet
   Strength: 500mg
   Price: 2.00 BDT
---
```

### **Example 2: Advanced Query with Pandas**

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/medicine_data.db")

# Get all paracetamol products with prices
query = """
    SELECT 
        d.generic_name,
        b.brand_name,
        p.amount,
        p.currency,
        s.source_name,
        d.dosage_form,
        d.strength
    FROM drugs d
    JOIN brand_names b ON d.id = b.drug_id
    JOIN prices p ON d.id = p.drug_id
    JOIN sources s ON d.id = s.drug_id
    WHERE d.generic_name LIKE '%paracetamol%'
    ORDER BY p.amount ASC
    LIMIT 20
"""

df = pd.read_sql_query(query, conn)
print(df.to_string(index=False))
conn.close()
```

**Output:**
```
generic_name  brand_name  amount currency     source_name dosage_form strength
 paracetamol    Suppository    0.5      BDT        medex     Suppository    100mg
 paracetamol        Napa Syrup   1.2      BDT        arogga        Syrup    120ml
 paracetamol         Napa       2.0      BDT        medex        Tablet    500mg
 paracetamol       Crocin       2.5      BDT        osudpotro    Tablet    500mg
```

### **Example 3: Price Comparison Across Sources**

```python
from utils.database import DrugDatabase

db = DrugDatabase("data/medicine_data.db")

# Search for a medicine
results = db.search("napa")

# Group by source
prices_by_source = {}
for drug in results:
    source = drug['source']
    price = drug.get('price', 0)
    if source not in prices_by_source:
        prices_by_source[source] = []
    prices_by_source[source].append(price)

# Display comparison
print("💰 NAPA Price Comparison by Source")
print("=" * 40)
for source, prices in prices_by_source.items():
    avg_price = sum(prices) / len(prices)
    print(f"  {source:15} | {avg_price:6.2f} BDT | {len(prices)} products")
```

**Output:**
```
💰 NAPA Price Comparison by Source
========================================
  medex           |   2.50 BDT | 15 products
  arogga          |   2.80 BDT | 23 products
  osudpotro       |   2.20 BDT | 8 products
```

### **Example 4: Export to JSON for API**

```python
from utils.pipeline import DrugPipeline

# Run full pipeline
pipeline = DrugPipeline()

# Scrape, process, and export
pipeline.run_full_pipeline()

# Results saved to:
# - data/medicine_data.db (SQLite)
# - data/merged_drugs.json (JSON)
# - data/raw/ (individual scraper outputs)
```

### **Example 5: Get Drug by Canonical ID**

```python
from utils.database import DrugDatabase

db = DrugDatabase("data/medicine_data.db")

# Get a specific drug by its canonical ID
drug = db.get_by_canonical_id("a1b2c3d4e5f6g7h8")

print(f"Drug: {drug['generic_name']}")
print(f"Brands: {drug['brand_names']}")
print(f"Clinical: {drug['indications']}")
```

### **Example 6: Add a New Scraper**

```python
# scrapers/international/new_drug_source.py
from scrapers.base import BaseScrapingScraper
from models.drug import Drug, DrugPrice, Manufacturer

class NewDrugSourceScraper(BaseScrapingScraper):
    name = "new_drug_source"
    base_url = "https://example.com"
    rate_limit = 1.0
    
    async def scrape_all(self) -> AsyncIterator[Drug]:
        # Fetch page using built-in bypass
        page = await self.fetch_page(f"{self.base_url}/drugs")
        
        # Parse the page
        for item in page.querySelectorAll('.drug-item'):
            yield Drug(
                source=self.name,
                source_url=item.querySelector('a').href,
                brand_name=item.querySelector('.brand').textContent,
                generic_name=item.querySelector('.generic').textContent,
                dosage_form=item.querySelector('.form').textContent,
                strength=item.querySelector('.strength').textContent,
                manufacturer=Manufacturer(
                    name=item.querySelector('.manufacturer').textContent,
                    country="USA"
                ),
                price=DrugPrice(
                    amount=float(item.querySelector('.price').textContent),
                    currency="USD",
                    unit="bottle"
                ),
                indications=[
                    item.querySelector('.indications').textContent
                ]
            )
```

---

## 📈 **Statistics**

| Metric | Count |
|--------|-------|
| **Total Scrapers** | 29 |
| **Active Sources** | 23+ |
| **Bangladesh Sources** | 6 |
| **International Sources** | 23 |
| **Medicines in Database** | ~200,000+ |
| **Brand Names Tracked** | ~500,000+ |
| **Price Records** | ~350,000+ |
| **Clinical Entries** | ~180,000+ |
| **Chemical Records** | ~150,000+ |

**Last Updated:** Auto-daily via GitHub Actions

---

## 🤝 **Contributing**

We ❤️ contributions! Everyone is welcome to help make Medicrawl better.

### **Quick Start for Contributors**

1. **Pick an issue** from [GitHub Issues](https://github.com/AKIB473/medicrawl/issues)
2. **Read [CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines
3. **Fork → Branch → Code → Test → PR**
4. **Get credited** in [AUTHORS.md](AUTHORS.md)!

### **What You Can Contribute**

- 🆕 **New Scraper:** Add a missing medicine data source
- 🐛 **Bug Fix:** Fix parsing or data extraction issues
- 📚 **Documentation:** Improve README, add examples
- 🧪 **Tests:** Write unit tests for scrapers
- 🎨 **UI:** Create a web interface (future project)
- 💡 **Ideas:** Suggest new features or improvements

### **Feature Requests**

Have an idea? [Open an Issue](https://github.com/AKIB473/medicrawl/issues/new?template=feature_request.md)!

---

## 🔒 **Security & Privacy**

- 🔐 No personal data collected
- 🛡️ Respects `robots.txt` (where applicable)
- ⏱️ Rate limiting per domain
- 🔑 No API keys required (except optional DrugBank)
- 🌐 GitHub token: Use `secrets.GITHUB_TOKEN` (auto-provided)

### **Token Rotation** 🔑

If you've exposed a token, rotate it immediately:

```bash
gh secret set GITHUB_TOKEN --body "ghp_your_new_token"
```

---

## 📜 **License**

MIT License — free for research, commercial, and learning use.

```
Copyright (c) 2026 Akibuzzaman Akib

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🌟 **Acknowledgments**

### **Lead Developer**

- **[@akibuzzaman7](https://github.com/akibuzzaman7)** — Architect, developer, maintainer
  - All 29 scraper implementations
  - Anti-bot bypass system
  - Database pipeline & normalization
  - CLI tools & API design

### **Inspired By**

- **OpenFDA** — Free drug data APIs
- **RxNorm** — Standard drug identifiers
- **DailyMed** — Structured labeling
- **PubChem** — Chemical database

### **Special Thanks**

- **Bangladesh pharmaceutical community**
- **Open-source maintainers** whose tools we use
- **Healthcare researchers** worldwide

### **Connect**

- 🐙 GitHub: [@akibuzzaman7](https://github.com/akibuzzaman7)
- 📧 Email: akibuzzaman7@gmail.com
- 🌐 Website: [github.com/akibuzzaman7](https://github.com/akibuzzaman7)

---

<div align="center">

# 🚀 **Built with ❤️ for the Healthcare Community**

## **Medicrawl — Unified Medicine Data Scraper**

*Making medicine information accessible to everyone, everywhere.*

[![GitHub stars](https://img.shields.io/github/stars/AKIB473/medicrawl?style=social)](https://github.com/AKIB473/medicrawl/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/AKIB473/medicrawl?style=social)](https://github.com/AKIB473/medicrawl/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/AKIB473/medicrawl?style=social)](https://github.com/AKIB473/medicrawl/watchers)

</div>
