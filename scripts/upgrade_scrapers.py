#!/usr/bin/env python3
"""Upgrade all scrapers to advanced features (concurrency, checkpoint, etc)."""

import ast
import asyncio
import pathlib
import re
import sys
from textwrap import indent

SCRAPERS_DIR = pathlib.Path(__file__).parent.parent / "scrapers"
BASE_ADVANCED_IMPORT = "from scrapers.base_advanced import BaseAdvancedScraper, BaseAdvancedAPIScraper"

# Map of scraper file to processing details: (urls_var, processor_method, processor_args_count, extra_setup)
# Will be auto-detected, fallback manual

def detect_method_info(source):
    """Analyze scrape_all AST to extract urls var and processor method name."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == 'scrape_all':
            # Find first assignment of urls-like variable that is awaited: urls = await self._get...
            urls_var = None
            assign = None
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    # target should be a Name
                    if isinstance(stmt.targets[0], ast.Name):
                        target = stmt.targets[0].id
                        value = stmt.value
                        if isinstance(value, ast.Await) and isinstance(value.func, ast.Attribute):
                            if isinstance(value.func.value, ast.Name) and value.func.value.id == 'self':
                                # self._get...
                                urls_var = target
                                assign = stmt
                                break
            if not urls_var:
                # maybe using other strategies like pagination collecting into list then returning
                # We'll handle special cases by name
                return None

            # Find for loop iterating over urls_var
            for_loop = None
            for stmt in node.body:
                if isinstance(stmt, ast.For) and isinstance(stmt.iter, ast.Name) and stmt.iter.id == urls_var:
                    for_loop = stmt
                    break
            if not for_loop:
                return None

            # Inside for loop, find assignment to drug variable that calls a method on self
            # The body of for loop may have try/except; look inside
            processor_method = None
            arg_count = 0
            # Walk through body of for
            for inner in ast.walk(for_loop):
                if isinstance(inner, ast.Assign):
                    # Check if assigns to a variable (likely 'drug')
                    targets = [t.id for t in inner.targets if isinstance(t, ast.Name)]
                    if 'drug' not in targets:
                        continue
                    # Check if value is await(self.method(...))
                    val = inner.value
                    if isinstance(val, ast.Await) and isinstance(val.func, ast.Attribute):
                        if isinstance(val.func.value, ast.Name) and val.func.value.id == 'self':
                            processor_method = val.func.attr
                            arg_count = len(val.args)
                            # Could break
            if processor_method:
                return {
                    'urls_var': urls_var,
                    'get_assignment': assign,
                    'logger_info_before': None,  # placeholder
                    'processor': processor_method,
                    'arg_count': arg_count,
                }
    return None

def build_concurrent_body(info):
    """Given info dict, build new scrape_all body as string."""
    lines = []
    # Preserve any statements before URL collection? We'll just reconstruct.
    # Usually starts with 'urls = await self._get_xxx()'
    # We'll need to unparse get_assignment
    get_assign_str = ast.unparse(info['get_assignment'])
    lines.append(get_assign_str)
    # Usually there is logger.info after that. We could check if next stmt is logger.info; but simpler: add logger.info pattern using info['urls_var'] variable from original? Actually original had logger.info using that count. We can compute count after URL fetch and log.
    lines.append(f"logger.info(f\"{{self.name}}: found {{len(urls)}} drug URLs\")")
    lines.append("")
    lines.append("# Filter already processed URLs via checkpoint resume")
    lines.append("if self.checkpoint_manager:")
    lines.append("    completed = self.checkpoint_manager.get_completed_urls(self.name)")
    lines.append("    urls = [u for u in urls if u not in completed]")
    lines.append("    logger.info(f\"{self.name}: {len(urls)} URLs remaining after checkpoint filter\")")
    lines.append("")
    lines.append("async for drug in self.concurrent_iter(urls, self._process):")
    lines.append("    yield drug")
    # Where _process is the internal method; but method name may not be _process. We need to call appropriate processor.
    # But concurrent_iter expects a function that takes one argument. In our case processor method may need additional args beyond url (like DailyMed). We'll need lambda.
    # We'll treat special cases separately.
    return "\n".join(lines)

def transform_simple_scraper(source):
    """Apply transformation to a scraper source code."""
    tree = ast.parse(source)
    imports_changed = False
    class_def_changed = False
    method_replaced = False

    # 1. Fix imports
    old_imports = [
        "from scrapers.base import BaseScrapingScraper",
        "from scrapers.base import BaseAPIScraper",
    ]
    new_imports = {
        "from scrapers.base import BaseScrapingScraper": "from scrapers.base_advanced import BaseAdvancedScraper",
        "from scrapers.base import BaseAPIScraper": "from scrapers.base_advanced import BaseAdvancedAPIScraper",
    }
    for old_imp, new_imp in new_imports.items():
        if old_imp in source:
            source = source.replace(old_imp, new_imp, 1)
            imports_changed = True
            break

    # 2. Change base class in class definition
    # Find lines like 'class XScraper(BaseScrapingScraper):' and replace with BaseAdvancedScraper
    # Also for BaseAPIScraper → BaseAdvancedAPIScraper
    # Use regex
    import re
    old_base_patterns = [
        (r'class\s+(\w+)\(BaseScrapingScraper\):', 'BaseAdvancedScraper'),
        (r'class\s+(\w+)\(BaseAPIScraper\):', 'BaseAdvancedAPIScraper'),
    ]
    for pattern, new_base in old_base_patterns:
        if re.search(pattern, source):
            source = re.sub(pattern, lambda m: f"class {m.group(1)}({new_base}):", source)
            class_def_changed = True
            break

    # 3. Replace scrape_all body
    # Try to detect method info
    info = detect_method_info(source)
    if not info:
        print(f"  WARNING: Could not detect scrape_all pattern; skipping body replacement")
        return source

    # Build new body using simple mapping (assumes single-arg processor)
    # But we need to respect any special processing. Determine if processor needs extra args based on known file?
    # This part is tricky; maybe make script only handle simple single-arg cases.
    # For special files, skip and handle manually.
    print(f"  Detected: urls_var={info['urls_var']}, processor={info['processor']}, args={info['arg_count']}")
    # Simpler: we can replace loop entirely with a concurrent call using that processor.
    # Write new function definition block.
    # Not using AST rewrite due to complexity; just regex: replace from the line `async def scrape_all` until next blank line after yield? Hard.

    return source

def main():
    py_files = list(SCRAPERS_DIR.rglob("*.py"))
    # Exclude base files
    py_files = [p for p in py_files if p.name not in ('base.py','base_advanced.py','__init__.py')]
    print(f"Found {len(py_files)} scraper files")
    for f in py_files:
        src = f.read_text()
        new_src = transform_simple_scraper(src)
        if new_src != src:
            f.write_text(new_src)
            print(f"[UPDATED] {f.name}")
        else:
            print(f"[SKIP]    {f.name} (no changes)")

if __name__ == '__main__':
    main()
