from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from databases.base import GraphDatabaseAdapter


@dataclass(frozen=True)
class IngestionResult:
    database: str
    node_count: int
    relationship_count: int
    elapsed_seconds: float

    @property
    def nodes_per_second(self) -> float:
        return self.node_count / self.elapsed_seconds

    @property
    def relationships_per_second(self) -> float:
        return self.relationship_count / self.elapsed_seconds


def run_ingestion(
    adapter: GraphDatabaseAdapter,
    nodes_path: Path,
    relationships_path: Path,
    batch_size: int = 1000,
) -> IngestionResult:
    """
    Load the complete benchmark dataset and measure ingestion time.

    The timer covers node and relationship loading only.
    Database cleanup and verification are intentionally excluded.
    """

    adapter.clear()

    start = perf_counter()

    node_count = adapter.load_nodes(
        nodes_path,
        batch_size=batch_size,
    )

    relationship_count = adapter.load_relationships(
        relationships_path,
        batch_size=batch_size,
    )

    elapsed = perf_counter() - start

    return IngestionResult(
        database=adapter.name,
        node_count=node_count,
        relationship_count=relationship_count,
        elapsed_seconds=elapsed,
    )