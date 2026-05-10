"""Advanced Drug scraper CLI - highly optimized, parallel, checkpoint-capable."""

from __future__ import annotations

import asyncio
import httpx
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler
import yaml

# Import new utilities
from utils.checkpoint import CheckpointManager, CheckpointState
from utils.cache import HTTPCache
from utils.metrics import MetricsCollector, ScrapeMetrics

logger = logging.getLogger(__name__)

# Bangladesh scrapers
from scrapers.bangladesh.medex import MedExScraper
from scrapers.bangladesh.dims import DIMSScraper
from scrapers.bangladesh.dgda import DGDAScraper
from scrapers.bangladesh.bdmedex import BDMedExScraper
from scrapers.bangladesh.bddrugs import BDDrugsScraper
from scrapers.bangladesh.bddrugstore import BDDrugstoreScraper
from scrapers.bangladesh.arogga import AroggaScraper
from scrapers.bangladesh.medeasy import MedEasyScraper
from scrapers.bangladesh.osudpotro import OsudpotroScraper
from scrapers.bangladesh.lazzpharma import LazzPharmaScraper
from scrapers.bangladesh.dghs_shr import DGHSSHRScraper

# International API scrapers
from scrapers.international.openfda import OpenFDAScraper
from scrapers.international.rxnorm import RxNormScraper
from scrapers.international.dailymed import DailyMedScraper
from scrapers.international.pubchem import PubChemScraper
from scrapers.international.chembl import ChEMBLScraper
from scrapers.international.kegg import KEGGScraper
from scrapers.international.ema import EMAScraper

# International scraping scrapers
from scrapers.international.drugs_com import DrugsComScraper
from scrapers.international.rxlist import RxListScraper
from scrapers.international.webmd import WebMDScraper
from scrapers.international.emc import EMCScraper
from scrapers.international.mims import MIMSScraper
from scrapers.international.who_eml import WHOEMLScraper
from scrapers.international.medscape import MedscapeScraper
from scrapers.international.epocrates import EpocratesScraper

# Research scrapers
from scrapers.research.drugbank import DrugBankScraper
from scrapers.research.pharmgkb import PharmGKBScraper
from scrapers.research.clincalc import ClinCalcScraper

# Import original base for backwards compatibility
from scrapers.base import BaseScraper as OldBaseScraper
from scrapers.base_advanced import BaseAdvancedScraper, ScrapeMeta

# Also import change detector and pipeline from original
from utils.change_detector import ChangeDetector
from utils.pipeline import post_process as _post_process

console = Console()

# ---------------------------------------------------------------------------
# Load configuration
# ---------------------------------------------------------------------------

CONFIG: dict = {}

def load_config(config_path: Path = Path("config/default.yaml")):
    global CONFIG
    if config_path.exists():
        with open(config_path) as f:
            CONFIG = yaml.safe_load(f)
        logging.info(f"Loaded configuration from {config_path}")
    else:
        logging.warning(f"Config file not found: {config_path}, using defaults")
        CONFIG = {
            "scrapers": {
                "default_concurrency": 10,
                "request_timeout": 30,
                "scraper_timeout": 900,
                "checkpoint_enabled": True,
                "checkpoint_interval": 100,
                "cache_enabled": True,
                "cache_ttl_seconds": 3600,
            }
        }

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALL_SCRAPERS: dict = {
    # Bangladesh
    "medex": MedExScraper,
    "dims": DIMSScraper,
    "dgda": DGDAScraper,
    "bdmedex": BDMedExScraper,
    "bddrugs": BDDrugsScraper,
    "bddrugstore": BDDrugstoreScraper,
    "arogga": AroggaScraper,
    "medeasy": MedEasyScraper,
    "osudpotro": OsudpotroScraper,
    "lazzpharma": LazzPharmaScraper,
    "dghs_shr": DGHSSHRScraper,
    # International APIs
    "openfda": OpenFDAScraper,
    "rxnorm": RxNormScraper,
    "dailymed": DailyMedScraper,
    "pubchem": PubChemScraper,
    "chembl": ChEMBLScraper,
    "kegg": KEGGScraper,
    "ema": EMAScraper,
    # International scraping
    "drugs_com": DrugsComScraper,
    "rxlist": RxListScraper,
    "webmd": WebMDScraper,
    "emc": EMCScraper,
    "mims": MIMSScraper,
    "who_eml": WHOEMLScraper,
    "medscape": MedscapeScraper,
    "epocrates": EpocratesScraper,
    # Research
    "drugbank": DrugBankScraper,
    "pharmgkb": PharmGKBScraper,
    "clincalc": ClinCalcScraper,
}

