from benchmark.config import BenchmarkConfig
from benchmark.ingestion import run_ingestion
from benchmark.query import run_query_benchmark
from benchmark.results import BenchmarkMetadata, BenchmarkSummary
from benchmark.workload import BenchmarkWorkload
from databases.base import GraphDatabaseAdapter


EXPECTED_NODES = 36_692
EXPECTED_RELATIONSHIPS = 183_831


def run_benchmark(
    adapter: GraphDatabaseAdapter,
    config: BenchmarkConfig,
    workloads: tuple[BenchmarkWorkload, ...],
) -> BenchmarkSummary:
    adapter.connect()

    try:
        ingestion = run_ingestion(
            adapter,
            config.nodes_path,
            config.relationships_path,
            batch_size=config.ingestion_batch_size,
        )

        if ingestion.node_count != EXPECTED_NODES:
            raise RuntimeError(
                f"Unexpected node count: {ingestion.node_count}"
            )

        if ingestion.relationship_count != EXPECTED_RELATIONSHIPS:
            raise RuntimeError(
                f"Unexpected relationship count: "
                f"{ingestion.relationship_count}"
            )

        metadata = BenchmarkMetadata(
            node_count=ingestion.node_count,
            relationship_count=ingestion.relationship_count,
            ingestion_batch_size=config.ingestion_batch_size,
            query_iterations=config.query_iterations,
            query_warmup_iterations=config.query_warmup_iterations,
        )

        query_results = tuple(
            run_query_benchmark(
                adapter,
                workload,
                iterations=config.query_iterations,
                warmup_iterations=config.query_warmup_iterations,
            )
            for workload in workloads
        )

        return BenchmarkSummary(
            database=adapter.name,
            metadata=metadata,
            ingestion=ingestion,
            queries=query_results,
        )

    finally:
        adapter.clear()
        adapter.close()
