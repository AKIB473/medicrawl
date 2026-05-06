#!/usr/bin/env python3
"""Finalize advanced transformations for all complex scrapers."""

import ast
import pathlib
import sys
import textwrap

SCRAPERS_DIR = pathlib.Path(__file__).parent.parent / "scrapers"

# Files that should be transformed (already using BaseAdvanced but missing concurrent_iter)
TARGET_FILES = [
    # Bangladesh
    "bangladesh/medex.py",
    "bangladesh/bdmedex.py",
    "bangladesh/arogga.py",
    "bangladesh/medeasy.py",
    "bangladesh/lazzpharma.py",
    "bangladesh/dgda.py",
    "bangladesh/osudpotro.py",
    "bangladesh/dims.py",
    "bangladesh/bddrugs.py",
    "bangladesh/bddrugstore.py",
    # International
    "international/epocrates.py",
    "international/medscape.py",
    "international/dailymed.py",
    "international/pubchem.py",
    "international/chembl.py",
    "international/kegg.py",
    "international/who_eml.py",
    "international/rxnorm.py",
    "international/ema.py",
    "international/openfda.py",
    # Research
    "research/pharmgkb.py",
    "research/clincalc.py",
]

def transform_file(path: pathlib.Path):
    source = path.read_text()
    tree = ast.parse(source)

    class Transformer(ast.NodeTransformer):
        def __init__(self):
            self.changed = False

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
            if node.name != 'scrape_all':
                return self.generic_visit(node)

            new_body = []
            i = 0
            while i < len(node.body):
                stmt = node.body[i]
                # Look for pattern: assignment of list (urls) followed by for loop over that variable.
                # We'll handle simple case: For loop directly after assignment (or after small gap)
                if isinstance(stmt, ast.For):
                    # Check if for iterates over a Name
                    if isinstance(stmt.iter, ast.Name):
                        var_name = stmt.iter.id
                        # Look back a few statements to see if var_name is assigned a list from a call like _get_urls, _collect_urls, etc.
                        # Not strictly needed; we just transform this for loop.
                        # Check if body of loop yields Drug via await self._scrape_...
                        new_for = self._transform_for(stmt, var_name)
                        if new_for is not None:
                            new_body.append(new_for)
                            self.changed = True
                            i += 1
                            continue
                new_body.append(stmt)
                i += 1

            node.body = new_body
            return node

        def _transform_for(self, for_node: ast.For, iter_var_name: str) -> ast.stmt | None:
            """
            Replace simple sequential loop with concurrent_iter.
            The loop body should contain a try/except or simple await that yields.
            We'll convert to:
                async for drug in self.concurrent_iter(self.filter_checkpoint(iter_var_name), processor):
                    yield drug
            where processor is an async function defined inline (as a nested FunctionDef) that processes one item.
            However, AST transformation with nested function is messy. Instead, we can inline a lambda-like call but Python doesn't have async lambda.
            So we'll create a new inner async function definition before the loop and then use it.
            But simpler: we can replace the loop with an AsyncFor that calls a helper method on the class? But we'd need to add that helper method to the class, which is more invasive.
            Alternative: Instead of AST transformation for arbitrary complex loops, we can modify the file via string replacement, using markers.

            Given the complexity, for this script we'll target specific known patterns per file using string replace. We'll read file as text and apply regex substitutions.

            Let's revert to a simpler approach: Use file-specific text replacements.

            We'll pass file name to transformer and apply known patterns.

            """
            # Not used: using file-specific text replace strategy.
            return None

    # Since AST-based generic transformation is complex, we'll use per-file text replacements.
    pass

# Instead implement per-file known transformations.
TRANSFORMS = {}

