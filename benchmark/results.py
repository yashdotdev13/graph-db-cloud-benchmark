from dataclasses import dataclass

from benchmark.ingestion import IngestionResult
from benchmark.query import QueryBenchmarkResult


@dataclass(frozen=True)
class BenchmarkMetadata:
    node_count: int
    relationship_count: int
    ingestion_batch_size: int
    query_iterations: int
    query_warmup_iterations: int


@dataclass(frozen=True)
class BenchmarkSummary:
    database: str
    metadata: BenchmarkMetadata
    ingestion: IngestionResult
    queries: tuple[QueryBenchmarkResult, ...]
