import click
import asyncio
from ingestion.reader import stream_parquet_domains
from scraper.engine import fetch_tier_1
from analysis.orchestrator import RulesEngine

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
    pass


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True), required=True)
@click.option('--batch-size', '-b', default=50)
def run(input_file: str, batch_size: int):
    click.echo(f"Ingesting from: {input_file}")
    engine = RulesEngine()
    domain_stream = stream_parquet_domains(input_file, batch_size=batch_size)
    for chunk_idx, target_chunk in enumerate(domain_stream):
        click.echo(f"\nProcessing chunk {chunk_idx + 1} ({len(target_chunk)} domains)...")
        payloads = asyncio.run(process_batch(target_chunk))

        for payload in payloads:
            if payload.error:
                click.echo(f"  [FAILED] {payload.url}")
                continue

            findings = engine.analyze(payload)

            if findings:
                click.echo(f"  [FOUND] {payload.url}")
                for finding in findings:
                    click.echo(f"    -> {finding.technology_name} ({finding.confidence * 100:.0f}% confidence)")
                    for proof in finding.proofs:
                        click.echo(f"       * {proof}")
            else:
                click.echo(f"  [CLEAN] {payload.url} (No known tech detected)")

cli.add_command(run)

if __name__ == '__main__':
    cli()