def init_transforms():
    # bdmedex pattern
    def bdmedex_transform(text):
        old = """    async def scrape_all(self) -> AsyncIterator[Drug]:
        # Step 1: Collect drug page URLs from listing pages (static HTML)
        urls = await self._collect_urls()
        logger.info(f"BDMedEx: found {len(urls)} drug page URLs")

        # Step 2: Scrape each drug page via Playwright (JS render required)
        for url in urls:
            try:
                drug = await self._scrape_with_playwright(url)
                if drug:
                    yield drug
                else:
                    # Try bypass fallback
                    drug = await self._scrape_page(url)
                    if drug:
                        yield drug
            except Exception as e:
                logger.warning(f"BDMedEx: error {url}: {e}")
            await asyncio.sleep(self.rate_limit)"""
        new = """    async def scrape_all(self) -> AsyncIterator[Drug]:
        # Step 1: Collect drug page URLs from listing pages (static HTML)
        urls = await self._collect_urls()
        logger.info(f"BDMedEx: found {len(urls)} drug page URLs")

        # Filter already completed URLs via checkpoint
        urls = self.filter_checkpoint(urls)

        async def _process(url: str) -> Drug | None:
            try:
                drug = await self._scrape_with_playwright(url)
                if drug:
                    return drug
                drug = await self._scrape_page(url)
                return drug
            except Exception as e:
                logger.warning(f"BDMedEx: error {url}: {e}")
                return None

        async for drug in self.concurrent_iter(urls, _process):
            if drug:
                yield drug"""
        return text.replace(old, new)
    TRANSFORMS["bangladesh/bdmedex.py"] = bdmedex_transform

    # epocrates
    def epocrates_transform(text):
        # This pattern includes multi-part before loop, then for item in items...
        # We'll replace the for-loop block.
        old = """        emitted = 0
        for item in items:
            if self.max_drugs and emitted >= self.max_drugs:
                break

            drug_id = item.get("id")
            if drug_id is None:
                continue

            try:
                card = await self._safe_get_json(CARD_URL, params={"drugId": drug_id})
            except Exception as e:
                logger.warning(f"Epocrates: card fetch failed for {drug_id}: {e}")
                card = {}

            brands = await self._safe_get_json_list(
                BRANDS_URL,
                params={"drugId": drug_id, "includeParent": "true"},
            )

            drug = self._build_drug(item, card, sections, brands)
            if drug:
                emitted += 1
                yield drug"""
        new = """        items = items[:self.max_drugs] if self.max_drugs else items

        async def _process(item) -> Drug | None:
            drug_id = item.get("id")
            if drug_id is None:
                return None
            # Checkpoint: Epocrates builds drug from ID, compute expected source_url
            expected_url = f"https://www.epocrates.com/drug/{drug_id}"
            if self.checkpoint_manager and self.checkpoint_manager.is_url_completed(self.name, expected_url):
                return None
            try:
                card = await self._safe_get_json(CARD_URL, params={"drugId": drug_id})
            except Exception as e:
                logger.warning(f"Epocrates: card fetch failed for {drug_id}: {e}")
                card = {}
            brands = await self._safe_get_json_list(
                BRANDS_URL,
                params={"drugId": drug_id, "includeParent": "true"},
            )
            drug = self._build_drug(item, card, sections, brands)
            return drug

        emitted = 0
        async for drug in self.concurrent_iter(items, _process):
            if drug:
                emitted += 1
                yield drug"""
        return text.replace(old, new)
    TRANSFORMS["international/epocrates.py"] = epocrates_transform

    # medscape
    def medscape_transform(text):
        old = """        emitted = 0
        for url in sorted_urls:
            if self.max_drugs and emitted >= self.max_drugs:
                break
            try:
                drug = await self._scrape_drug_page(url)
                if not drug:
                    continue
                emitted += 1
                yield drug
            except Exception as e:
                logger.warning(f"Medscape: failed {url}: {e}")"""
        new = """        sorted_urls = self.filter_checkpoint(sorted_urls)
        emitted = 0

        async def _process(url: str) -> Drug | None:
            try:
                drug = await self._scrape_drug_page(url)
                return drug
            except Exception as e:
                logger.warning(f"Medscape: failed {url}: {e}")
                return None

        async for drug in self.concurrent_iter(sorted_urls, _process):
            if drug:
                emitted += 1
                if self.max_drugs and emitted >= self.max_drugs:
                    break
                yield drug"""
        return text.replace(old, new)
    TRANSFORMS["international/medscape.py"] = medscape_transform

    # bdmedex, medex, etc. will add similarly.

def process_file(filepath: pathlib.Path):
    text = filepath.read_text()
    filename = filepath.name
    parent = filepath.parent.name
    key = f"{parent}/{filename}"
    if key not in TRANSFORMS:
        print(f"  No transform for {key}")
        return False
    new_text = TRANSFORMS[key](text)
    if new_text != text:
        filepath.write_text(new_text)
        print(f"  TRANSFORMED {key}")
        return True
    else:
        print(f"  (no change) {key}")
        return False

def main():
    init_transforms()
    for rel in TRANSFORMS.keys():
        p = SCRAPERS_DIR / rel
        if p.exists():
            process_file(p)
        else:
            print(f"Missing: {p}")

if __name__ == '__main__':
    main()