BD_SCRAPERS = [
    "medex", "dims", "dgda", "bdmedex", "bddrugs",
    "bddrugstore", "arogga", "medeasy", "osudpotro", "lazzpharma", "dghs_shr",
]
INTL_SCRAPERS = [
    "openfda", "rxnorm", "dailymed", "pubchem", "chembl",
    "kegg", "ema", "drugs_com", "rxlist", "webmd",
    "emc", "mims", "who_eml", "medscape", "epocrates",
]
RESEARCH_SCRAPERS = ["drugbank", "pharmgkb", "clincalc"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


def get_source_config(source_name: str) -> dict:
    """Get per-source configuration from config file."""
    default_cfg = CONFIG.get("scrapers", {})
    source_cfg = CONFIG.get("sources", {}).get(source_name, {})
    return {**default_cfg, **source_cfg}


async def _run_scraper_advanced(
    scraper_cls,
    scraper_name: str,
    data_dir: Path,
    ck_manager: CheckpointManager,
    cache: HTTPCache | None,
    metrics: MetricsCollector,
    concurrency_override: Optional[int] = None,
) -> ScrapeMeta:
    """Run a single scraper with advanced features."""

    source_config = get_source_config(scraper_name)
    scraper_timeout = source_config.get("scraper_timeout", CONFIG.get("scrapers", {}).get("scraper_timeout", 900))
    checkpoint_interval = source_config.get("checkpoint_interval", CONFIG.get("scrapers", {}).get("checkpoint_interval", 100))

    # Instantiate scraper
    scraper = scraper_cls(
        data_dir=data_dir,
        checkpoint_manager=ck_manager,
        cache=cache,
        metrics=metrics,
    )

    # Override parameters from config
    scraper.scraper_timeout = scraper_timeout
    scraper.checkpoint_interval = checkpoint_interval
    if concurrency_override:
        scraper.max_concurrent_requests = concurrency_override
        scraper._limits = httpx.Limits(
            max_connections=concurrency_override,
            max_keepalive_connections=concurrency_override // 2,
        )
    elif "concurrency" in source_config:
        scraper.max_concurrent_requests = source_config["concurrency"]
        scraper._limits = httpx.Limits(
            max_connections=source_config["concurrency"],
            max_keepalive_connections=source_config["concurrency"] // 2,
        )

    try:
        meta = await scraper.run()  # type: ignore[no-any-return]
        return meta  # type: ignore[no-any-return]
    except Exception as e:
        logger.error(f"Scraper {scraper_name} failed: {e}", exc_info=True)
        raise


async def _run_scrapers(
    sources: list[str],
    data_dir: Path,
    concurrency: int = 4,
    resume: bool = True,
    checkpoint_interval: int = 100,
    cache_enabled: bool = True,
) -> None:
    """
    Run multiple scrapers in parallel with full optimization.

    Args:
        sources: List of source names to run
        data_dir: Output directory for scraped data
        concurrency: Max concurrent scrapers (not internal URL concurrency)
        resume: Enable resume from checkpoints
        checkpoint_interval: Save checkpoint every N drugs
        cache_enabled: Enable HTTP response caching
    """

    # Initialize utilities
    ck_manager = CheckpointManager(data_dir)
    cache = HTTPCache(data_dir / ".cache") if cache_enabled else None
    metrics = MetricsCollector(data_dir / "metrics.json")

    # Load previous metrics for comparison
    previous = metrics.load_previous()
    if previous:
        console.print(f"[dim]Previous run: {previous.get('total_drugs', 0)} drugs total[/dim]")

    # Determine which sources to run (filter out already completed)
    sources_to_run = []
    skipped = []

    for src in sources:
        if resume and ck_manager.exists(src):
            ck = ck_manager.load(src)
            if ck and ck.status == "completed":
                skipped.append(src)
                continue
        sources_to_run.append(src)

    if skipped:
        console.print(f"[yellow]Skipped (already complete): {', '.join(skipped)}[/yellow]")

    if not sources_to_run:
        console.print("[green]All sources already completed![/green]")
        return

    console.print(f"[cyan]Running {len(sources_to_run)} sources with max {concurrency} parallel scrapers[/cyan]")

    # Create semaphore to limit concurrent scrapers
    scraper_semaphore = asyncio.Semaphore(concurrency)

    async def run_one(source_name: str):
        async with scraper_semaphore:
            scraper_cls = ALL_SCRAPERS[source_name]
            try:
                meta = await _run_scraper_advanced(
                    scraper_cls=scraper_cls,
                    scraper_name=source_name,
                    data_dir=data_dir,
                    ck_manager=ck_manager,
                    cache=cache,
                    metrics=metrics,
                )
                return source_name, meta, None
            except Exception as e:
                return source_name, None, str(e)

    # Run all scrapers concurrently with bounded parallelism
    tasks = [run_one(s) for s in sources_to_run]
    results = []

    for fut in asyncio.as_completed(tasks):
        source, meta, error = await fut
        if error:
            console.print(f"[red]✗ {source}: {error}[/red]")
            results.append((source, None))
        else:
            console.print(f"[green]✓ {source}: {meta.total_drugs if meta else 0} drugs[/green]")
            results.append((source, meta))

    # Final metrics summary
    console.print("\n")
    table = Table(title="Scrape Summary")
    table.add_column("Source")
    table.add_column("Drugs", justify="right")
    table.add_column("Errors", justify="right")
    table.add_column("Time (s)", justify="right")

    detector = ChangeDetector(data_dir)
    total_drugs = 0
    for source, meta in results:
        if meta:
            changed = detector.has_changed(meta.source) if hasattr(detector, 'has_changed') else "N/A"
            table.add_row(
                source,
                str(meta.total_drugs),
                str(meta.errors),
                f"{meta.duration_seconds:.1f}",
            )
            detector.update_checksum(meta.source)
            total_drugs += meta.total_drugs

    console.print(table)
    console.print(f"[bold]Total drugs collected: {total_drugs}[/bold]")

    # Save final metrics
    metrics.save()

    # Show cache stats
    if cache:
        stats = cache.stats()
        console.print(f"[dim]Cache: {stats['entries']} entries, {stats['size_bytes']/1024/1024:.1f} MB[/dim]")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Verbose logging")
@click.option("--config", type=Path, default=Path("config/default.yaml"),
              help="Configuration file path")
def cli(verbose: bool, config: Path) -> None:
    """Medicrawl Advanced — Comprehensive medicine database scraper."""
    setup_logging(verbose)
    load_config(config)


@cli.command()
@click.argument("sources", nargs=-1)
@click.option("--all", "run_all", is_flag=True, help="Run all scrapers")
@click.option("--fullscrape", is_flag=True, help="Disable source caps")
@click.option("--bd", is_flag=True, help="Run Bangladesh scrapers only")
@click.option("--intl", is_flag=True, help="Run international scrapers only")
@click.option("--research", is_flag=True, help="Run research scrapers only")
@click.option("--data-dir", type=Path, default=Path("data"), help="Output directory")
@click.option("--concurrency", default=4, show_default=True,
              help="Max concurrent scrapers (NOT per-scraper URL concurrency)")
@click.option("--no-resume", is_flag=True, help="Don't resume from checkpoints (start fresh)")
@click.option("--no-cache", is_flag=True, help="Disable HTTP response caching")
@click.option("--timeout", type=int, default=None,
              help="Override scraper timeout in seconds")
def scrape(
    sources: tuple,
    run_all: bool,
    fullscrape: bool,
    bd: bool,
    intl: bool,
    research: bool,
    data_dir: Path,
    concurrency: int,
    no_resume: bool,
    no_cache: bool,
    timeout: Optional[int],
) -> None:
    """Run scrapers for specified sources (advanced version)."""

    # Select sources
    if run_all:
        selected = list(ALL_SCRAPERS.keys())
    elif bd:
        selected = list(BD_SCRAPERS)
    elif intl:
        selected = list(INTL_SCRAPERS)
    elif research:
        selected = list(RESEARCH_SCRAPERS)
    elif sources:
        selected = list(sources)
    else:
        console.print("[red]Specify sources, or use --all, --bd, --intl, --research[/red]")
        sys.exit(1)

    # Validate
    invalid = [s for s in selected if s not in ALL_SCRAPERS]
    if invalid:
        console.print(f"[red]Unknown sources: {', '.join(invalid)}[/red]")
        sys.exit(1)

    data_dir.mkdir(parents=True, exist_ok=True)

    # Run
    asyncio.run(_run_scrapers(
        sources=selected,
        data_dir=data_dir,
        concurrency=concurrency,
        resume=not no_resume,
        cache_enabled=not no_cache,
    ))


@cli.command()
@click.option("--data-dir", type=Path, default=Path("data"))
def resume(data_dir: Path) -> None:
    """Resume all incomplete scrapers."""
    ck_manager = CheckpointManager(data_dir)
    all_names = list(ALL_SCRAPERS.keys())
    resumable = ck_manager.get_resumable_scrapers(all_names)

    if not resumable:
        console.print("[green]No incomplete scrapers to resume.[/green]")
        return

    console.print(f"[yellow]Resuming {len(resumable)} scrapers: {', '.join(resumable)}[/yellow]")
    # Call scrape with these sources
    # (Could call scrape() but need to pass args properly - simplified here)
    asyncio.run(_run_scrapers(resumable, data_dir, concurrency=4))


@cli.command()
@click.option("--data-dir", type=Path, default=Path("data"))
def clear_checkpoints(data_dir: Path) -> None:
    """Clear all checkpoints (allows re-running from start)."""
    ck_manager = CheckpointManager(data_dir)
    count = len(ck_manager.list_all())
    if click.confirm(f"Delete {count} checkpoint(s)?"):
        ck_manager.db_path.unlink(missing_ok=True)
        console.print("[green]Checkpoints cleared.[/green]")


@cli.command()
@click.option("--data-dir", type=Path, default=Path("data"))
def clean_cache(data_dir: Path) -> None:
    """Clear HTTP response cache."""
    cache = HTTPCache(data_dir / ".cache")
    cache.clear()
    console.print("[green]Cache cleared.[/green]")


# Export old API for backwards compatibility
@cli.command(name="scrape-old")
def scrape_old():
    """Legacy scraper (sequential, no advanced features)."""
    console.print("[yellow]Legacy mode - call 'scrape' instead for advanced features[/yellow]")


if __name__ == "__main__":
    cli()
