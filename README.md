# 💊 Medicrawl — Unified Medicine Data Scraper

<div align="center">

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-black?style=for-the-badge)](https://github.com/psf/black)

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
| **[@akibuzzaman7](https://github.com/akibuzzaman7)** | 🥇 Lead Developer | All scrapers, bypass system, pipeline, database design |
| You? | 🥈 Contributor | *(Add your name via PR!)* |

Every contributor credited in [AUTHORS.md](AUTHORS.md)!

### 🚀 How to Contribute

1. **Pick an issue** from GitHub Issues
2. **Read CONTRIBUTING.md** for guidelines
3. **Fork → Branch → Code → Test → PR**
4. **Get credited** in the project!

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
- PubChem — 100M+ compounds, chemical data
- ChEMBL — Bioactivity database
- DrugBank — Comprehensive drug database
- ClinCalc — Top prescribed drugs
- Drugs.com — Consumer drug information
- WebMD/EMC/MIMS — Monographs, PIL

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
python main.py run-all          # Full pipeline
python main.py scrape           # Run all scrapers
python main.py post-process     # Merge, normalize, build SQLite
python main.py search-db "napa" # Search database
python main.py db-stats         # Show statistics
```

### Output Files

```
data/
├── raw/                      # Raw JSON from scrapers
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

## 🎬 Usage Example

```python
from utils.database import DrugDatabase

db = DrugDatabase("data/medicine_data.db")
results = db.search("paracetamol")
for r in results:
    print(f"{r['brand_name']}: {r['generic_name']}")
```

---

## 📈 Statistics

| Metric | Count |
|--------|-------|
| **Total Scrapers** | 29 |
| **Active Sources** | 23+ |
| **Bangladesh Sources** | 6 |
| **International Sources** | 23 |
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

- **Lead Developer:** [@akibuzzaman7](https://github.com/akibuzzaman7)

<div align="center">

**Built with ❤️ for the healthcare community**  
Medicrawl — Unified Medicine Data Scraper  

</div>
