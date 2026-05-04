# 💊 Medicine Data Scraper — Unified Pharmaceutical Intelligence

<div align="center">

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-black?style=for-the-badge)](https://github.com/psf/black)

</div>

---

## 🌟 Overview

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=700&size=42&duration=3500&pause=1000&color=2E86AB&center=true&vCenter=true&width=650&height=100&lines=MEDICINE+DATA+SCRAPER%3BUnified+Pharmaceutical+Intelligence%3BBuilt+by+Akibuzzaman+Akib"
  alt="Typing SVG" />

</div>

**Medicine Data Scraper** is a backend-grade, production-ready data pipeline that **unifies pharmaceutical information from multiple global sources** into one clean, deduplicated, structured database. Built for researchers, pharmacists, developers, and healthcare innovators.

*Created and maintained with ❤️ by **Akibuzzaman Akib** (@akibuzzaman7)*

---

## 🤝 Contributing

We ❤️ contributions! This project welcomes everyone to help build the most comprehensive pharmaceutical database.

👉 **[Read our full Contributing Guide](CONTRIBUTING.md)**

### 🏆 Contributors

| Contributor | Role | Contributions |
|-------------|------|---------------|
| **[@akibuzzaman7](https://github.com/akibuzzaman7)** | 🥇 Lead Developer | All scrapers, bypass system, pipeline architecture, database design |
| You? | 🥈 Contributor | *(Add your name via PR!)* |

*Every contributor will be credited in [AUTHORS.md](AUTHORS.md)!*

### 🚀 How to Contribute

1. **Pick an issue** from [GitHub Issues](https://github.com/AKIB473/medicine-data-scraper/issues)
2. **Read [CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines
3. **Fork → Branch → Code → Test → PR**
4. **Get credited** in the project!

### 🎯 Good First Issues

- Add a new pharmaceutical data scraper
- Improve drug name normalization
- Add data validation rules
- Enhance search functionality (FTS5)
- Create export formats (CSV, Parquet)
- Write unit tests

---

## 📊 Data Sources

We aggregate pharmaceutical data from multiple sources:

### Bangladesh Sources (6)
- **MedEx BD** — Local drug database with clinical info
- **Arogga** — 56k+ products with pricing
- **Osudpotro** — Government registry (7L+ items)
- **DIMS** — Drug inventory management
- **BDMedEx** — Medicine marketplace
- **BD Drugs/Stores** — Local pharmacy listings

### International Sources (23+)
- **OpenFDA** — US drug labels, adverse events
- **RxNorm** — NLM standard identifiers
- **DailyMed** — Structured product labels
- **PubChem** — 100M+ compounds, chemical data
- **ChEMBL** — Bioactivity database
- **DrugBank** — Comprehensive drug database
- **ClinCalc** — Top prescribed drugs
- **Drugs.com** — Consumer drug information
- **WebMD/EMC/MIMS** — Monographs, PIL

*+ More sources being added continuously*

---

## 🏗️ Architecture

```

        MULTIPLE SCRAPERS (Parallel)           
  ┌───────────┐ ┌───────────┐ ┌─────────┐ 
  │   BD      │ │   API     │ │  Scrape │ 
  │ Sources 6 │ │ Sources   │ │ Sources │ 
  │           │ │ 15+       │ │ 8+      │ 
  └───────────┘ └───────────┘ └─────────┘ 
       │                 │              │
       └─────────────────┼──────────────┘
                        ▼
             
        Bypass Stack (4 Levels)        
             
      1. curl_cffi  (TLS spoof)      ⚡
      2. cloudscraper (JS solve)      🌐
      3. playwright (full browser)   🎭
      4. httpx       (fallback)      🔄
             
                        ▼
             
       Normalizer (Pydantic)          
             
      • Standardize drug names         
      • Canonical IDs (hash)           
      • Clean strengths/forms          
      • Handle None gracefully         
             
                        ▼
             
        Merger (De-duplication)        
             
      • Group by canonical_id          
      • Prioritize sources             
      • Merge multi-source fields      
      • Preserve all metadata          
             
                        ▼
             
        SQLite Database (WAL)          
             
      Tables:                          
      • drugs          (canonical)     
      • brand_names    (aliases)       
      • prices         (currency)      
      • clinical       (indications)   
      • chemistry      (formula)       
      • sources        (provenance)    
             
                        ▼
             
        Export: DB + JSON Files        
             
```

---

## 🔐 Anti-Bot & Cloudflare Bypass

**Progressive 4-Level Stack** — Fully automatic:

```
1️⃣ curl_cffi    → TLS/HTTP2 impersonation (0.5-2s) ⚡
   ↓ (if rate-limited / JS challenge)
2️⃣ cloudscraper → Direct Cloudflare solver (2-5s) 🌐
   ↓ (if blocked / CAPTCHA)
3️⃣ playwright   → Headless Chrome (5-10s) 🎭
   ↓ (if all else fails)
4️⃣ httpx        → Simple fallback 🔄
```

- Per-domain sessions maintain cookies/CF clearance
- Automatic retry — transparent to scraper code
- No API keys required — fully self-contained

---

## 🗄️ Database Schema

### Main Tables

```sql
-- Canonical drugs (one row per unique drug)
CREATE TABLE drugs (
    id INTEGER PRIMARY KEY,
    canonical_id TEXT UNIQUE,       -- SHA256(generic+form+strength)
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
    unii TEXT,
    created_at TIMESTAMP
);

-- Brand name aliases
CREATE TABLE brand_names (
    drug_id INTEGER REFERENCES drugs(id),
    brand_name TEXT,
    source TEXT,
    is_primary BOOLEAN
);

-- Pricing data
CREATE TABLE prices (
    drug_id INTEGER REFERENCES drugs(id),
    amount REAL,
    currency TEXT,
    unit TEXT,
    source TEXT,
    last_updated TIMESTAMP
);

-- Clinical information
CREATE TABLE clinical (
    drug_id INTEGER REFERENCES drugs(id),
    indications TEXT[],
    contraindications TEXT[],
    side_effects TEXT[],
    dosage TEXT,
    mechanism_of_action TEXT,
    warnings TEXT[]
);

-- Chemical data
CREATE TABLE chemistry (
    drug_id INTEGER REFERENCES drugs(id),
    molecular_formula TEXT,
    molecular_weight REAL,
    smiles TEXT,
    inchi TEXT,
    chembl_id TEXT,
    kegg_id TEXT
);

-- Source provenance
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

### Main Commands

```bash
# Full pipeline: scrape → process → DB
python main.py run-all

# Individual steps
python main.py scrape          # Run all scrapers
python main.py post-process    # Merge, normalize, build SQLite
python main.py search-db "napa" # Search database
python main.py db-stats        # Show statistics

# Scraper management
python main.py list-sources    # List all scrapers
python main.py test-source <name>  # Test one scraper
```

### Output Files

```
data/
├── raw/                      # Raw JSON from scrapers
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

Same drug from different sources → same canonical ID → merged.

### Field Prioritization

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
- No API keys required (optional DrugBank)
- GitHub token: Use `secrets.GITHUB_TOKEN`

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
