# 💊 Medicrawl — Unified Medicine Data Crawler

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/AKIB473/medicrawl?style=for-the-badge)]
[![Forks](https://img.shields.io/github/forks/AKIB473/medicrawl?style=for-the-badge)]
[![License](https://img.shields.io/github/license/AKIB473/medicrawl?style=for-the-badge)]
[![Python](https://img.shields.io/badge/python-3.11%2B-blue?style=for-the-badge&logo=python)]
[![Contributors](https://img.shields.io/github/contributors/AKIB473/medicrawl?style=for-the-badge)]

</div>

---

## 🌟 Overview

**Medicrawl** is a backend-grade production pipeline that unifies medicine information from multiple global sources into one clean, deduplicated, structured database. Built for researchers, pharmacists, developers, and healthcare innovators.

*Created & maintained with ❤️ by **Akibuzzaman Akib** (@akibuzzaman7)*

---

## 🤝 Contributing

We ❤️ contributions! 👉 **[Read CONTRIBUTING.md](CONTRIBUTING.md)** for detailed guidelines.

### 🏆 Contributors

| Contributor | Role | Contributions |
|-------------|------|---------------|
| **[AKIBUZZAMAN AKIB](https://github.com/AKIB473)** | 🥇 Lead Developer | All crawlers, pipeline, database design |
| You? | 🥈 Contributor | *(Add your name via PR!)* |

Every contributor credited in [AUTHORS.md](AUTHORS.md)!

---

## 📊 Data Sources (29 Crawlers)

### Bangladesh (6)
- **MedEx BD** — Local drug database with clinical info
- **Arogga** — 56k+ products with pricing
- **Osudpotro** — Government registry (7L+ items)
- **DIMS** — Drug inventory management
- **BDMedEx** — Medicine marketplace
- **BD Drugs/Stores** — Local pharmacy listings

### International (23)
- **OpenFDA** — US drug labels, adverse events
- **RxNorm** — NLM standard identifiers
- **DailyMed** — Structured product labels
- **PubChem** — 100M+ compounds, chemical data
- **ChEMBL** — Bioactivity database
- **DrugBank** — Comprehensive drug database
- **ClinCalc** — Top prescribed drugs
- **Drugs.com** — Consumer drug information
- **WebMD/EMC/MIMS** — Monographs, PIL

---

## 🏗️ Architecture

```

  29 CRAWLERS (Parallel)     
  BD:6  API:15  Crawl:8      

         ▼
  Bypass Stack (4 Levels)     
  1.crawler_cffi  TLS spoof ⚡   
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

**Progressive 4-Level Crawler Stack** — Fully automatic:

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
- Automatic retry — transparent to crawler code
- No API keys required — fully self-contained

---

## 🗄️ Database Schema

```sql
CREATE TABLE drugs (
    id INTEGER PRIMARY KEY,
    canonical_id TEXT UNIQUE,
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

CREATE TABLE brand_names (...);
CREATE TABLE prices (...);
CREATE TABLE clinical (...);
CREATE TABLE chemistry (...);
CREATE TABLE sources (...);
```

---

## 🛠 CLI Commands

```bash
# Full pipeline: crawl → process → DB
python main.py run-all

# Individual steps
python main.py crawl           # Run all crawlers, save raw JSON
python main.py post-process    # Merge, normalize, build SQLite
python main.py search-db "napa" # Search database (SQL + FTS5)
python main.py db-stats        # Show statistics

# Crawler management
python main.py list-sources    # List all available crawlers
python main.py test-source <name>  # Test one crawler
```

### Output Files

```
data/
├── raw/                      # Raw JSON from each crawler
├── merged_drugs.json         # Unified, deduplicated JSON
└── medicine_data.db          # SQLite database (WAL)
```

---

## 🧬 Data Normalization

**Canonical ID:** `sha256(generic|form|strength)[:16]`

Same medicine from different sources → same canonical ID → merged.

| Field | Priority Order |
|-------|----------------|
| Clinical info | MedEx > DIMS > BDMedEx > OpenFDA |
| Chemistry | PubChem > ChEMBL > DrugBank |
| Prices | Arogga > Osudpotro > MedEx |

### Graceful None Handling

- Missing fields → `NULL` (never crash)
- Empty lists → `[]` (never `None`)
- Optional fields → Pydantic `Optional[T]`

---

## 🎬 Usage Examples

### Example 1: Search Database

```python
from utils.database import DrugDatabase

db = DrugDatabase("data/medicine_data.db")
results = db.search("paracetamol")

for drug in results:
    print(f"Brand: {drug['brand_name']}")
    print(f"Generic: {drug['generic_name']}")
    print(f"Price: {drug.get('price', 'N/A')}")
    print("---")
```

### Example 2: Compare Prices

```python
import sqlite3, pandas as pd

conn = sqlite3.connect("data/medicine_data.db")
df = pd.read_sql_query("""
    SELECT d.generic_name, b.brand_name, p.amount, s.source_name
    FROM drugs d
    JOIN brand_names b ON d.id = b.drug_id
    JOIN prices p ON d.id = p.drug_id
    JOIN sources s ON d.id = s.drug_id
    WHERE d.generic_name LIKE '%napa%'
    ORDER BY p.amount
""", conn)
print(df)
```

### Example 3: Export to JSON

```python
from utils.pipeline import DrugPipeline

pipeline = DrugPipeline()
pipeline.run_full_pipeline()
# Output: data/merged_drugs.json
```

---

## 📈 Statistics

| Metric | Count |
|--------|-------|
| **Total Crawlers** | 29 |
| **Active Sources** | 23+ |
| **Bangladesh Sources** | 6 |
| **Medicines in DB** | ~200k+ |

---

## 🔒 Security

- No personal data
- Rate limiting per domain
- No API keys required

---

## 📜 License

MIT — free for research, commercial, and learning.

---

## ❤️ Acknowledgments

- **Lead Developer:** [AKIBUZZAMAN](https://github.com/AKIB473)

<div align="center">

**Built with ❤️ for the healthcare community**  
Medicrawl — Unified Medicine Data Crawler  

</div>
