# 💊 Medicine Data Scraper — Unified Pharmaceutical Intelligence

<div align="center">

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-black?style=for-the-badge)](https://github.com/psf/black)

</div>

---

## 🌟 Overview

**Medicine Data Scraper** is a backend-grade production pipeline that unifies pharmaceutical information from multiple global sources into one clean, deduplicated, structured database. Built for researchers, pharmacists, developers, and healthcare innovators.

*Created & maintained with ❤️ by **Akibuzzaman Akib** (@akibuzzaman7)*

---

## 🤝 Contributing

We ❤️ contributions! 👉 **[Read CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines.

### 🏆 Contributors

| Contributor | Role | Contributions |
|-------------|------|---------------|
| **[@akibuzzaman7](https://github.com/akibuzzaman7)** | 🥇 Lead Developer | All scrapers, bypass system, pipeline, database design |
| You? | 🥈 Contributor | *(Add your name via PR!)* |

Every contributor credited in [AUTHORS.md](AUTHORS.md)!

---

## 📊 Data Sources (29 Scrapers)

### Bangladesh (6)
- MedEx BD — Local drug database with clinical info
- Arogga — 56k+ products with pricing
- Osudpotro — Government registry (7L+ items)
- DIMS — Drug inventory management
- BDMedEx — Medicine marketplace
- BD Drugs/Stores — Local pharmacy listings

### International (23)
- OpenFDA — US drug labels, adverse events
- RxNorm — NLM standard identifiers
- DailyMed — Structured product labels
- PubChem — 100M+ compounds
- ChEMBL — Bioactivity database
- DrugBank — Comprehensive drug database
- ClinCalc — Top prescribed drugs
- Drugs.com — Consumer drug information
- WebMD/EMC/MIMS — Monographs

---

## 🏗️ Architecture

```

  29 SCRAPERS (Parallel)     
  BD:6  API:15  Scrape:8      

         ▼
  Bypass Stack (4 Levels)     
  1.curl_cffi  TLS spoof ⚡    
  2.cloudscraper  JS solve 🌐 
  3.playwright  Full browser 🎭
  4.httpx  fallback 🔄        

         ▼
  Normalizer (Pydantic)       
  • Canonical IDs (hash)      
  • Standardize names         
  • Handle None gracefully    

         ▼
  Merger (De-duplication)     
  • Group by canonical_id     
  • Prioritize sources        
  • Merge multi-source fields 

         ▼
  SQLite Database (WAL)       
  • drugs, brand_names        
  • prices, clinical          
  • chemistry, sources        

         ▼
  Export: DB + JSON           

```

---

## 🔐 Anti-Bot & Cloudflare Bypass

**Progressive 4-Level Stack** — Fully automatic:

```
1️⃣ curl_cffi    → TLS/HTTP2 impersonation (0.5-2s) ⚡ Fastest
   ↓ (if rate-limited / JS challenge)
2️⃣ cloudscraper → Direct Cloudflare solver (2-5s) 🌐
   ↓ (if blocked / CAPTCHA)
3️⃣ playwright   → Headless Chrome (5-10s) 🎭 Full render
   ↓ (if all else fails)
4️⃣ httpx        → Simple fallback (no CF) 🔄
```

- Per-domain sessions maintain cookies/CF clearance
- Automatic retry — transparent to scraper code
- No API keys required — fully self-contained

---

## 🗄️ Database Schema

**Main Tables:**
- `drugs` — Canonical drugs (one row per unique drug)
- `brand_names` — Brand name aliases
- `prices` — Pricing data
- `clinical` — Clinical information
- `chemistry` — Chemical data
- `sources` — Source provenance

```sql
CREATE TABLE drugs (
    id INTEGER PRIMARY KEY,
    canonical_id TEXT UNIQUE,       -- SHA256(generic|form|strength)
    generic_name TEXT,
    dosage_form TEXT,
    strength TEXT,
    manufacturer_id INTEGER,
    drug_class TEXT,
    pharmacological_class TEXT,
    therapeutic_class TEXT,
    molecular_formula TEXT,
    pubchem_cid INTEGER,
    rxcui TEXT,
    created_at TIMESTAMP
);

CREATE TABLE brand_names (
    drug_id INTEGER REFERENCES drugs(id),
    brand_name TEXT,
    source TEXT,
    is_primary BOOLEAN
);

CREATE TABLE prices (
    drug_id INTEGER REFERENCES drugs(id),
    amount REAL,
    currency TEXT,
    unit TEXT,
    source TEXT,
    last_updated TIMESTAMP
);

CREATE TABLE clinical (
    drug_id INTEGER REFERENCES drugs(id),
    indications TEXT[],
    contraindications TEXT[],
    side_effects TEXT[],
    dosage TEXT,
    mechanism_of_action TEXT,
    warnings TEXT[]
);

CREATE TABLE chemistry (
    drug_id INTEGER REFERENCES drugs(id),
    molecular_formula TEXT,
    molecular_weight REAL,
    smiles TEXT,
    inchi TEXT,
    chembl_id TEXT,
    kegg_id TEXT
);

CREATE TABLE sources (
    drug_id INTEGER REFERENCES drugs(id),
    source_name TEXT,
    source_url TEXT,
    source_id TEXT,
    scraped_at TIMESTAMP
);
```

---

## 🛠 CLI Commands

```bash
# Full pipeline: scrape → process → DB
python main.py run-all

# Individual steps
python main.py scrape          # Run all scrapers, save raw JSON
python main.py post-process    # Merge, normalize, build SQLite
python main.py search-db "napa" # Search database (SQL + FTS5)
python main.py db-stats        # Show statistics

# Scraper management
python main.py list-sources    # List all available scrapers
python main.py test-source <name>  # Test one scraper (sample 5 drugs)
```

### Output Files

```
data/
├── raw/                      # Raw JSON from each scraper
│   ├── medex.json
│   ├── openfda.json
│   └── ...
├── merged_drugs.json         # Unified, deduplicated JSON
└── medicine_data.db          # SQLite database (WAL mode)
```

---

## 🧬 Data Normalization

### Canonical ID Generation

```python
canonical_id = sha256(
    f"{generic_name.lower()}|{dosage_form.lower()}|{strength}"
).hexdigest()[:16]
```

Same drug from different sources → same canonical ID → merged into one row.

### Field Prioritization (Multi-Source Merge)

| Field | Priority Order |
|-------|----------------|
| Clinical info | MedEx > DIMS > BDMedEx > OpenFDA |
| Chemistry | PubChem > ChEMBL > DrugBank |
| Prices | Arogga > Osudpotro > MedEx |
| Generic names | MedEx > DIMS > RxNorm |

### Graceful None Handling

- Missing fields → `NULL` (never crash)
- Empty lists → `[]` (never `None`)
- Optional fields → Pydantic `Optional[T]`

---

## 🎬 Usage Examples

### Example 1: Search Database

```python
import sqlite3, pandas as pd

conn = sqlite3.connect("data/medicine_data.db")
df = pd.read_sql_query("""
    SELECT d.generic_name, b.brand_name, p.amount, s.source_name
    FROM drugs d
    JOIN brand_names b ON d.id = b.drug_id
    JOIN prices p ON d.id = p.drug_id
    JOIN sources s ON d.id = s.drug_id
    WHERE d.generic_name LIKE '%paracetamol%'
    ORDER BY p.amount
    LIMIT 10
""", conn)
print(df)
```

### Example 2: Export to JSON

```python
from utils.pipeline import DrugPipeline

pipeline = DrugPipeline()
pipeline.run_full_pipeline()
# Output: data/merged_drugs.json
```

### Example 3: Get Drug by Canonical ID

```python
from utils.database import DrugDatabase

db = DrugDatabase("data/medicine_data.db")
results = db.search("napa")
for r in results:
    print(r)
```

---

## 📈 Current Statistics

| Metric | Count |
|--------|-------|
| **Total Scrapers** | 29 |
| **Active Sources** | 23+ |
| **Bangladesh Sources** | 6 |
| **International Sources** | 23 |
| **Drugs in DB** | ~200k+ |
| **Brands Tracked** | ~500k+ |

---

## 🔒 Security & Privacy

- No personal data collected
- Respects robots.txt (where applicable)
- Rate limiting per domain
- No API keys required (except optional DrugBank)
- GitHub token: Use `secrets.GITHUB_TOKEN` (auto-provided)

### Token Rotation 🔑

Rotate exposed tokens immediately:
```bash
gh secret set GITHUB_TOKEN --body "ghp_your_new_token"
```

---

## 📜 License

MIT License — free for research, commercial, and learning use.

---

## ❤️ Acknowledgments

- **Lead Developer:** [@akibuzzaman7](https://github.com/akibuzzaman7)
- **Inspired by:** OpenFDA, RxNav, DailyMed
- **Special thanks:** Bangladesh pharmaceutical community

---

<div align="center">

**Built with ❤️ for the healthcare community**  
Medicine Data Scraper — Unified Pharmaceutical Intelligence  

</div>
