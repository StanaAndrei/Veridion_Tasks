import click
import asyncio
from ingestion.reader import stream_parquet_domains
from scraper.engine import fetch_tier_1
from analysis.orchestrator import RulesEngine
from exporting.exporter import JSONExporter


async def process_batch(domains, concurrency_limit=50):
    """Processes a chunk of domains concurrently."""
    semaphore = asyncio.Semaphore(concurrency_limit)

    async def sem_fetch(domain):
        async with semaphore:
            return await fetch_tier_1(domain)

    tasks = [sem_fetch(domain) for domain in domains]
    return await asyncio.gather(*tasks)


@click.group()
def cli():
    """Website Technologies Scraper Pipeline"""
    pass


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True), required=True)
@click.option('--output-file', '-o', default='data/results.json', help='Path for final JSON output')
@click.option('--batch-size', '-b', default=50)
def run(input_file: str, output_file: str, batch_size: int):
    """Run the ingestion, scraping, and export pipeline."""
    click.echo(f"Ingesting from: {input_file}")

    engine = RulesEngine()
    exporter = JSONExporter(output_path=output_file)
    domain_stream = stream_parquet_domains(input_file, batch_size=batch_size)

    try:
        for chunk_idx, target_chunk in enumerate(domain_stream):
            click.echo(f"Processing chunk {chunk_idx + 1} ({len(target_chunk)} domains)...")

            # Scrape
            payloads = asyncio.run(process_batch(target_chunk))

            # Analyze and Export
            for payload in payloads:
                if payload.error:
                    click.echo(f"  [FAILED] {payload.url} - {payload.error}")
                    continue

                findings = engine.analyze(payload)
                exporter.append_result(domain_url=payload.url, findings=findings)

                if findings:
                    click.echo(f"  [FOUND] {payload.url} ({len(findings)} technologies)")
                else:
                    click.echo(f"  [CLEAN] {payload.url}")
    finally:
        exporter.finalize()


# Crucial: This wires the 'run' command to the CLI group!
cli.add_command(run)

if __name__ == '__main__':
    cli()