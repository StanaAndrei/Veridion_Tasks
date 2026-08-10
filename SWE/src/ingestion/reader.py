import pyarrow.parquet as pq
from typing import Iterator, List
import pandas as pd
from .models import DomainTarget


def stream_parquet_domains(file_path: str, batch_size: int = 1000) -> Iterator[List[DomainTarget]]:
    """
    Streams a Parquet file in chunks to maintain a constant memory footprint.
    Yields batches of strict DomainTarget DTOs.
    """
    parquet_file = pq.ParquetFile(file_path)

    for batch in parquet_file.iter_batches(batch_size=batch_size, columns=['root_domain']):
        df = batch.to_pandas()
        valid_domains = df['root_domain'].dropna().unique()

        chunk_targets = []
        for domain in valid_domains:
            if isinstance(domain, bytes):
                domain = domain.decode('utf-8', errors='ignore')

            if domain:
                chunk_targets.append(DomainTarget(root_domain=domain))

        # Yield the whole list of targets for this batch
        if chunk_targets:
            yield chunk_targets