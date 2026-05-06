#!/usr/bin/env python3
"""Transform all scrapers to advanced base and simple concurrent loops."""

import ast
import pathlib
import sys

SCRAPERS_DIR = pathlib.Path(__file__).parent.parent / "scrapers"

# Files that need manual handling (complex patterns)
MANUAL_OVERRIDES = {
    "dailymed.py", "medex.py", "dgda.py", "osudpotro.py", "dghs_shr.py",
    "pubchem.py", "chembl.py", "kegg.py", "who_eml.py", "rxnorm.py",
    "ema.py", "openfda.py", "pharmgkb.py", "clincalc.py", "arogga.py",
    "medeasy.py", "lazzpharma.py", "dims.py", "bddrugs.py", "bddrugstore.py",
    # Note: some may still match simple pattern; we include them here to be safe.
}

def transform_imports_and_bases(source: str) -> str:
    source = source.replace(
        "from scrapers.base import BaseScrapingScraper",
        "from scrapers.base_advanced import BaseAdvancedScraper"
    )
    source = source.replace(
        "from scrapers.base import BaseAPIScraper",
        "from scrapers.base_advanced import BaseAdvancedAPIScraper"
    )
    import re
    source = re.sub(
        r'class\s+(\w+)\(BaseScrapingScraper\):',
        r'class \1(BaseAdvancedScraper):',
        source
    )
    source = re.sub(
        r'class\s+(\w+)\(BaseAPIScraper\):',
        r'class \1(BaseAdvancedAPIScraper):',
        source
    )
    return source


class SimpleLoopTransformer(ast.NodeTransformer):
    """Replace simple for...await self.method(item) loops with concurrent_iter."""

    def __init__(self):
        self.changed = False

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        if node.name != 'scrape_all':
            return self.generic_visit(node)

        # We'll iterate over body and replace any For nodes that match pattern
        new_body = []
        for stmt in node.body:
            if isinstance(stmt, ast.For):
                new_for = self._try_transform_for(stmt)
                if new_for is not None:
                    new_body.append(new_for)
                    self.changed = True
                    continue  # skip original
            new_body.append(stmt)
        node.body = new_body
        return node

    def _try_transform_for(self, for_node: ast.For) -> ast.stmt | None:
        # Check iterator is simple Name
        if not isinstance(for_node.iter, ast.Name):
            return None
        iter_name = for_node.iter.id

        # Check body pattern: Try with single Assign that does await self.method(loop_var)
        if len(for_node.body) != 1:
            return None
        try_node = for_node.body[0]
        if not isinstance(try_node, ast.Try):
            return None
        # In try body, expect Assign, maybe then If that yields drug. Simplify: find Assign to 'drug' with await self.method(loop_var)
        processor_attr = None
        drug_assign = None
        for inner in try_node.body:
            if isinstance(inner, ast.Assign):
                # Look for target 'drug'
                if any(isinstance(t, ast.Name) and t.id == 'drug' for t in inner.targets):
                    # Check value: Await(Call(self.method, args=[loop_var]))
                    val = inner.value
                    if isinstance(val, ast.Await):
                        call = val.value
                        if isinstance(call, ast.Call):
                            func = call.func
                            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == 'self':
                                if len(call.args) == 1:
                                    arg = call.args[0]
                                    if isinstance(arg, ast.Name) and arg.id == for_node.target.id:
                                        processor_attr = func.attr
                                        drug_assign = inner
                                        break
        if processor_attr is None:
            return None

        # Build new AsyncFor
        # Iter expression: Call self.concurrent_iter with args:
        #   arg1: Call self.filter_checkpoint(original iterable)
        #   arg2: Attribute self.processor
        filter_call = ast.Call(
            func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='filter_checkpoint', ctx=ast.Load()),
            args=[ast.Name(id=iter_name, ctx=ast.Load())],
            keywords=[]
        )
        processor_attr_node = ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr=processor_attr, ctx=ast.Load())
        concurrent_call = ast.Call(
            func=ast.Attribute(value=ast.Name(id='self', ctx=ast.Load()), attr='concurrent_iter', ctx=ast.Load()),
            args=[filter_call, processor_attr_node],
            keywords=[]
        )

        target = for_node.target  # typically Name('drug')
        # Build body: Yield drug, then checkpoint add_url if checkpoint_manager exists.
        yield_stmt = ast.Expr(value=ast.Yield(value=ast.Name(id=target.id, ctx=ast.Load())))
        checkpoint_if = ast.If(
            test=ast.Compare(
                left=ast.Attribute(value=ast.Name(id='self'), attr='checkpoint_manager', ctx=ast.Load()),
                ops=[ast.IsNot()],
                comparators=[ast.Constant(value=None)]
            ),
            body=[
                ast.Expr(value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(value=ast.Name(id='self'), attr='checkpoint_manager', ctx=ast.Load()),
                        attr='add_url', ctx=ast.Load()
                    ),
                    args=[
                        ast.Attribute(value=ast.Name(id='self'), attr='name', ctx=ast.Load()),
                        ast.Attribute(value=ast.Name(id=target.id), attr='source_url', ctx=ast.Load())
                    ],
                    keywords=[]
                ))
            ],
            orelse=[]
        )
        new_async_for = ast.AsyncFor(
            target=target,
            iter=concurrent_call,
            body=[yield_stmt, checkpoint_if],
            orelse=[]
        )
        # Copy location for readability (optional)
        return new_async_for


def process_file(path: pathlib.Path):
    source = path.read_text()
    changed = False

    # Step 1: import and base class replacement via string replace
    new_source = transform_imports_and_bases(source)
    if new_source != source:
        changed = True
        source = new_source

    filename = path.name
    if filename in MANUAL_OVERRIDES:
        print(f"  SKIP manual: {filename}")
        path.write_text(source)
        return

    # Step 2: AST transformation for simple loops
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  PARSE ERROR {filename}: {e}")
        path.write_text(source)
        return

    transformer = SimpleLoopTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    if transformer.changed:
        new_source = ast.unparse(new_tree)
        path.write_text(new_source)
        print(f"  TRANSFORMED: {filename}")
    else:
        path.write_text(source)
        print(f"  (no loop change) {filename}")


def main():
    py_files = list(SCRAPERS_DIR.rglob("*.py"))
    py_files = [p for p in py_files if p.name not in ('base.py','base_advanced.py','__init__.py')]
    print(f"Processing {len(py_files)} scraper files...")
    for f in py_files:
        process_file(f)

if __name__ == '__main__':
    main()
