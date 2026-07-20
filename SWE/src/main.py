import click
import asyncio
from ingestion.reader import stream_parquet_domains
from scraper.engine import fetch_tier_1


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
@click.option('--batch-size', '-b', default=50, help='Rows per chunk')
def run(input_file: str, batch_size: int):
    """Run the ingestion and scraper pipeline."""
    click.echo(f"Ingesting from: {input_file}")
    domain_stream = stream_parquet_domains(input_file, batch_size=batch_size)

    for chunk_idx, target_chunk in enumerate(domain_stream):
        # target_chunk is already a list now!
        click.echo(f"Processing chunk {chunk_idx + 1} ({len(target_chunk)} domains)...")

        payloads = asyncio.run(process_batch(target_chunk))

        for payload in payloads:
            if payload.error:
                click.echo(f"  [FAILED] {payload.url}: {payload.error}")
            else:
                click.echo(
                    f"  [SUCCESS] {payload.url} (Status: {payload.status_code}, HTML length: {len(payload.html)})")

        break  # Safety break for testing


cli.add_command(run)

if __name__ == '__main__':
    cli()