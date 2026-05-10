#!/usr/bin/env python3
import json, os, sys

ALL_SCRAPERS = [
    'medex', 'dims', 'dgda', 'bdmedex', 'bddrugs', 'bddrugstore',
    'arogga', 'medeasy', 'osudpotro', 'lazzpharma', 'dghs_shr',
    'openfda', 'rxnorm', 'dailymed', 'pubchem', 'chembl',
    'kegg', 'ema', 'drugs_com', 'rxlist', 'webmd',
    'emc', 'mims', 'who_eml', 'medscape', 'epocrates',
    'drugbank', 'pharmgkb', 'clincalc',
]

CATEGORIES = {
    'all': ALL_SCRAPERS,
    'bd': ALL_SCRAPERS[:11],
    'intl': ALL_SCRAPERS[11:26],
    'research': ALL_SCRAPERS[26:],
}

STEALTH_SOURCES = {
    'drugbank', 'rxlist', 'drugs_com', 'mims', 'emc', 'webmd',
    'osudpotro', 'medeasy', 'dgda', 'arogga', 'lazzpharma', 'epocrates',
    'medscape',
}

SHARDS = [
    ('bd-medex-dims', ['medex', 'dims']),
    ('bd-bdmedex-bddrugs', ['bdmedex', 'bddrugs']),
    ('bd-arogga-osudpotro', ['arogga', 'osudpotro']),
    ('bd-rest', ['dgda', 'bddrugstore', 'medeasy', 'lazzpharma', 'dghs_shr']),
    ('intl-api-1', ['openfda', 'rxnorm', 'dailymed']),
    ('intl-api-2', ['pubchem', 'chembl', 'kegg']),
    ('intl-api-3', ['ema', 'who_eml']),
    ('intl-scrape-1', ['drugs_com', 'rxlist']),
    ('intl-scrape-2', ['webmd', 'emc']),
    ('intl-scrape-3', ['mims']),
    ('intl-scrape-4', ['medscape', 'epocrates']),
    ('research-drugbank', ['drugbank']),
    ('research-rest', ['pharmgkb', 'clincalc']),
]

event_name = os.getenv('GITHUB_EVENT_NAME', '')
sources_input = (os.getenv('INPUT_SOURCES') or '').strip()
category = (os.getenv('INPUT_CATEGORY') or 'all').strip().lower()
fullscrape = (os.getenv('INPUT_FULLSCRAPE') or 'false').strip().lower() == 'true'

if event_name == 'schedule':
    selected = list(ALL_SCRAPERS)
    use_fullscrape = True
else:
    if sources_input:
        selected = [s.strip() for s in sources_input.split(',') if s.strip()]
        use_fullscrape = fullscrape
    else:
        if category not in CATEGORIES:
            print(f'Unsupported category: {category}', file=sys.stderr)
            sys.exit(1)
        selected = list(CATEGORIES[category])
        use_fullscrape = fullscrape or category == 'all'

invalid = sorted(set(selected) - set(ALL_SCRAPERS))
if invalid:
    print(f"Unknown sources: {', '.join(invalid)}", file=sys.stderr)
    sys.exit(1)

selected_set = set(selected)
matrix = []
for shard_name, shard_sources in SHARDS:
    picked = [s for s in shard_sources if s in selected_set]
    if picked:
        matrix.append({
            'name': shard_name,
            'sources_csv': ' '.join(picked),
            'source_count': len(picked),
            'needs_playwright': any(s in STEALTH_SOURCES for s in picked),
        })

# Diagnostics to stderr
print(f'Selected sources ({len(selected)}): {", ".join(selected)}', file=sys.stderr)
print(f'Shards to run: {len(matrix)}', file=sys.stderr)
print(f'Fullscrape mode: {use_fullscrape}', file=sys.stderr)

# Use heredoc format for proper JSON output in GITHUB_OUTPUT
output_file = os.environ.get('GITHUB_OUTPUT', '')
if output_file:
    with open(output_file, 'a', encoding='utf-8') as fh:
        fh.write('matrix<<MATRIX_JSON\n')
        json.dump(matrix, fh)
        fh.write('\nMATRIX_JSON\n')
        fh.write(f"shard_count={len(matrix)}\n")
        fh.write(f"use_fullscrape={'true' if use_fullscrape else 'false'}\n")
        fh.write(f"selected_sources={','.join(selected)}\n")
else:
    print(f"matrix<<MATRIX_JSON")
    print(json.dumps(matrix))
    print("MATRIX_JSON")
    print(f"shard_count={len(matrix)}")
    print(f"use_fullscrape={'true' if use_fullscrape else 'false'}")
    print(f"selected_sources={','.join(selected)}")
