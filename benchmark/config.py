from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BenchmarkConfig:
    nodes_path: Path
    relationships_path: Path

    expected_nodes: int = 36_692
    expected_relationships: int = 183_831

    ingestion_batch_size: int = 1000

    query_iterations: int = 100
    query_warmup_iterations: int = 10

    query_seed: int = 42